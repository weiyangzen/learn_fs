# sources/distributed-fs/eos/mgm/drain/DrainFs.hh

## Purpose
Declares the per-filesystem drain controller used by the central `Drainer`. It owns the future for one filesystem drain and the transfer jobs running under it.

## Important APIs and Types
- `enum class State { Done, Failed, Running, Rerun }` describes supervisor outcomes.
- Public lifecycle/status methods: constructor, destructor, `SignalStop`, `GetDrainStatus`, `GetFsId`, `DoIt`, `SetFuture`, `IsRunning`.
- `PrintJobsTable` exposes transfer job status for admin/monitoring output.
- `UpdateFinishedJob` is the completion callback used by thread-pool transfer tasks.
- Private helpers cover counter reset, space config, preparation, progress, final status, stop, and namespace boot wait.

## Control Flow and State
The class stores fs view pointer, source/target fsids, drain status, cancellation flag, max parallel jobs, drain period, min transfer rate, drain timestamps, failed/running job collections, a shared thread pool reference, future, and progress counters. `IsRunning` is future-based rather than status-based.

## Dependencies and Integration Points
Depends on EOS file-system metadata/status types, `IFsView`, common logging/RWMutex, `ThreadPool`, `DrainTransferJob`, and table formatting.

## Risks
- `mStatus` and `mDidRerun` are not atomic; access is mostly supervisor-thread local, but status can be read externally.
- `mJobsFailed` is a set of shared pointers with default pointer ordering, not ordered by fid or error.
- Unimplemented private declarations (`MarkFsDraining`, `CollectDrainJobs`) can confuse maintainers.
- `sRefreshTimeout` is declared but not meaningfully used.

## Test Signals
Tests should cover future-based `IsRunning`, `SignalStop`, job completion bookkeeping, counter reset, status reads during execution, and compile warnings for declared-but-unimplemented helpers if build flags catch them.
