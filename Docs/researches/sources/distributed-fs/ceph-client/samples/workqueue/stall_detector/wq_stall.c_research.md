# sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/wq_stall.c

## Purpose
`wq_stall.c` is a deliberate fault-injection sample module for validating the workqueue stall detector. It hides a worker from workqueue concurrency accounting so a queued item remains stuck long enough to trigger watchdog diagnostics.

## APIs, Types, And Functions
It defines a wait queue, `atomic_t wake_condition`, and two `work_struct`s. `stall_work1_fn()` triggers the stall; `stall_work2_fn()` reports when the second item eventually runs. `wq_stall_init()` schedules the first work item, and `wq_stall_exit()` wakes and flushes both work items.

## Control Flow
The first work item queues the second item on the same per-CPU pool, clears `PF_WQ_WORKER`, then sleeps in `wait_event_idle()`. Because the worker no longer calls `wq_worker_sleeping()`, the pool can believe a worker is still running and may not start another, leaving the second item pending until the watchdog reports a lockup. Module exit restores progress by setting the wake condition and flushing work.

## State And Persistence
State is kernel-memory-only: work items, wait queue, atomic wake condition, and temporary mutation of `current->flags`. No persistence exists after module unload.

## Dependencies And Integration Points
It depends on workqueue internals, scheduler task flags, wait queues, and module lifecycle APIs. It integrates with workqueue watchdog diagnostics and kernel logs.

## Risks And Test Signals
This module intentionally creates a kernel stall and should only run in test environments. Risks include noisy lockup reports or delayed unload. Test signals are expected `BUG: workqueue lockup` diagnostics after roughly 30-60 seconds, second work item running after unload wakeup, and clean `flush_work()` completion.
