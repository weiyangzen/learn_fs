# sources/distributed-fs/eos/mgm/convert/ConverterEngine.cc

## Purpose
Implements the central converter thread that accepts conversion requests, durably records pending jobs in QuarkDB, dispatches `ConversionJob` tasks to a thread pool, handles cleanup, and persists converter configuration in the global config map.

## Important APIs and Functions
- `Start` and `Stop` manage the assisted converter thread.
- `PopulatePendingJobs` reloads QuarkDB pending jobs into the in-memory queue, using `mFidTracker` to avoid duplicate scheduling.
- `HandlePostJobRun` removes a job from running state, deletes its QuarkDB pending entry, records failures, removes the conversion proc file, notifies observers, and clears the fid tracker.
- `Convert` waits for namespace boot and mastership, reloads pending jobs, drains the in-memory queue into thread-pool tasks, and joins jobs on termination.
- `JoinAllConversionJobs` cancels running jobs and waits until they leave running/pending states.
- `ScheduleJob` validates running state, queue size, conversion string, and duplicate fid tracking, then queues in memory and writes to QuarkDB.
- `ApplyConfig`, `SetConfig`, `SerializeConfig`, and `StoreConfig` manage global converter settings.
- `QdbHelper` wraps the `eos-conversion-jobs-pending` hash with add/list/clear/remove operations.

## Control Flow
Scheduling pushes a job to the in-memory queue and then persists it to QDB. The converter thread waits for items, waits for thread-pool capacity, parses the conversion string, creates a `ConversionJob`, pushes a task that runs the job and post-run cleanup, then records it in `mJobsRunning`. On invalid persisted conversion strings, it removes the pending hash entry and tracker entry.

## State and Persistence
Durable pending jobs are stored in QuarkDB hash `eos-conversion-jobs-pending`, keyed by decimal fid and valued by conversion string. Runtime-only state includes `mPendingJobs`, `mJobsRunning`, callbacks, failure count, observer manager, thread pool, max queue size, and fid tracker entries. Converter config is persisted through `FsView::gFsView.SetGlobalConfig("converter", ...)`.

## Dependencies and Integration Points
Depends on `ConversionInfo`, `ConversionJob`, QuarkDB qclient/QHash, `FsView`, MGM master state, global fid tracker, common thread pool, observer manager, and `XrdOucCallBack`.

## Risks
- `ScheduleJob` pushes to memory before `AddPendingJob`; if QDB persistence fails, the job may run but will not survive restart.
- `QdbHelper::AddPendingJob` writes `std::cerr << "hset: ..."` from daemon code, likely unintended noisy output.
- Recovered pending jobs use `nullptr` callbacks, so restart loses callback notification.
- `Stop` joins the assisted thread before setting `mIsRunning=false`; behavior depends on `AssistedThread::join` signalling termination.
- `Convert` records the running job after pushing the task, so a very fast job can call `HandlePostJobRun` before it is inserted into `mJobsRunning`.
- `NumPendingJobs` reports in-memory queue size, not durable QDB pending count.

## Test Signals
Tests should cover scheduling persistence failure, restart reload, duplicate fid tracking, invalid conversion removal, thread-pool queue throttling, config parsing bounds, observer notifications, and the race between task execution and `mJobsRunning` insertion.
