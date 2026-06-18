# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.c

Purpose: shared pvpanic core that registers pvpanic instances, exposes capability/event sysfs controls, and sends panic/crash-loaded/shutdown events to hypervisor-visible IO/MMIO registers.

Important APIs and types: `struct pvpanic_instance` stores base register, capability mask, enabled events, optional sys_off handler, and list node. Exported APIs are `devm_pvpanic_probe()` and `pvpanic_dev_groups`. Core helpers include `pvpanic_send_event()`, panic notifier `pvpanic_panic_notify()`, `pvpanic_sys_off()`, `pvpanic_synchronize_sys_off_handler()`, sysfs show/store functions, and `pvpanic_remove()`.

Control flow: module init initializes the global list/spinlock and registers a high-priority panic notifier. Probe reads device-supported events from `ioread8(base)` masked by known bits, enables all supported events by default, conditionally registers a low-priority poweroff sys_off handler, adds the instance to a spinlocked global list, stores drvdata, and registers a devm cleanup action. Panic notification sends `PVPANIC_CRASH_LOADED` if a crash kernel is loaded, else `PVPANIC_PANICKED`. Shutdown sends `PVPANIC_SHUTDOWN`. The `events` sysfs store validates the requested mask against capability and toggles sys_off registration.

State and persistence: global in-memory instance list and per-device enabled event masks. Writes to the hypervisor register are transient event notifications. Sysfs `events` changes persist only until device/module lifetime ends.

Dependencies and integration points: depends on `uapi/misc/pvpanic.h`, panic notifier chain, kexec crash state, sys_off API, MMIO accessors, and the PCI/MMIO transport front ends.

Risks and test signals: `pvpanic_send_event()` uses `spin_trylock()` and silently drops events if contended, which is intentional for panic paths but should be understood. The expression in `pvpanic_synchronize_sys_off_handler()` is subtle; tests should cover enabling/disabling shutdown via sysfs. Event writes occur during panic context, so avoid sleeping and validate with QEMU host-side event observation, crash-kernel loaded/unloaded cases, multiple devices, and removal while sys_off is registered.
