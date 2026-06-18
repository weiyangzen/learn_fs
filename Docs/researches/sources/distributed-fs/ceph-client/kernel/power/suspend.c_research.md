# sources/distributed-fs/ceph-client/kernel/power/suspend.c

## Purpose
Implements system suspend states: suspend-to-idle (`freeze`/s2idle), standby (`shallow`), and suspend-to-RAM (`mem`/`deep`). It registers platform suspend operations, exposes state labels, coordinates process freezing and device suspend phases, executes low-level platform entry, and resumes the system.

## Important APIs, Types, and Functions
Exported state includes `pm_labels`, `pm_states`, `mem_sleep_states`, `mem_sleep_current`, `mem_sleep_default`, `pm_suspend_target_state`, and `pm_suspend_global_flags`. Platform hooks are stored in `suspend_ops` and `s2idle_ops`. S2idle state uses `s2idle_state`, `s2idle_lock`, and `s2idle_wait_head`.

Important entry points are `pm_suspend_default_s2idle()`, `s2idle_set_ops()`, `s2idle_wake()`, `pm_states_init()`, `suspend_set_ops()`, `suspend_valid_only_mem()`, `suspend_devices_and_enter()`, and exported `pm_suspend()`. Weak architecture hooks are `arch_suspend_disable_irqs()` and `arch_suspend_enable_irqs()`.

## Control Flow
`pm_suspend()` validates the requested state, logs entry, calls `enter_state()`, records the result in suspend stats, and logs exit. `enter_state()` validates platform support, locks `system_transition_mutex`, initializes s2idle state if needed, optionally syncs filesystems, clears wakeup flags, runs `suspend_prepare()`, handles freezer test mode, and calls `suspend_devices_and_enter()`.

`suspend_prepare()` checks support, prepares the console, runs robust suspend notifiers, optionally freezes filesystems, and calls `suspend_freeze_processes()`. Failure records `SUSPEND_FREEZE`, thaws filesystems, posts notifiers, and restores the console.

`suspend_devices_and_enter()` sets the target state, begins platform suspend, suspends consoles, starts DPM suspend, and loops through `suspend_enter()` while platform `suspend_again()` requests another cycle. `suspend_enter()` runs platform prepare, late device suspend, s2idle-specific prepare, noirq device suspend, platform noirq prepare, and PM test checks. For s2idle it runs `s2idle_loop()` with devices suspended and CPUs idling until wake. For platform states it disables secondary CPUs, disables IRQs, sets `SYSTEM_SUSPEND`, suspends syscore, checks wakeups, calls `suspend_ops->enter()`, and unwinds syscore, IRQs, CPUs, platform, and DPM resume phases.

`s2idle_enter()` uses a raw spinlock to avoid losing wakeups between `pm_wakeup_pending()` and `s2idle_state` updates, wakes idle CPUs, and waits until `s2idle_wake()` transitions state to wake.

## State and Persistence Behavior
Suspend state is runtime-only. `mem_sleep_current` persists until changed by `/sys/power/mem_sleep` or boot `mem_sleep_default=`, influencing future `mem` requests. `pm_suspend_target_state` identifies the active transition to drivers. `pm_suspend_global_flags` can carry flags from platform/device code. Suspend statistics are updated in `main.c`.

## Dependencies and Integration Points
The file integrates with platform suspend ops, platform s2idle ops, DPM phases, syscore ops, CPU hotplug, cpuidle, console suspend, freezer/filesystem freeze, PM notifiers, wakeup sources, tracepoints, PM test/debug infrastructure, and `/sys/power/state`/`mem_sleep` dispatch from `main.c`.

## Risks
Risks include lost wakeups in s2idle, invalid platform callback ordering, not resuming devices after partial failures, IRQ state mismatches, CPU hotplug races, CXL memory restrictions for deep suspend, PM test modes unsupported for s2idle, and inconsistent `pm_suspend_target_state` cleanup. The nested unwind labels must preserve resume ordering after every failure point.

## Test Signals
Test `/sys/power/state` values `freeze`, `standby`, and `mem`; `/sys/power/mem_sleep` values `s2idle`, `shallow`, and `deep`; `mem_sleep_default=` boot parameter; PM test levels `freezer`, `devices`, `platform`, `processors`, and `core`; wakeup injection during late/noirq/syscore phases; platform `suspend_again()`; and failure injection in DPM/platform callbacks. Validate suspend_stats fields and tracepoints.
