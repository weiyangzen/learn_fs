<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/codespell.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/codespell.yml

### Purpose
This workflow runs codespell on pull requests to Longhorn Engine.

### Important APIs, Types, And Functions
It triggers on PRs to `master`, `main`, or `v*.*.*`, checks out with pinned `actions/checkout`, and runs pinned `codespell-project/actions-codespell` with filename checking and a broad skip list.

### Control Flow
On matching PRs, the job checks out one commit and executes codespell against the repository while excluding generated/vendor/script/integration and manifest-like paths.

### State, Persistence, And Dependencies
No repository state is changed. Dependencies are GitHub Actions, codespell action, and the skip pattern.

### Integration Points
This is a PR quality gate complementary to build and commit-lint workflows.

### Risks
The skip list excludes many YAML, script, integration, and vendor paths, so spelling issues there are not caught. `fetch-depth: 1` is enough for codespell but not history-aware checks.

### Test Signals
Signals include action success on clean PRs, failure on intentional spelling mistakes in checked paths, and no false positives in skipped generated/vendor areas.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/codespell.yml -->
