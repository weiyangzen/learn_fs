# sources/distributed-fs/ceph-client/kernel/time/timer.c

## Purpose
This file implements the kernel's classic timer wheel, jiffies state, timer initialization/modification/deletion APIs, timer softirq execution, nohz timer event prediction, timer migration support, process tick accounting entry points, and CPU hotplug timer migration.

## Important APIs, types, and functions
Global `jiffies_64` is exported. Core state is per-CPU `struct timer_base`, with lock, running timer pointer, base clock, next expiry, idle/pending flags, pending bitmap, and wheel buckets. Public APIs include `timer_init_key()`, stack timer init/destroy helpers, `mod_timer_pending()`, `mod_timer()`, `timer_reduce()`, `add_timer()`, `add_timer_local()`, `add_timer_global()`, `add_timer_on()`, `timer_delete()`, `timer_shutdown()`, `timer_delete_sync_try()`, `timer_delete_sync()`, `timer_shutdown_sync()`, jiffies rounding helpers, `get_next_timer_interrupt()`, `timer_base_try_to_set_idle()`, `timer_clear_idle()`, `update_process_times()`, and `timers_init()`.

## Control flow
Timers are placed into a multi-level wheel by `calc_wheel_index()`, which selects a bucket based on expiration delta and level granularity. `__mod_timer()` serializes on the timer's current base, optimizes unchanged/same-bucket updates, detaches pending timers, migrates base ownership when necessary, and enqueues into the selected bucket. Timer interrupt processing calls `update_process_times()`, which runs hrtimer queues, checks timer bases, and raises `TIMER_SOFTIRQ` when needed. The softirq runs `__run_timer_base()`, collects expired buckets, recalculates next expiry, detaches timers, drops locks around callbacks, and tracks `running_timer` for synchronous deletion.

## State and persistence behavior
Persistent runtime state is per-CPU and in-memory: timer bases, pending bitmaps, bucket lists, next-expiry calculations, nohz static keys, migration settings, and timer object flags encoding base CPU, pinned/deferrable/irqsafe/shutdown state, and wheel index. There is no disk persistence. CPU hotplug moves pending timers from dead CPU bases to the current CPU while preserving expiry behavior.

## Dependencies and integration points
The file integrates with jiffies, hrtimers, tick/nohz, timer migration hierarchy, softirqs, scheduler tick accounting, POSIX CPU timers, RCU scheduler clock ticks, irq_work, debug objects, lockdep, tracepoints, sysctl, and CPU hotplug. It is a foundational service for most kernel timeout users, including networking, block I/O, workqueues, and drivers.

## Risks
Risks are dominated by concurrency and timing semantics: timer-base locking, migration races, shutdown-vs-rearm ordering, lockdep expectations for `timer_delete_sync()`, PREEMPT_RT callback wait behavior, idle/nohz wakeups, and one-jiffy delays from lockless next-expiry reads. Wheel granularity intentionally batches far-future timers; users requiring precise expiry must use hrtimers. Incorrect pending bitmap or bucket index maintenance can lose timers or fire them late.

## Test signals
Runtime signals include timer tracepoints, debug object warnings, lockdep reports, nohz idle behavior, sysctl `kernel.timer_migration`, CPU hotplug stress, and softirq timer execution. Useful tests include timer selftests, workqueue delayed-work teardown tests using `timer_shutdown_sync()`, PREEMPT_RT coverage, nohz full/timer migration scenarios, and boot tests across different `HZ` values.
