# sources/distributed-fs/ceph-client/kernel/torture.c

## Purpose

`torture.c` provides common infrastructure for in-kernel torture test modules, especially RCU-derived stress tests. It centralizes randomized sleeps, CPU hotplug churn, task shuffling, automatic shutdown, stutter/pause behavior, lifecycle serialization, and generic torture kthread helpers. Client torture modules explicitly call these helpers instead of using this file as an independent module entry point.

## Important APIs, types, and functions

- Module parameters: `disable_onoff_at_boot`, `ftrace_dump_at_shutdown`, `verbose_sleep_frequency`, `verbose_sleep_duration`, and `random_shuffle`.
- Lifecycle state: `FULLSTOP_DONTSTOP`, `FULLSTOP_SHUTDOWN`, `FULLSTOP_RMMOD`, guarded by `fullstop_mutex`.
- Sleep/random helpers: `verbose_torout_sleep()`, `torture_hrtimeout_ns/us/ms/jiffies/s()`, and `torture_random()`.
- CPU hotplug helpers under `CONFIG_HOTPLUG_CPU`: `torture_num_online_cpus()`, `torture_offline()`, `torture_online()`, `torture_onoff_init()`, `torture_onoff_stats()`, and `torture_onoff_failures()`.
- Task shuffling helpers: `torture_shuffle_task_register()`, `torture_shuffle_init()`, and internal `torture_shuffle_tasks()`.
- Shutdown helpers: `torture_shutdown_absorb()`, `torture_shutdown_init()`, reboot notifier `torture_shutdown_notify()`, and cleanup logic.
- Stutter helpers: `stutter_wait()` and `torture_stutter_init()`.
- Test lifecycle: `torture_init_begin()`, `torture_init_end()`, `get_torture_init_jiffies()`, `torture_cleanup_begin()`, `torture_cleanup_end()`, `torture_must_stop()`, and `torture_must_stop_irq()`.
- Thread helpers: `torture_kthread_stopping()`, `_torture_create_kthread()`, and `_torture_stop_kthread()`.

## Control flow

A client module begins with `torture_init_begin(ttype, verbose)`. This serializes against existing torture tests, records the type string, sets normal fullstop state, stores the initialization jiffies, and prints parameters. The client then initializes optional subsystems such as CPU on/off, shuffling, shutdown, and stutter, and calls `torture_init_end()` to release the mutex and register the reboot notifier.

CPU hotplug stress starts with `torture_onoff_init()`, which creates `torture_onoff()` when an interval is configured. That kthread brings all CPUs online, waits for holdoff and boot completion, then repeatedly picks a random CPU and tries to offline it or online it, updating success/failure and timing statistics. Cleanup stops the thread and brings all CPUs online again.

Task shuffling starts with `torture_shuffle_init()`. Registered kthreads are kept in `shuffle_task_list`. The shuffler periodically builds a CPU mask that excludes one CPU, then applies it to registered tasks so each CPU can become idle in turn. With `random_shuffle`, only a random subset of tasks is moved each interval.

Automatic shutdown uses `torture_shutdown_init()`, which creates a thread sleeping until an absolute shutdown time. If the test has not stopped, the thread runs the registered cleanup hook, optionally dumps ftrace, and calls `kernel_power_off()`. An external reboot/shutdown triggers `torture_shutdown_notify()`, which moves fullstop state to shutdown so kthreads can park via `torture_shutdown_absorb()`.

Stuttering uses `torture_stutter()` to periodically set `stutter_till_abs_time`; participating test threads call `stutter_wait()` and sleep until the pause interval ends.

Cleanup starts with `torture_cleanup_begin()`. It detects a shutdown/rmmod race, otherwise sets fullstop to rmmod, stops common helper threads in a safe order, and returns whether the caller should abandon normal teardown. `torture_cleanup_end()` clears `torture_type` after client threads have stopped.

## State and persistence behavior

The file maintains global singleton state for one active torture test: `torture_type`, `verbose`, `fullstop`, and `torture_init_jiffies`. Hotplug, shuffle, shutdown, and stutter each keep static task pointers and configuration. Hotplug statistics persist until module cleanup and are reported through exported stats/failure functions. `shuffle_task_list` owns heap-allocated `shuffle_task` nodes registered for each torture kthread and frees them on shuffle cleanup.

Concurrency is guarded by mutexes for fullstop and shuffle list updates, atomic state for verbose sleeps, `READ_ONCE()`/`WRITE_ONCE()` for lockless stop and timing flags, cpus read locks during affinity changes, and kthread stop synchronization during cleanup.

## Dependencies and integration points

The file depends on generic kernel kthreads, CPU hotplug (`add_cpu()`, `remove_cpu()`, `cpu_is_hotpluggable()`), scheduler affinity, hrtimers, reboot notifiers, freezer/scheduling APIs, RCU torture helpers from `rcu/rcu.h`, trace clock/local clock, and exported declarations in `linux/torture.h`. It exports symbols for client modules such as RCU, lock, refscale, or other kernel torture tests.

## Risks and edge cases

- Only one torture test may run at a time. Mispaired `torture_init_begin/end` or cleanup calls can leave `fullstop_mutex` or `torture_type` in a bad state.
- Shutdown and rmmod are intentionally treated as illegal concurrently; clients must honor `torture_cleanup_begin()` returning true.
- Kthreads must call `torture_kthread_stopping()` before returning, otherwise module text/data may be freed while a thread still runs.
- CPU hotplug operations can fail during early boot due to transient platform restrictions; the code forgives early `-EBUSY` but records other failures.
- Affinity shuffling can fail or be ineffective on one-CPU systems or under cpuset constraints; the code skips the one-online-CPU case.
- The random generator is crude and not cryptographic; it is intended for stress variation only.

## Test signals

Signals include successful creation and stopping of helper kthreads, hotplug success/attempt ratios from `torture_onoff_stats()`, absence of `torture_onoff_failures()`, correct parking during shutdown, full CPU restoration after hotplug cleanup, and no lingering registered shuffle tasks. Kernel logs with `TORTURE_FLAG`, lockdep, CPU hotplug warnings, and ftrace dumps at shutdown are the primary observability path.
