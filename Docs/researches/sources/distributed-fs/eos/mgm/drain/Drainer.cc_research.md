# sources/distributed-fs/eos/mgm/drain/Drainer.cc

## Purpose
Implements the central drain manager. It starts/stops the drainer thread, launches per-filesystem `DrainFs` supervisors, queues drains when a node already has too many active filesystem drains, exposes job info, reapplies drain state after mastership, and persists drainer configuration.

## Important APIs and Functions
- `Start`/`Stop` manage the assisted central thread and clear drain fid tracker state on stop.
- `StartFsDrain` validates optional target fs in same space/group, prevents duplicate/pending drains, queues when per-node limit is reached, or starts an async `DrainFs::DoIt`.
- `StopFsDrain` removes pending requests or signals an active `DrainFs` to stop.
- `GetJobsInfo` collects transfer job rows from all or one drain supervisor.
- `Drain` waits for namespace boot/mastership, reapplies drain status, periodically handles queued drains, cleans fid tracker state, and removes completed supervisors.
- `WaitForAllDrainToStop` signals and waits for all active drains before clearing maps.
- `ApplyConfig`, `SetConfig`, `SerializeConfig`, and `StoreConfig` manage global drainer settings.
- `HandleQueued` retries pending drain requests.

## Control Flow
The central thread starts only after namespace boot and mastership, then loops every five seconds. User/API calls to `StartFsDrain` either launch a new `DrainFs` with `std::async` or mark the filesystem `kDrainWait` and append to `mPending`. `HandleQueued` swaps pending requests out under lock and calls `StartFsDrain` for each. Completed futures are removed from `mDrainFs`.

## State and Persistence
Runtime state includes a map from node hostport to active `DrainFs` set, pending source/destination fsid pairs, a shared drain transfer thread pool, and max parallel fs per node. Drainer config is stored in `FsView` global config key `drainer`. Individual filesystem status persistence is handled by `DrainFs`.

## Dependencies and Integration Points
Depends on global `gOFS`, `FsView`, `IMaster`, `DrainFs`, `DrainTransferJob`, thread pool, fid tracker, string tokenization, stacktrace utilities, and table formatting. Start/stop methods assume callers hold `FsView::ViewMutex` read locks per header note.

## Risks
- `HandleQueued` holds an `FsView` read lock while calling `StartFsDrain`, whose header also expects the lock but internally may take `mDrainMutex`; lock ordering should be reviewed against other callers.
- `Stop` joins the assisted thread and then clears tracker; if called when never started, behavior depends on `AssistedThread`.
- `mCfgMutex` exists in the header but config mutation here does not use it.
- Queueing sets local drain wait status but does not persist a durable pending queue; process restart relies on filesystem drain status reapply, not `mPending`.
- `DrainMap` uses `std::set<std::shared_ptr<DrainFs>>`, ordered by pointer rather than fsid.

## Test Signals
Tests should cover same-space/group validation for forced target, duplicate and pending detection, per-node queueing, stop pending vs active drain, config parsing/persistence, completed future cleanup, master wait/reapply behavior, and `GetJobsInfo` for empty and populated drain maps.
