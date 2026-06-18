# sources/distributed-fs/ceph-client/kernel/power/main.c

## Purpose
Provides the PM subsystem core sysfs/debugfs surface and shared helpers used by suspend and hibernation. It owns `/sys/power`, common sleep-state dispatch, wakeup-count handshake, PM notifiers, suspend statistics, PM workqueues, debug toggles, and filesystem sync helpers.

## Important APIs, Types, and Functions
Exported helpers include `lock_system_sleep()`, `unlock_system_sleep()`, `ksys_sync_helper()`, `register_pm_notifier()`, `unregister_pm_notifier()`, `pm_notifier_call_chain_robust()`, `pm_notifier_call_chain()`, `pm_report_hw_sleep_time()`, `pm_report_max_hw_sleep()`, `pm_sleep_transition_in_progress()`, `pm_debug_messages_should_print()`, and exported workqueue `pm_wq`.

State includes `saved_gfp_count`, `saved_gfp_mask`, `pm_fs_sync_count`, `pm_fs_sync_wq`, `pm_chain_head`, `pm_async_enabled`, `sync_on_suspend_enabled`, `pm_test_level`, `suspend_stats`, `pm_print_times_enabled`, `pm_debug_messages_on`, `power_kobj`, `filesystem_freeze_enabled`, and the PM kobjects/attribute groups. `struct suspend_stats` records success/fail counts, per-step failures, recent failed devices/errno/steps, and hardware sleep time.

Sysfs attributes include `state`, `pm_async`, `mem_sleep`, `sync_on_suspend`, `pm_test`, `wakeup_count`, `autosleep`, `wake_lock`, `wake_unlock`, `pm_trace`, `pm_trace_dev_match`, `pm_freeze_timeout`, `freeze_filesystems`, `pm_print_times`, `pm_wakeup_irq`, `pm_debug_messages`, and `suspend_stats/*`.

## Control Flow
`pm_init()` is a core initcall that allocates `pm_wq` and `pm_fs_sync_wq`, initializes hibernation image/reserved sizes, initializes suspend state labels, creates `/sys/power`, installs attribute groups, initializes PM debug timing, and initializes autosleep.

Writing `/sys/power/state` enters `state_store()`: it locks autosleep, rejects manual writes while autosleep is active, decodes labels, maps `mem` to `mem_sleep_current`, and dispatches to `pm_suspend()` or `hibernate()`. Writing `/sys/power/mem_sleep` updates the selected `mem` implementation when autosleep is not active. Writing `/sys/power/wakeup_count` implements the race-free wakeup-event protocol by saving the observed wakeup count or printing active wakeup sources.

`pm_sleep_fs_sync()` runs `ksys_sync()` on an ordered workqueue and waits in short intervals so wakeup events can abort a suspend or hibernate attempt with `-EBUSY`. `pm_restrict_gfp_mask()` and `pm_restore_gfp_mask()` maintain a nesting count while clearing `__GFP_IO` and `__GFP_FS` under `system_transition_mutex`, preventing allocations that require I/O while devices are suspended.

Suspend statistics are updated by DPM and suspend paths through `dpm_save_failed_dev()`, `dpm_save_failed_step()`, and `dpm_save_errno()`. Sysfs and debugfs readers expose the current ring-buffered failure details.

## State and Persistence
Most state is runtime-only kernel state exposed through sysfs/debugfs. Sysfs writes persist only until reboot unless boot parameters set defaults. `pm_async_enabled`, `sync_on_suspend_enabled`, `pm_test_level`, `freeze_timeout_msecs`, and `filesystem_freeze_enabled` directly affect later suspend/hibernate behavior. `suspend_stats` persists in memory across multiple transitions and is observable under `/sys/power/suspend_stats` and debugfs.

## Dependencies and Integration Points
This file binds the PM core to sysfs/kobject infrastructure, debugfs/seq_file, workqueues, system calls (`ksys_sync`), wakeup-source accounting, autosleep, wakelocks, PM trace, ACPI low-power S0 reporting, freezer timeout configuration, PM notifier chains, hibernation, and suspend. It is the public user-space control plane for the rest of `kernel/power`.

## Risks
Risks include incorrect serialization around `system_transition_mutex`, wakeup-count races causing lost wakeups or unnecessary suspend failures, failure to restore `gfp_allowed_mask`, sysfs stores accepting invalid states while autosleep is active, statistics updates without sufficient locking for all fields, and initialization ordering problems because later hibernation/suspend files add sysfs groups under `power_kobj`.

## Test Signals
Check `/sys/power/state`, `mem_sleep`, `wakeup_count`, `autosleep`, `pm_async`, `sync_on_suspend`, `pm_test`, `freeze_filesystems`, and debug attributes under supported configs. Race tests should read/write `wakeup_count` while generating wakeup events, toggle autosleep while writing state attributes, inject filesystem sync wakeups, verify suspend-stat counters after failed DPM steps, and boot with `pm_async=off` or `pm_debug_messages`.
