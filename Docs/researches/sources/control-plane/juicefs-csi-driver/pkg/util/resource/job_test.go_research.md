## sources/control-plane/juicefs-csi-driver/pkg/util/resource/job_test.go

### Purpose
`job_test.go` verifies the pure Job status helpers in `resource/job.go`. It documents how completion, failure, and recycle decisions are expected to behave for representative Kubernetes Job statuses.

### Important APIs, Types, And Functions
Tests are `TestIsJobCompleted`, `TestIsJobFailed`, and `TestIsJobShouldBeRecycled`. They construct `batchv1.Job` objects with controlled conditions, TTLs, and completion times.

### Control Flow
The first two tests use table cases with complete and failed conditions. The recycle test uses current time, a one-second TTL, and cases for fresh completed jobs, no TTL, completion time older than TTL, non-complete jobs, and failed jobs without completion time.

### State, Persistence, And Dependencies
There is no external state. Dependencies are Kubernetes batch/core/meta APIs and `time`.

### Integration Points
These tests protect helper behavior consumed by mount job wait/recycle paths.

### Risks
`WaitForJobComplete` is not tested. Edge cases such as multiple conditions, terminating count rendering, and failed jobs with old completion times are not covered.

### Test Signals
Failures indicate changed terminal-condition interpretation or cleanup policy. Any change to TTL behavior should update this suite.
