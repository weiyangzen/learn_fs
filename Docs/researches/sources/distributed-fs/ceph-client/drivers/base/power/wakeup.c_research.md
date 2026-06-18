# sources/distributed-fs/ceph-client/drivers/base/power/wakeup.c

## Purpose
This file implements the system wakeup event framework. It registers and tracks wakeup sources, attaches them to devices, manages wakeup IRQ arming, maintains global wakeup event counters used to abort suspend, provides stay-awake/relax event APIs, and exposes aggregate wakeup-source statistics through debugfs.

## Important APIs, Types, And Functions
Exports include wakeup source lifecycle (`wakeup_source_register()`, `wakeup_source_unregister()`), list traversal (`wakeup_sources_read_lock()`, `wakeup_sources_walk_start()`, `wakeup_sources_walk_next()`), device policy (`device_wakeup_enable()`, `device_wakeup_disable()`, `device_set_wakeup_capable()`, `device_set_wakeup_enable()`), wake IRQ attachment and arming, event APIs (`__pm_stay_awake()`, `pm_stay_awake()`, `__pm_relax()`, `pm_relax()`, `pm_wakeup_ws_event()`, `pm_wakeup_dev_event()`), suspend-abort APIs (`pm_wakeup_pending()`, `pm_system_wakeup()`, `pm_system_cancel_wakeup()`, `pm_wakeup_clear()`, `pm_system_irq_wakeup()`, `pm_wakeup_irq()`), and wakeup-count APIs (`pm_get_wakeup_count()`, `pm_save_wakeup_count()`).

## Control Flow And State
Global state includes `events_check_enabled`, two recorded wakeup IRQ slots, `pm_abort_suspend`, `combined_event_count`, `saved_count`, `events_lock`, `wakeup_sources`, `wakeup_count_wait_queue`, `wakeup_srcu`, deleted-source aggregate stats, and `wakeup_ida`. A wakeup source has a spinlock, timer, active flag, event counters, timing totals, autosleep fields, optional sysfs device, and optional wake IRQ.

Activation increments active/event accounting and the low bits of `combined_event_count`; deactivation updates total/max/prevent-sleep time and atomically increments the registered-event count while decrementing in-progress count. `pm_save_wakeup_count()` snapshots the registered count and enables checking only if nothing is in progress. `pm_wakeup_pending()` compares the current count/in-progress pair to the saved value and disables checking after a detected wakeup. Timed events use `pm_wakeup_timer_fn()` to relax a source after a requested processing window.

## Dependencies And Integration Points
The file integrates with device sysfs (`wakeup_sysfs_add/remove()` and `wakeup_source_sysfs_add/remove()`), wake IRQ helpers, suspend core (`s2idle_wake()` and wakeup count protocol), debugfs, SRCU-protected list traversal, timers, tracepoints from `trace/events/power.h`, and device registration state.

## Risks And Test Signals
Risks include leaked wakeup sources, stale wake IRQ pointers, wrong SRCU/list locking, timer races around relax/activate, overflow of packed event counters, suspend abort false positives/negatives, and missing wakeup sysfs on capability changes. Test signals include wakeup_count protocol tests, suspend aborts from `pm_wakeup_event()`, debugfs `wakeup_sources` totals, active-source logging, deleted-source accounting, wake IRQ arm/disarm behavior, and stress with concurrent IRQ events and unregister.
