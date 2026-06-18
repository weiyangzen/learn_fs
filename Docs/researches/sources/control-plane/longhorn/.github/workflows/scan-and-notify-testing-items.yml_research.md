## sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.yml

### Purpose
This workflow schedules and runs the QA testing-item Slack scanner.

### Important APIs, Types, And Functions
It triggers every Sunday at 12:00 UTC and on manual dispatch with optional org/repo/project inputs. It creates a GitHub App token, checks out the repository, sets up Python, installs `requests`, resolves input defaults from environment variables, and runs `scan-and-notify-testing-items.py`.

### Control Flow
Manual inputs override default `longhorn`, `longhorn`, and `Longhorn Sprint` values. The script receives GitHub token, Slack webhook, and user mapping through environment.

### State, Persistence, And Dependencies
It writes no repo state. It depends on app secrets, Slack secrets, setup-python, checkout, and the Python script.

### Integration Points
It is the operational wrapper for `.github/workflows/scan-and-notify-testing-items.py`.

### Risks
The app token requests only contents/issues read permissions; Projects v2 access must be available through the app. Manual input expressions inside shell conditionals must remain valid for scheduled events.

### Test Signals
Manual dispatch with a test project should produce expected Slack output or no-op logs when no testing items exist.
