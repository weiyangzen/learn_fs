## sources/control-plane/juicefs-csi-driver/pkg/util/resource/job.go

### Purpose
`resource/job.go` provides Kubernetes Job status helpers and a wait loop for job completion. It is used by mount and lifecycle code to interpret batch job conditions and recycle stale jobs.

### Important APIs, Types, And Functions
`IsJobCompleted(job)` checks for a true `JobComplete` condition. `IsJobFailed(job)` checks for a true `JobFailed` condition. `GetJobStatus(job)` renders a compact status string from active/succeeded/failed/terminating counts and conditions. `IsJobShouldBeRecycled(job)` decides whether a completed/failed job should be manually deleted. `WaitForJobComplete(ctx, client, name, timeout)` polls until success, failure, NotFound, or timeout.

### Control Flow
Status helpers iterate conditions. Recycle logic returns false unless the job is terminal, true if TTL is absent, false for failed jobs without completion time, and true if completion time plus TTL is before now. The wait loop ticks every two seconds, treats NotFound as success, fails on `JobFailed`, returns nil on `JobComplete`, and on timeout tries to fetch the job for a final status.

### State, Persistence, And Dependencies
No state is persisted here; it reads Kubernetes Job status through `K8sClient`. Dependencies include Kubernetes batch/core APIs, `config.Namespace`, `k8sclient`, and time.

### Integration Points
`PodMount.waitUntilJobCompleted` has its own shorter wait loop but uses `IsJobCompleted` and `IsJobShouldBeRecycled`. Other lifecycle controllers can call `WaitForJobComplete`.

### Risks
NotFound-as-success is appropriate for TTL cleanup but can hide unexpected deletion. Timeout handling calls `client.GetJob` with the already-expired `waitCtx`, which may return context errors instead of useful status. `GetJobStatus` overwrites status by count order before appending conditions, so mixed states need careful interpretation.

### Test Signals
`job_test.go` covers complete/failed condition recognition and recycle decisions for TTL/no-TTL/expired/nonterminal/nil-completion cases. Wait-loop behavior is not covered.
