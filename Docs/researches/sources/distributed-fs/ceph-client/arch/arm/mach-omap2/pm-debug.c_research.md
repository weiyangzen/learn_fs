# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-debug.c

## Purpose
`pm-debug.c` exposes debugfs instrumentation for OMAP power management. It reports powerdomain state counters, time spent in states, clockdomain usecounts, per-powerdomain suspend targets, and global off-mode control.

## Important APIs, Types, and Functions
Key functions are `pm_dbg_update_time()`, `pm_dbg_counters_show()`, `pm_dbg_timers_show()`, `pwrdm_suspend_get()`, `pwrdm_suspend_set()`, `option_get()`, `option_set()`, and `pm_dbg_init()`. It uses debugfs show helpers, `pwrdm_for_each()`, `clkdm_for_each()`, `omap3_pm_get_suspend_state()`, and `omap3_pm_set_suspend_state()`.

## Control Flow
When `CONFIG_DEBUG_FS` is enabled, `omap_arch_initcall(pm_dbg_init)` creates `/sys/kernel/debug/pm_debug`. It installs `count`, `time`, `enable_off_mode`, and per-powerdomain `suspend` files. Powerdomain transitions call `pm_dbg_update_time()` to accumulate timers after init completes.

## State and Persistence Behavior
Debug state lives in `pm_dbg_init_done`, `enable_off_mode`, and per-powerdomain counters/timers embedded in `struct powerdomain`. Writing `enable_off_mode` can immediately reprogram OMAP3 suspend targets.

## Dependencies and Integration Points
It depends on debugfs, seq_file, scheduler clock, clockdomain and powerdomain frameworks, OMAP SoC detection, and OMAP3 PM suspend-state APIs.

## Risks
Debugfs writes can change suspend behavior on live systems. Timer accounting assumes valid previous state indexes. Calling `pwrdm_state_switch()` from debug display can perturb transition bookkeeping.

## Test Signals
With `CONFIG_PM_DEBUG` and `CONFIG_DEBUG_FS`, mount debugfs and read `pm_debug/count` and `pm_debug/time` before and after idle/suspend. Change OMAP3 per-domain `suspend` and `enable_off_mode` values and verify expected PM behavior without state mismatch warnings.
