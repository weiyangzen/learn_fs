# sources/distributed-fs/ceph-client/include/linux/pm_wakeup.h

Purpose: defines the device wakeup-source interface used to mark devices as wake-capable, enable or disable system wakeup, account wake events, and prevent autosleep while events are active.

Important APIs and types: `struct wakeup_source` records name/id, list linkage, spinlock, optional `wake_irq`, timer, active/prevent-sleep timing, event/active/relax/expire/wakeup counters, sysfs device, active flag, and autosleep flag. Helpers expose `device_can_wakeup()`, `device_may_wakeup()`, wakeup-path and out-of-band flags, wakeup source register/unregister/walk, `device_wakeup_enable/disable()`, `device_set_wakeup_capable()`, `__pm_stay_awake()`, `pm_stay_awake()`, `__pm_relax()`, and wakeup event helpers including hard events and `devm_device_init_wakeup()`.

Control flow: drivers mark wake-capable devices, optionally enable wakeup by default, call stay-awake or wakeup-event helpers when hardware reports activity, and relax once work is drained. The PM core uses the wakeup-source active state and wakeup path flags to abort or shape suspend/autosleep transitions. `device_init_wakeup()` combines capability and enable state; the devm wrapper installs a cleanup action.

State and persistence: runtime state is held in `dev->power` and `struct wakeup_source`: wake enablement, path markers, event counters, timers, and aggregate active/prevent-sleep time. No persistent storage is used.

Dependencies and integration points: included via `device.h`, and integrates with PM sleep, wake IRQs, timers, spinlocks, wakeup-source sysfs statistics, autosleep, and device-managed actions. Without `CONFIG_PM_SLEEP`, wakeup-source allocation and event accounting are no-ops, but basic capability/should-wakeup booleans remain available.

Risks and test signals: risks include not relaxing active wakeup sources, enabling wakeup for devices that cannot signal wake, racing event timers with suspend entry, missing hard wakeup events, and code assuming wakeup-source statistics exist in no-sleep builds. Test wakeup enable/disable sysfs, autosleep aborts, timed events, hard wake events, devm cleanup, wake IRQ association, and disabled sleep configurations.
