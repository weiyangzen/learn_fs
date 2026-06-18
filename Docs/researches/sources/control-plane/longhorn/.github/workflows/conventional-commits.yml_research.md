## sources/control-plane/longhorn/.github/workflows/conventional-commits.yml

### Purpose
This workflow enforces conventional commit messages and semantic PR titles.

### Important APIs, Types, And Functions
It runs on PR open/edit/synchronize/reopen with read permissions. It checks out full history, runs `wagoid/commitlint-github-action`, and runs `amannn/action-semantic-pull-request` allowing types such as `feat`, `fix`, `docs`, `test`, `chore`, `ci`, `revert`, and `BREAKING`.

### Control Flow
Both lint steps read PR commits/title and fail the job if format rules are violated.

### State, Persistence, And Dependencies
It writes no state. Dependencies are pinned actions and the default commitlint configuration provided by the action.

### Integration Points
It supports release note and changelog hygiene by normalizing commit and PR titles.

### Risks
Full history checkout can be slower. Allowed type list must stay aligned with repository conventions. The uppercase `BREAKING` type may or may not match semantic-release expectations.

### Test Signals
PRs with invalid titles or commit messages should fail; valid conventional commits should pass.
