<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.cpp

### Purpose
`TimerQueue.cpp` implements delayed function scheduling backed by a manager thread and an elastic pool of timer worker threads.

### Important APIs, Types, And Functions
Implemented pieces include `TimerWorkList::enqueue/deque/waitingItems`, `TimerWorker` construction/destruction/start/stop/run`, `TimerQueue` construction/destruction, `enqueue`, `cancel`, `run`, `requestWorkers`, and `deactivateWorker`.

### Control Flow
`TimerQueue::enqueue` inserts actions keyed by due time and sequence number, then signals the manager. The manager waits until the next due action or idle timeout, moves due actions into `TimerWorkList`, and requests enough inactive workers for queued work. Workers try an immediate dequeue, then wait up to ten seconds; non-keepalive workers exit when idle, while keepalive workers remain. Destruction stops the manager, wakes/stops workers, and enqueues empty functions to break waits.

### State, Persistence, And Dependencies
State includes a mutex/condition, monotonic-clock queue, sequence counter, work list, worker pool, and inactive-worker map. All state is in-memory. Dependencies include `Condition`, `PThread`, `StringTk`, chrono, map, deque, and function.

### Integration Points
`CMakeLists.txt` includes `TestTimerQueue.cpp`, showing this component has unit coverage. Other BeeGFS components can schedule deferred callbacks without tying up the manager thread.

### Risks
`EntryHandle::cancel` assumes the handle still points to a live queue; handles outliving `TimerQueue` are unsafe. Worker function exceptions are not caught in `TimerWorker::run`, so an action can terminate a worker thread unexpectedly. Worker startup failures cause short retry loops through `workerRetryTimeout`.

### Test Signals
Tests should cover delayed execution ordering, same-time sequence ordering, cancellation before due time, zero-delay self-requeue termination behavior, min/max pool behavior, idle worker deactivation, destructor wakeup, and action exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.cpp -->
