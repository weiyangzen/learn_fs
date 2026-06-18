<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/stale.yaml -->
## sources/control-plane/longhorn-engine/.github/workflows/stale.yaml

### Purpose
This workflow delegates stale issue/PR handling to the central Longhorn reusable workflow.

### Important APIs, Types, And Functions
It runs manually or on cron `30 1 * * *`. The job calls `longhorn/longhorn/.github/workflows/stale.yaml` pinned to commit `efbad602...`.

### Control Flow
At the scheduled time or manual dispatch, GitHub Actions invokes the reusable stale workflow.

### State, Persistence, And Dependencies
State changes are produced by the called workflow, likely comments, labels, or closures on stale issues/PRs. Dependencies are the pinned central workflow and default permissions/secrets.

### Integration Points
This keeps stale policy shared with other Longhorn repositories.

### Risks
Pinned central workflow can become stale. Local permissions are not declared, so the called workflow must request or operate within inherited defaults.

### Test Signals
Signals include successful scheduled/manual invocation and expected stale labeling/commenting behavior in repository issues/PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/stale.yaml -->
