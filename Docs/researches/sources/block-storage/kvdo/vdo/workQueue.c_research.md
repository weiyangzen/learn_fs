# File Research: sources/block-storage/kvdo/vdo/workQueue.c

## Purpose
Implements VDO kernel work queues for `vdo_completion` processing. It supports:
- simple single-thread queues,
- round-robin queues composed of multiple simple queues,
- priority funnel queues,
- kthread lifecycle,
- reduced wakeup behavior,
- debug dumping and current-work-queue introspection.

## Core Data Structures
- `struct vdo_work_queue`: common external object with name, round-robin flag, owner thread, and queue type.
- `struct simple_work_queue`: one worker kthread, priority funnel queues, private data, parent pointer, wait queues, startup state, idle/wakeup atomics, and debug timestamp.
- `struct round_robin_work_queue`: common object plus array of subordinate simple queues.
- Per-CPU `service_queue_rotor`: used to distribute submissions across round-robin subqueues.

## Completion Processing
`poll_for_completion()` scans priority queues from highest used priority down to zero and returns one completion. The comment explicitly notes priority is not strictly enforced under races.

`enqueue_work_queue_completion()`:
1. validates the completion is not already queued,
2. substitutes default priority if requested,
3. clamps invalid priority to zero after assertion failure,
4. records `completion->my_queue`,
5. pushes into the relevant funnel queue,
6. uses memory barriers, `idle`, and `first_wakeup` atomics to decide whether to wake the worker.

`service_work_queue()` runs optional start hook, repeatedly polls or waits for completions, runs callbacks through `vdo_run_completion_callback()`, yields on `need_resched()`, and runs optional finish hook on exit.

`wait_for_next_completion()` prepares the worker to sleep, marks it idle only after wait setup, polls again to avoid lost wakeups, checks `kthread_should_stop()`, schedules, and clears idle state on exit.

## Lifecycle
`make_simple_work_queue()` allocates the queue, duplicates the name, initializes wait queues/spinlock, allocates priority funnel queues, starts a kthread, records pid, and waits until the runner has entered VDO code.

`make_work_queue()` creates either:
- a simple queue when `thread_count == 1`, or
- a round-robin queue with `thread_count` subordinate simple queues.

`finish_work_queue()` stops simple worker threads or all round-robin subthreads. `free_work_queue()` finishes then frees the appropriate queue form.

## Debug and Introspection
- `dump_work_queue()` logs thread/idle/task-state info for simple or all round-robin queues.
- `dump_completion_to_buffer()` formats queue name and callback function symbol compactly.
- `get_current_work_queue()` returns the current VDO work queue only when running in a VDO work-queue kthread and not interrupt context.
- `get_work_queue_private_data()` returns the simple queue’s private pointer for the current worker thread.
- `get_work_queue_owner()` returns the owner `vdo_thread`.
- `vdo_work_queue_type_is()` compares a queue’s type pointer.

The current-thread detection includes kernel-version-specific handling for pre-5.13 `kthread_func()` behavior around `current->set_child_tid`.

## Dependencies
Uses Linux atomics, kthreads, percpu data, scheduler/task helpers, funnel queues, completion callbacks, logging, allocation, assertions, and string helpers.

## Invariants and Risks
- Completion `my_queue` must be NULL before enqueue and is cleared before callback execution.
- Queue finish assumes no further enqueueing after `finish_work_queue()` begins.
- Wakeup reduction relies on paired barriers and atomic state; comments acknowledge tolerated races with periodic wakeups/scheduling.
- Round-robin distribution is approximate and per-CPU rotor based.
- `vdo_work_queue_type_is()` assumes a valid non-NULL queue pointer.
