# sources/distributed-fs/ceph-client/fs/btrfs/async-thread.c

## Purpose
Implements Btrfs-specific workqueue wrappers for asynchronous work, ordered completion callbacks, per-filesystem ownership tracing, congestion checks, and adaptive concurrency thresholding.

## Important APIs, Types, And Functions
`struct btrfs_workqueue` wraps a kernel `workqueue_struct`, the owning `btrfs_fs_info`, an ordered-work list and lock, pending count, active worker limits, threshold state, and threshold lock. Exported functions include `btrfs_alloc_workqueue()`, `btrfs_alloc_ordered_workqueue()`, `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_destroy_workqueue()`, `btrfs_workqueue_set_max()`, `btrfs_flush_workqueue()`, `btrfs_workqueue_owner()`, `btrfs_work_owner()`, and `btrfs_workqueue_normal_congested()`.

Internal helpers include `thresh_queue_hook()`, `thresh_exec_hook()`, `run_ordered_work()`, and `btrfs_work_helper()`. Work flags `WORK_DONE_BIT` and `WORK_ORDER_DONE_BIT` coordinate ordinary and ordered phases.

## Control Flow
Allocation initializes ownership, pending state, ordered list, and locks. Regular workqueues may start with `current_active = 1` and grow toward `limit_active` when a threshold is configured; low or disabled thresholds use `NO_THRESHOLD`. Ordered workqueues are allocated through `alloc_ordered_workqueue()` and fixed at one active worker.

`btrfs_queue_work()` assigns the workqueue pointer, increments pending threshold state, appends ordered work to `ordered_list` under `list_lock` when needed, traces the queue event, and queues the kernel work item. `btrfs_work_helper()` runs in worker context, applies threshold execution adjustment, calls the work function, and either traces completion directly or marks `WORK_DONE_BIT` with a memory barrier and calls `run_ordered_work()`.

`run_ordered_work()` walks the ordered list from the head and only runs ordered callbacks for work items whose normal work has completed. It leaves the current item on the list as a barrier while its ordered function runs, then removes it and calls the ordered free callback outside the lock. If the completed item is the currently executing work, freeing is deferred until after traversal to avoid recycling the work item while kernel workqueue non-reentrancy assumptions still depend on its address.

Thresholding increments pending in queue context, decrements in worker context, and periodically adjusts `workqueue_set_max_active()` based on pending load under `thres_lock`. Congestion reports true when pending is more than twice the threshold.

## State And Persistence
All state is in memory. Workqueue state includes pending count, current/limit active counts, ordered list membership, per-work flags, and ownership pointers. Work callbacks can mutate filesystem state, but this wrapper only coordinates execution and completion ordering. Destroying the workqueue drains kernel workqueue resources and frees the wrapper.

## Dependencies And Integration Points
It depends on Linux workqueues, spinlocks, atomics, memory barriers, tracepoints from `trace/events/btrfs.h`, and the Btrfs `struct btrfs_work` declared in `async-thread.h`. It is used by Btrfs subsystems needing asynchronous execution with optional ordered completion, such as delayed work, compression, endio, or transaction-adjacent tasks.

## Risks
The ordered-work logic is concurrency-sensitive. Missing barriers could allow ordered callbacks to see stale writes from normal work. Freeing or reusing work items too early can deadlock with kernel workqueue non-reentrancy behavior, especially across filesystems or loop-device dependencies. Threshold adjustment has a likely bug-prone condition around `wq->count %= (wq->thresh / 4)` and when adjustment is skipped, so changes need careful load testing. Updating `limit_active` does not immediately call `workqueue_set_max_active()`; it only constrains future threshold changes.

## Test Signals
Tests should queue ordered and unordered work, verify ordered callbacks run in submission order even when normal work finishes out of order, confirm free callbacks are not called under list lock, stress queue/destroy/flush races, exercise threshold growth/shrink under pending load, and check tracepoints/congestion reporting. Memory-ordering bugs are best exposed with stress tests on weakly ordered architectures.
