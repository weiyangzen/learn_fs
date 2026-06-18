# sources/distributed-fs/ceph-client/drivers/base/power/sysfs.c

## Purpose
This file exposes device power-management state and policy through per-device sysfs `power/` attributes. It bridges user-visible policy controls to runtime PM, wakeup-source configuration, PM QoS constraints, wakeup statistics, async system sleep configuration, and advanced runtime PM debugging attributes.

## Important APIs, Types, And Functions
The exported setup/removal functions are `dpm_sysfs_add()`, `dpm_sysfs_change_owner()`, `wakeup_sysfs_add()`, `wakeup_sysfs_remove()`, `pm_qos_sysfs_add_*()`, `pm_qos_sysfs_remove_*()`, `rpm_sysfs_remove()`, and `dpm_sysfs_remove()`. Attribute handlers include `control_show/store`, `runtime_status_show`, runtime active/suspended time, `autosuspend_delay_ms`, PM QoS resume latency, latency tolerance, no-power-off flag, wakeup enable/disable, wakeup counters/timers, `runtime_usage`, `runtime_active_kids`, `runtime_enabled`, and `async`.

## Control Flow And State
`dpm_sysfs_add()` creates the base `power` group, merges runtime attributes unless callbacks are suppressed, merges wakeup attributes when the device is wake-capable, merges latency tolerance attributes when supported, and adds wakeup-source stats if needed. Error paths unmerge groups in reverse order. Store handlers parse sysfs text with `sysfs_streq()` or `kstrto*()`, then call core helpers such as `pm_runtime_allow()`, `pm_runtime_forbid()`, `pm_runtime_set_autosuspend_delay()`, `device_set_wakeup_enable()`, and PM QoS update APIs.

Wakeup statistic reads take `dev->power.lock` before dereferencing `dev->power.wakeup`; if no wakeup source is attached they emit a blank line. Runtime status maps internal states to `active`, `suspended`, `suspending`, `resuming`, `unsupported`, or `error`.

## Dependencies And Integration Points
This file depends on sysfs/kobject APIs, runtime PM, wakeup framework functions from `wakeup.c`, PM QoS, and optional config blocks: `CONFIG_PM_SLEEP`, `CONFIG_PM_AUTOSLEEP`, and `CONFIG_PM_ADVANCED_DEBUG`. It is called from device registration/removal and wakeup capability transitions.

## Risks And Test Signals
Risks include partial sysfs group creation failure, stale wakeup-source pointers, invalid user input handling, owner-change mismatches, and incorrect visibility when `pm_runtime_no_callbacks()` removes runtime attributes. Test signals include sysfs read/write tests for `power/control`, wakeup enable toggles, autosuspend delay parsing, PM QoS special values (`n/a`, `auto`, `any`), group cleanup on simulated failure, and uevent emission on wakeup attribute changes.
