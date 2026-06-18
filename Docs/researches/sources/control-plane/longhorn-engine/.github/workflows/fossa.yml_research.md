<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/fossa.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/fossa.yml

### Purpose
This workflow runs FOSSA license/security scanning for the canonical Longhorn Engine repository.

### Important APIs, Types, And Functions
It triggers on pushes to `master`/`v*`, tags `v*`, and manual dispatch. The job is gated by `github.repository == 'longhorn/longhorn-engine'`, grants `contents: read`, checks out code, and runs pinned `fossas/fossa-action` with `FOSSA_API_KEY` and project `longhorn-engine`.

### Control Flow
On eligible events in the canonical repository, the job checks out the code and uploads scan data to FOSSA.

### State, Persistence, And Dependencies
State is external FOSSA project scan results. Dependencies include the FOSSA GitHub Action and the `FOSSA_API_KEY` secret.

### Integration Points
This supports compliance/release processes outside the build pipeline.

### Risks
Forks do not run scans. Secret absence or FOSSA outage fails the job. The action comment says locking is preferred even though the action is pinned.

### Test Signals
Signals include workflow skip on forks, successful scan upload in canonical repo, and FOSSA project updates for branch/tag pushes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/fossa.yml -->
