# sources/distributed-fs/ceph-client/net/netfilter/xt_IDLETIMER.c

Purpose: `IDLETIMER` target creates named sysfs-visible timers reset by matching packets, notifying userspace on expiry.

Important APIs/types/functions: `struct idletimer_tg`, create/check/destroy helpers for v0/v1, `idletimer_tg_target()`, `idletimer_tg_target_v1()`, sysfs show, timer/alarm callbacks, and work notifier.

Control flow: module init creates class/device and registers targets. Check validates label/timeout/type, reuses existing timer by label or creates sysfs attr and timer/alarm. Runtime resets expiration. Expiry schedules work for `sysfs_notify()`. Destroy refcounts shared timers and cancels timer/alarm/work before freeing.

State and persistence: global timer list, sysfs files, class/device, timers/alarms, work items, and refcounts. Dependencies include x_tables, sysfs/kobject, timer, alarmtimer, workqueue, mutexes, and `xt_check_proc_name()`. Risks: shared-label refcounting, timer/work teardown races, reserved sysfs names, type mismatch, and unsupported netlink message option. Test signals: v0/v1 timers, alarm mode, shared label, sysfs reads, expiry notification, invalid labels/timeouts/types, and unload cleanup.
