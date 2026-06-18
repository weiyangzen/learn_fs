## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/device-init.c

### Purpose
`device-init.c` discovers PS3 hypervisor repository devices and registers Linux PS3 system-bus, storage, VUART, graphics, sound, LPM, and ramdisk devices, including a background storage probe thread.

### Important APIs, Types, And Functions
Key setup functions cover LPM, GELIC, USB EHCI/OHCI, VUART, storage, sound, graphics, ramdisk, dynamic/static repository devices, and `ps3_register_devices()`. Notification support uses `struct ps3_notification_device`, `ps3_notification_interrupt()`, `ps3_notification_read_write()`, `ps3_probe_thread()`, and reboot notifier `ps3_stop_probe_thread()`.

### Control Flow
The device initcall exits unless `FW_FEATURE_PS3_LV1` is present, starts a storage probe kthread, registers VUART/graphics/sound/LPM/ramdisk devices, and enumerates static SB devices. Storage notifications use a pseudo storage device, an event receive port, IRQ handler, and 512-byte command/event buffer. Each notification read can lead to repository lookup by bus/dev id and dynamic storage device registration.

### State, Persistence, And Dependencies
Allocated device layouts persist after successful registration and contain DMA/MMIO regions or storage region arrays. `probe_task` persists until reboot notifier stops it. Dependencies include LV1 storage calls, repository helpers, PS3 system bus registration, DMA/MMIO region init, interrupts, rcuwait, kthreads, and freezer support.

### Integration Points
The registered devices are consumed by PS3 GELIC, USB, storage, AV, sys-manager, sound, graphics, LPM, and ramdisk drivers.

### Risks
Failure paths rely on each setup function freeing only unregistered allocations. The async notification path must avoid tag mismatches and stop cleanly on reboot. Some repository devices can be inaccessible and are intentionally ignored.

### Test Signals
Boot enumeration logs, storage hot/late readiness, IRQ notification flow, kthread freezer/reboot stop, repository failure injection, and driver binding for each match id are key signals.
