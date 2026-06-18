<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.h -->
## sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.h

### Purpose
This header declares the delayed task scheduler, worker list, worker threads, and cancellation handle used by BeeGFS common code.

### Important APIs, Types, And Functions
`TimerWorkList` provides thread-safe ready-work enqueue/dequeue/count. `TimerWorker` is a `PThread` with start/stop/run, keepalive behavior, id, and atomic state. `TimerQueue` is a `PThread` with `EntryHandle`, constructor/destructor, `enqueue`, `cancel`, manager `run`, worker request, and worker deactivation.

### Control Flow
`EntryHandle::cancel` delegates to its owning queue. `TimerQueue` manages scheduled actions and workers; workers execute ready actions outside the queue mutex through `TimerWorkList`.

### State, Persistence, And Dependencies
Types encode in-memory scheduler state only. `QueueType` uses `std::chrono::steady_clock` and sequence numbers for deterministic ordering; a static assertion requires millisecond-or-better clock precision.

### Integration Points
Common components can include this header to schedule `std::function<void()>` callbacks. Unit tests are registered through the common CMake file.

### Risks
`TimerQueue` is noncopyable/nonmovable but `EntryHandle` is lightweight and can become dangling if retained after queue destruction. Callback execution is unconstrained; long-running callbacks occupy worker threads.

### Test Signals
Header-level tests should verify API usability with lambdas, move-only captures wrapped in `std::function` where supported, cancellation handle behavior, and pool sizing boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.h -->
