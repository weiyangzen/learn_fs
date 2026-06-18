<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/backport-pr.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/backport-pr.yml

### Purpose
This GitHub Actions workflow delegates backport PR issue-linking logic to a reusable workflow in the central Longhorn repository.

### Important APIs, Types, And Functions
Workflow `Link-Backport-PR-Issue` runs on opened pull requests targeting `master` or `v*` branches. The single job uses `longhorn/longhorn/.github/workflows/backport-pr.yml` pinned to commit `666fcb2f...`.

### Control Flow
When a matching PR opens, GitHub Actions invokes the reusable workflow with inherited default context.

### State, Persistence, And Dependencies
State changes are controlled by the reusable workflow, likely GitHub PR/issue links or comments. Dependencies include GitHub Actions reusable workflow support and the pinned Longhorn commit.

### Integration Points
This keeps Longhorn Engine backport behavior aligned with central Longhorn automation.

### Risks
The pinned commit can become stale relative to current central workflow fixes. No explicit permissions are declared locally, so behavior depends on defaults and called workflow requirements.

### Test Signals
Signals include workflow dispatch on opened PRs, called workflow success, and expected issue/PR linkage on master and release branches.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/backport-pr.yml -->
