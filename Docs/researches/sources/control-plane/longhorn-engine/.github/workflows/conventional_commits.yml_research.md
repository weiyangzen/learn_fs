<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/conventional_commits.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/conventional_commits.yml

### Purpose
This workflow enforces conventional commit messages and semantic pull request titles.

### Important APIs, Types, And Functions
It triggers on PR opened, edited, synchronize, and reopened events. It grants read permissions, checks out PR commits at the head SHA with full history, runs `wagoid/commitlint-github-action`, and runs `amannn/action-semantic-pull-request` with allowed types.

### Control Flow
Each relevant PR event checks out the PR head, validates commit messages, then validates the PR title/type using `GITHUB_TOKEN`.

### State, Persistence, And Dependencies
No repo state is changed. Dependencies include the two pinned third-party actions and GitHub pull-request metadata.

### Integration Points
This workflow supports release-note/changelog hygiene for Longhorn Engine and complements automated backport/merge workflows.

### Risks
Full-history checkout can be slower. Allowed type `BREAKING` is unusual as a semantic type and may reflect local convention; if not, it can permit odd PR titles. Fork PR token permissions must satisfy the semantic PR action.

### Test Signals
Signals include failing invalid commit messages, failing invalid PR titles, accepting allowed types, and handling synchronize/reopened events.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/conventional_commits.yml -->
