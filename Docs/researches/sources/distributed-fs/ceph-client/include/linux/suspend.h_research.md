<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/suspend.h -->
# sources/distributed-fs/ceph-client/include/linux/suspend.h

## Purpose

`suspend.h` is the central kernel header for system sleep, suspend-to-idle, and hibernation interfaces. It defines sleep-state constants, platform callback contracts, PM notification IDs, wakeup helpers, hibernation image helpers, and config-dependent stubs so callers can compile across PM configurations.

## Important APIs, types, and functions

Key types are `suspend_state_t`, `struct platform_suspend_ops`, `struct platform_s2idle_ops`, `struct pbe`, and `struct platform_hibernation_ops`. Public APIs include `suspend_set_ops()`, `pm_suspend()`, `s2idle_set_ops()`, `s2idle_wake()`, `hibernate()`, `hibernation_set_ops()`, `register_nosave_region()`, `swsusp_arch_suspend()`/`resume()`, PM notifier registration, wakeup event helpers, `lock_system_sleep()`, `pm_sleep_transition_in_progress()`, debug printing macros, autosleep work queuing, and suspend failure recording.

## Control flow

Suspend flow validates a target state, calls platform `begin`, suspends devices, invokes `prepare`/`prepare_late`, disables nonboot CPUs and IRQs as required, enters the platform state, then unwinds through `wake`, `finish`, device resume, and `end` or `recover`. S2idle uses a smaller callback set and a global `s2idle_state` checked by idle code. Hibernation flow shrinks/freezes, snapshots memory, writes or restores an image, and calls architecture/platform hooks across snapshot, enter, leave, and restore phases.

## State and persistence behavior

Global PM state includes `pm_suspend_target_state`, current/default mem sleep state, `pm_suspend_global_flags`, `s2idle_state`, wakeup counters, debug flags, hibernation hardware signature, and `restore_pblist`. Flags record whether firmware participates or platform power state remains under kernel control. Hibernation persists a memory image to storage; suspend state is mostly transient but hardware sleep state outlives CPU execution.

## Dependencies and integration points

The header depends on swap, notifiers, init, PM, MM, freezer, and arch errno. It integrates with device power management, freezer, CPU hotplug, wakeup source tracking, sysfs `/sys/power`, hibernation snapshot code, architecture suspend/resume code, consoles, VT, and PM debug.

## Risks and test signals

Risks include callback ordering violations, missing unwind callbacks after partial failures, using PM helpers when their config stubs return success/no-op, wakeup races, storage I/O under restricted GFP masks, and firmware/kernel ownership confusion. Tests should exercise suspend success and failure injection at each stage, s2idle wake behavior, hibernation snapshot/restore, PM notifier ordering, wakeup-count races, debug output gating, and builds with `CONFIG_SUSPEND`, `CONFIG_HIBERNATION`, and `CONFIG_PM_SLEEP` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/suspend.h -->
