import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI

#print("🔐 OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

# Load secrets from .env

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

print("🧪 DEBUG: TELEGRAM_TOKEN =", TELEGRAM_TOKEN)
print("🧪 DEBUG: OPENAI_API_KEY =", OPENAI_API_KEY)
print("🧪 DEBUG: ASSISTANT_ID =", ASSISTANT_ID)


openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    print(f"🔵 User: {user_input}")

    try:
        # OpenAI Assistant logic
        thread = openai_client.beta.threads.create()
        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Simulate "typing..." while waiting
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        while run.status not in ["completed", "failed", "cancelled"]:
            time.sleep(1)
            run = openai_client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)

        if run.status != "completed":
            raise Exception("Run failed.")

        messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value
        await update.message.reply_text(answer)

    except Exception as e:
        print("❌ Error:", e)
        await update.message.reply_text("Sorry, something went wrong.")

# Set up the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()
