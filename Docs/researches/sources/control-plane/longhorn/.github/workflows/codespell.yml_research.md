## sources/control-plane/longhorn/.github/workflows/codespell.yml

### Purpose
`codespell.yml` runs spelling checks on pull requests.

### Important APIs, Types, And Functions
It triggers on PRs to `master` and `v*.*.*` branches, checks out the repository, and runs `codespell-project/actions-codespell` with filename checking and skip patterns for YAML, scripts, vendor, maintainers, license, and Go module files.

### Control Flow
The action scans changed repository content according to codespell behavior and fails the job on detected spelling errors.

### State, Persistence, And Dependencies
It writes no repo state. Dependencies are the pinned checkout and codespell actions.

### Integration Points
The workflow acts as a PR management quality gate.

### Risks
The skip pattern excludes all YAML and scripts, leaving many user-facing texts unverified. Branch pattern `v*.*.*` may not match `vX.Y.x` maintenance branches.

### Test Signals
Introduce a known typo in a non-skipped file on a test PR and confirm the job fails.
