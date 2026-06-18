# sources/distributed-fs/ceph-client/arch/sh/drivers/push-switch.c



Source read size: 135 lines, 3012 bytes.



Purpose: small platform-driver framework for board push switches with debounce timer, workqueue notification, and optional sysfs name exposure.

Important APIs/types/functions: `switch_drv_probe()`, `switch_drv_remove()`, `switch_timer()`, `switch_work_handler()`, read-only `switch` attribute, `struct push_switch`, and `struct push_switch_platform_info`.

Control flow: probe allocates state, fetches the platform IRQ, requests the board-provided IRQ handler, creates the name attribute when present, initializes work and debounce timer, and stores drvdata. Timer schedules work; work clears state and emits `KOBJ_CHANGE`. Remove tears down attribute, timer, work, IRQ, and allocation.

State and persistence: per-device state, debounce timer, work item, IRQ registration, and sysfs attribute persist while bound.

Dependencies and integration points: depends on board-supplied platform data and IRQ handler, platform bus, sysfs, workqueues, timers, and uevent consumers.

Risks and test signals: `BUG_ON(!platform_data)` makes bad board data fatal; state clearing is generic while actual IRQ handler is external; debounce scheduling is platform-specific. Test IRQ firing, debounce timer behavior, uevents, sysfs attribute, and remove while work is pending.
