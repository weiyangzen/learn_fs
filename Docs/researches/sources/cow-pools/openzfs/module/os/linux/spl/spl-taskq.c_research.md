# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-taskq.c

## Purpose

Implements the Linux SPL task queue subsystem, providing Solaris-style `taskq_*` APIs on top of Linux kthreads, wait queues, timers, spinlocks, CPU hotplug callbacks, and kstats. It exports global task queues used across OpenZFS and supports fixed, dynamic, delayed, priority, preallocated, and CPU-percentage-sized task queues.

## Major State

- `system_taskq`: global dynamic task queue for normal short work.
- `system_delay_taskq`: global dynamic queue for delayed work.
- `dynamic_taskq`: private queue used to create additional dynamic taskq worker threads without recursing into `system_taskq`.
- `tq_list` plus `tq_list_sem`: global registry of all task queues for kstats and kick handling.
- `taskq_tsd`: TSD key storing the current thread’s taskq membership.
- `spl_taskq_cpuhp_state`: CPU hotplug multi-state used for `TASKQ_THREADS_CPU_PCT`.

Module parameters:
- `spl_taskq_thread_bind`: optionally binds taskq threads to CPUs.
- `spl_taskq_thread_timeout_ms`: idle timeout pacing for dynamic thread exit.
- `spl_taskq_thread_dynamic`: enables dynamic taskq thread behavior.
- `spl_taskq_thread_priority`: enables setting worker nice levels from taskq priority.
- `spl_taskq_thread_sequential`: threshold of sequential tasks before trying to spawn more workers.
- `spl_taskq_kick`: write-only style trigger that scans taskqs for old pending work and tries to spawn more threads.

## Core Data Flow

Task dispatch allocates or reuses a `taskq_ent_t`, assigns a monotonically increasing `tqent_id`, links it to one of the task lists, wakes workers, and may request a dynamic worker spawn. The queue maintains separate ordered lists for:

- `tq_pend_list`: normal pending tasks.
- `tq_prio_list`: front/priority tasks and expired delayed tasks.
- `tq_delay_list`: timer-backed delayed tasks.
- `tq_active_list`: tasks currently executing on worker threads.
- `tq_free_list`: reusable task entries.

`taskq_lowest_id()` computes the lowest incomplete task ID across pending, priority, delay, and active state. `taskq_wait_id()`, `taskq_wait_outstanding()`, and `taskq_wait()` all build on that monotonic ID accounting.

## Important Functions

- `task_alloc()` / `task_free()` / `task_done()`: manage task entry reuse, allocation throttling, and free-list retention.
- `task_expire()` / `task_expire_impl()`: timer callback path for delayed tasks; moves them from delay list to priority list.
- `taskq_find()` and `taskq_find_list()`: locate dispatched tasks in queued or active state.
- `taskq_cancel_id()`: cancels pending or delayed tasks, optionally waits for active tasks, and uses `timer_delete_sync()` unconditionally to close a delayed-task expiry race.
- `taskq_dispatch()`: normal dispatch, honoring `TQ_NOQUEUE`, `TQ_FRONT`, allocation flags, and dynamic spawning.
- `taskq_dispatch_delay()`: delayed dispatch using Linux timers.
- `taskq_dispatch_ent()`: dispatches caller-provided preallocated entries.
- `taskq_thread()`: worker main loop; blocks signals, records TSD taskq membership, pulls priority before pending work, updates active lists, executes functions, updates lowest task ID, and exits if dynamic idle-stop rules allow.
- `taskq_thread_create()` / `taskq_thread_spawn()`: create workers directly or through `dynamic_taskq`.
- `taskq_create()` / `taskq_destroy()` / `taskq_create_synced()`: lifecycle and optional synchronized worker capture.
- `spl_taskq_expand()` / `spl_taskq_prepare_down()`: CPU hotplug callbacks for queues sized by CPU percentage.
- `spl_taskq_init()` / `spl_taskq_fini()`: module-level setup and teardown.

## Kstats

Per-taskq kstats expose static values, gauges, and counters including thread counts, pending/priority/delayed task counts, dispatch/execution counts, cancellation counts, wakeups, sleeps, and free entries. A raw `taskq/summary` kstat prints a compact all-taskq table.

## Concurrency And Correctness Notes

- `tq_lock` protects taskq lists, counts, and active state.
- `tq_lock_class` distinguishes general queues from `dynamic_taskq` to avoid lockdep false positives during nested dispatch.
- Task lists are kept in task-ID order where needed so wait semantics can be implemented cheaply.
- Preallocated entries are duplicated on worker execution because their original storage may be reused or freed by the task function.
- Delayed cancellation deliberately avoids relying on `timer_pending()` because an expired timer can be dequeued before its callback runs.
- `taskq_destroy()` first clears `TASKQ_ACTIVE`, waits for outstanding dynamic-spawn work, drains tasks, stops workers, frees cached entries, and asserts all lists/counts are empty.
