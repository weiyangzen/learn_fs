## sources/control-plane/longhorn/.github/workflows/pr-review-reminder.py

### Purpose
`pr-review-reminder.py` gathers open PRs across Longhorn repositories and sends a Slack reminder listing requested reviewers.

### Important APIs, Types, And Functions
`REPOS` lists Longhorn repositories. `pr_review_reminder` runs `gh pr list` for each repo requesting number, title, author, review requests, and labels. `flatten_issues` formats Slack blocks in chunks of five PRs. `send_slack_notification` reads `SLACK_WEBHOOK_URL` and optional GitHub-to-Slack `USER_MAPPING`, then posts block-kit JSON with `requests`.

### Control Flow
The script skips bot-authored PRs and PRs labeled `pending`, collects reviewer logins, maps them to Slack mentions when possible, and sends one payload containing per-repo sections.

### State, Persistence, And Dependencies
It persists nothing. Dependencies are authenticated GitHub CLI, `requests`, Slack incoming webhook, and environment secrets.

### Integration Points
`pr-review-reminder.yml` schedules and runs the script after authenticating `gh`.

### Risks
A single Slack post can fail if block count or payload size grows too large, though chunks of five reduce section size. Repos with gh errors are skipped, which can hide missing reminders. The script prints payloads, potentially exposing PR metadata in logs.

### Test Signals
Mock `gh pr list` output and Slack responses to verify skip logic, reviewer mapping, chunking, and error handling.
