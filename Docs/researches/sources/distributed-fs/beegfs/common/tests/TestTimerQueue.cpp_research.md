# sources/distributed-fs/beegfs/common/tests/TestTimerQueue.cpp

Purpose: This file tests asynchronous `TimerQueue` scheduling, cancellation, and worker concurrency.

Important APIs/types/functions: `TestTimerQueue` owns a `std::unique_ptr<TimerQueue>` and starts `TimerQueue(0, 20)` in `SetUp()`. `EnqueueCancelFn` increments an `AtomicSizeT`; `EnqueueManyLongFn` sleeps for one second and increments a shared atomic counter.

Control flow: `enqueueCancel` schedules a callback after 100 ms, cancels its handle, sleeps one second, and verifies no callback ran. `enqueueManyLong` enqueues 42 callbacks after 10 ms, each sleeping one second, then waits until all complete and asserts elapsed time is under 20 seconds. With one-at-a-time execution, the test would take roughly 42 seconds, so the assertion proves parallel worker execution.

State and persistence behavior: State is in-memory atomic counters and queued callbacks. No persistence is involved.

Dependencies and integration: `TimerQueue` is used by metadata service scheduling, including client sync requeueing and disposal garbage collection in this subset. Cancellation correctness matters for shutdown and race-free delayed work.

Risks and test signals: The tests are timing-sensitive and use `sleep(1)`, so heavily loaded systems may produce noise. They provide useful behavioral signal for cancellation and parallelism but not for shutdown drain, exception handling inside callbacks, or ordering of equal deadlines.
