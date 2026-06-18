# sources/distributed-fs/ceph-client/drivers/powercap/idle_inject.c

## Purpose
`idle_inject.c` implements the idle injection framework, allowing clients to force selected CPUs into precise idle intervals for a configured portion of a period. It is intended for power capping and thermal control.

## Important APIs, Types, And Functions
`struct idle_inject_thread` stores the per-CPU smpboot task and run flag. `struct idle_inject_device` stores hrtimer, idle/run durations, max latency, optional update callback, and cpumask. Exported APIs are `idle_inject_register_full()`, `idle_inject_register()`, `idle_inject_unregister()`, `idle_inject_set_duration()`, `idle_inject_get_duration()`, `idle_inject_set_latency()`, `idle_inject_start()`, and `idle_inject_stop()`. Internal work uses `idle_inject_wakeup()`, `idle_inject_timer_fn()`, `idle_inject_fn()`, and smpboot callbacks.

## Control Flow
An early initcall registers per-CPU smpboot threads. A client registers a cpumask; registration allocates an `idle_inject_device`, initializes its hrtimer, sets default latency, stores an optional update callback, and claims per-CPU device pointers. Starting verifies nonzero total period, wakes all online CPUs in the mask, and starts a periodic hrtimer. Each timer tick optionally calls `update()`, wakes per-CPU threads, and forwards the timer by run+idle duration. Each woken thread clears its `should_run` flag and calls `play_idle_precise()` for the idle duration with the configured latency. Stop cancels the timer, disables CPU hotplug, clears `should_run` for all CPUs in the mask, waits for tasks to become inactive, and reenables hotplug. Unregister stops, clears per-CPU pointers, and frees the device.

## State, Persistence, And Dependencies
State is per-CPU `idle_inject_thread`, per-CPU `idle_inject_device *`, the allocated control device, and hrtimer. No persistent state exists. Dependencies include smpboot, hrtimer, CPU hotplug locking, scheduler `play_idle_precise()`, RT scheduling setup via `sched_set_fifo()`, and the exported `IDLE_INJECT` namespace.

## Integration Points
Clients from thermal/powercap code can register CPU masks, update duty cycles dynamically, and start/stop injection. The Kconfig option is `IDLE_INJECT`, and symbols are exported in namespace `"IDLE_INJECT"`.

## Risks
The framework relies on callers to provide higher-level synchronization against concurrent start/stop/unregister and duration updates. `idle_inject_set_duration()` ignores attempts to set both run and idle to zero, so callers cannot clear the period through that API. `idle_inject_start()` can be called repeatedly without an explicit running flag, potentially restarting an already active hrtimer. Registration prevents overlapping CPU masks by checking per-CPU ownership, but there is no lock around concurrent registrations.

## Test Signals
Test register/unregister with overlapping masks, start without duration, 100 percent idle (`run_duration_us=0`), stop while CPUs are in `play_idle_precise()`, CPU hotplug during stop/start, update callback skip/reschedule behavior, repeated start calls, and exported namespace usage by clients.
