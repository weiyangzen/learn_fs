# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/Scheduler.java

Purpose: master-side scheduler for Alluxio jobs. It owns active job state, periodically refreshes workers, assigns tasks, handles task callbacks, persists job updates, and cleans old finished jobs.

Important APIs/types/functions: `start`, `stop`, `submitJob`, `stopJob`, `getJobProgress`, `updateWorkers`, `cleanupStaleJob`, `processJobs`, `processJob`, and `scheduleTask`. Core maps are `mExistingJobs`, `mRunningTasks`, and `mActiveWorkers`.

Control flow: `start` retrieves persisted jobs, creates a single-thread scheduled executor, refreshes workers at configured interval, processes jobs every 100 ms, and cleans stale jobs hourly. `submitJob` updates a matching non-done job or persists and starts a new one if capacity allows. `processJob` persists completed/stopped jobs, fails unhealthy jobs, schedules at most one task per worker per job description, and completes or starts verification when the current pass finishes. `scheduleTask` obtains the next task, executes it on the worker client, and adds a future listener on the scheduler executor to process responses and chain more work.

State and persistence: job metadata is persisted through `JobMetaStore.updateJob`. Running worker sets are per-job `HashSet`s stored in a concurrent map; worker clients are immutable-map snapshots and are closed on stop or worker loss. Finished jobs are retained in `mExistingJobs` until retention cleanup.

Dependencies/integration: depends on `WorkerProvider`, `BlockWorkerClient`, scheduler `Job`/`Task` APIs, `JobProgressReportFormat`, `Configuration`, and Alluxio runtime exception classes.

Risks: per-job running-worker sets are plain `HashSet`s mutated by scheduler callbacks; the design relies on the single scheduler executor, but worker refresh can replace `mActiveWorkers` concurrently. `submitJob` and processing can race around `mRunningTasks`. Exceptions are broadly caught to preserve the scheduler thread, which can hide systemic issues except for logs and job failure state.

Test signals: tests should cover job recovery, duplicate submit/update, capacity exhaustion, worker refresh add/drop/client-close, task chaining, retryable/nonretryable `getNextTask` errors, stop job persistence, verification transition, retention cleanup, and executor shutdown.
