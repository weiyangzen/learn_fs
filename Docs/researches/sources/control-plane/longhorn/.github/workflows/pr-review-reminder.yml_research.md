## sources/control-plane/longhorn/.github/workflows/pr-review-reminder.yml

### Purpose
This workflow schedules and runs the PR review reminder Slack notification.

### Important APIs, Types, And Functions
It triggers manually and every Monday at 02:00 UTC, sets up Python 3, installs `requests`, creates a GitHub App token with read permissions, authenticates GitHub CLI, checks out the repository, and runs `.github/workflows/pr-review-reminder.py` with Slack and user-mapping secrets.

### Control Flow
The workflow prepares dependencies and credentials before invoking the Python script.

### State, Persistence, And Dependencies
It writes no repository state. It depends on app secrets, Slack webhook secret, user mapping secret, GitHub CLI availability, and pinned actions.

### Integration Points
It is the scheduler and runtime wrapper for `pr-review-reminder.py`.

### Risks
If `gh auth login` fails, the script cannot list PRs. Secret formatting for `USER_MAPPING` must be valid JSON. Schedule comment says GMT+8 and cron matches Monday 10:00 China time.

### Test Signals
Manual dispatch should post a Slack reminder or clearly fail on dependency/secret issues.
