# sources/distributed-fs/eos/mgm/drain/DrainFs.cc

## Purpose
Implements draining of one filesystem: prepare the filesystem, schedule per-file `DrainTransferJob`s, monitor progress/stalls/expiry, update local drain status counters, stop jobs on cancellation, and mark final success or failure.

## Important APIs and Functions
- `DrainFs::DoIt` is the main per-filesystem drain loop.
- `GetSpaceConfiguration` reads `drainer.fs.ntx` and `drainer.tx.minrate` from space config.
- `PrepareFs` sets `kDrainPrepare`, waits service delay, reads drain period, then sets `kDraining` and initial counters.
- `UpdateFinishedJob` removes completed jobs from running state and records failures.
- `SuccessfulDrain` sets status `kDrained`, progress 100, and durable `configstatus=empty` unless MGM is shutting down.
- `FailedDrain` sets `kDrainFailed` and failed count.
- `StopJobs` cancels and waits for running transfer jobs.
- `UpdateProgress` updates counters, detects stalls/expiry, handles rerun once when files remain, and decides final state.
- `PrintJobsTable` emits running or failed transfer info.

## Control Flow
`DoIt` waits for namespace boot, exits successfully for empty filesystems, prepares the fs, streams file ids from `IFsView`, and schedules jobs while running jobs are within `mMaxJobs`. Each job is tracked in `mJobsRunning` and submitted to the shared thread pool; job completion calls back into `UpdateFinishedJob`. After each scheduling or wait interval, `UpdateProgress` can keep running, rerun, fail, or mark done. Cancellation or leftover running jobs triggers `StopJobs` and counter reset.

## State and Persistence
Runtime state includes source/target fsids, drain status, cancellation flag, max jobs, drain period, min transfer rate, running/failed job sets, total/pending counters, and progress timestamps. Persistent/durable impact is mostly through `FileSystemUpdateBatch`: local drain counters/status during operation, and durable `configstatus=empty` plus stored FS config on success.

## Dependencies and Integration Points
Uses `DrainTransferJob`, `IFsView`, `FsView`, global `gOFS`, EOS thread pool, file-system update batches, table formatting, namespace boot state, and fid tracker indirectly through jobs.

## Risks
- Scheduling condition uses `NumRunningJobs() <= mMaxJobs`, which permits one more than the configured maximum.
- Some helper declarations in the header (`MarkFsDraining`, `CollectDrainJobs`, `sRefreshTimeout`) are unused in this implementation.
- `GetSpaceConfiguration` requires a `FsView` lock per comment, but the implementation reads `mSpaceView` without taking one itself; callers must uphold that.
- Stalled drains sleep 30 seconds, slowing responsiveness to stop requests.
- Success writes durable `configstatus=empty` only when not shutting down; restart semantics depend on reapply logic elsewhere.

## Test Signals
Tests should cover empty fs success, prepare removal/stop cases, max-job boundary, failed-job rerun logic, drain expiry, stall status transitions, success durable config update, cancellation cleanup, and table rendering for running/failed jobs.
