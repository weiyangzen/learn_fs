## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/job.go

### Purpose
`job.go` builds Kubernetes Jobs used for one-shot JuiceFS operations: create/delete subpath volumes, clean cache, abort hung FUSE connections, canary image/binary checks, and snapshot create/restore/delete workflows. It centralizes job naming, pod template reuse, command construction, TTL/backoff policies, and owner/integration defaults.

### Important APIs, Types, And Functions
`JobBuilder` embeds `PodBuilder`; `NewJobBuilder()` creates it. `NewJobForCreateVolume()`, `NewJobForDeleteVolume()`, and `NewJobForCleanCache()` produce volume lifecycle jobs. `GenJobNameByVolumeId()` hashes a volume ID to a stable `juicefs-...` prefix. `newJob()` builds the shared JuiceFS job template and `newCleanJob()` builds node-pinned cache-clean jobs. `NewFuseAbortJob()` builds a privileged sysfs job that may write `/sys/fs/fuse/connections/<minor>/abort`. `NewCanaryJob()` builds a node-pinned canary job from an existing mount pod. Snapshot APIs are `NewJobForSnapshot()`, `NewJobForRestore()`, and `NewJobForDeleteSnapshot()`.

### Control Flow
Create/delete jobs start from `newJob()`, combine optional init commands with a JuiceFS mount command, then perform mkdir or `juicefs rmr` under `/mnt/jfs`. `newJob()` sets a default secret name if absent, reuses common pod generation, adds a PreStop lazy unmount, lets the scheduler choose a node, copies CSI pod scheduling constraints, and sets a short TTL. FUSE abort jobs check fuse-pass health via inode probing first, inspect `waiting`, and only write `abort` when the kernel reports pending requests. Canary jobs delete any existing job with the same deterministic name before returning a fresh spec. Snapshot jobs mount, create/prepare paths, call `juicefs clone` or `juicefs rmr`, and unmount best-effort.

### State, Persistence, And Dependencies
The persisted state is Kubernetes `batchv1.Job` objects and their pod templates. Jobs also depend on Secrets produced by `NewSecret()` and later owned by the Job. Naming persists through a truncated sha256 hash of volume IDs. The code depends on `config`, `common`, `k8sclient`, `util`, Kubernetes batch/core APIs, and shell command strings.

### Integration Points
`PodMount.JCreateVolume`, `JDeleteVolume`, and `CleanCache` create these jobs, then wait for completion. `NewCanaryJob` integrates with upgrade/restart flows by deriving settings from a mount pod. `NewFuseAbortJob` integrates with corrupted/hung FUSE recovery and depends on dev minor tracking from `util/dev_minor.go`.

### Risks
Command strings are shell-heavy and must be escaped; create/delete commands escape subpaths, but snapshot/restore path inputs are interpolated more directly and need trusted caller validation. `newJob()` mutates `r.jfsSetting.SecretName`, which is convenient but surprising. TTL assumptions may fail on clusters without TTL-after-finished support, so cleanup code must handle stale jobs. FUSE abort is intentionally privileged and hostPath-backed, so it has a high security blast radius. Snapshot restore refuses non-empty targets, but path handling still matters.

### Test Signals
No direct job-builder tests are listed, but `resource/job_test.go` covers completion/failure/recycle helpers consumed by waiting code. Useful integration checks include generated job names, TTL/backoff values, owner secret creation, mount command content, FUSE abort skip/abort branches, and snapshot command path handling.
