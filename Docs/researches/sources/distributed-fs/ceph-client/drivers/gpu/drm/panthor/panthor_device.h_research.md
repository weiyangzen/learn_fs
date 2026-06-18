# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.h

`panthor_device.h` defines the central Panthor device and file-private state, PM/reset/IRQ enums, common IRQ boilerplate, exception codes, MMIO helpers, and lifecycle prototypes.

Key definitions are `struct panthor_soc_data`, `enum panthor_device_pm_state`, `enum panthor_irq_state`, `struct panthor_irq`, profiling flags, `struct panthor_device`, `struct panthor_gpu_usage`, and `struct panthor_file`. It declares init/unplug/mmap/PM and exception APIs. Inline helpers schedule resets, check pending reset, recover runtime PM after failed resume, classify exceptions, perform 32/64-bit MMIO access, read stable 64-bit counters, and poll MMIO. `PANTHOR_IRQ_HANDLER()` generates raw and threaded IRQ handlers, suspend/resume, and mask update helpers.

The IRQ macro's flow is raw status check, ACTIVE-to-PROCESSING transition, mask interrupts, threaded drain through subsystem callback, then PROCESSING-to-ACTIVE and mask restore. Device/file structs persist DRM base, SoC data, clocks, MMIO, subsystem pointers, PM mapping state, reset work, VM/group pools, user MMIO offset, and stats.

Dependencies include DRM core, scheduler, io-pgtable, runtime PM, Panthor uAPI, and low-level registers. Risks are broad because most subsystems include this header: IRQ mask ordering, user-controlled MMIO offsets, PM recovery atomics, and structure layout changes. Tests should stress shared IRQs, suspend/resume, 32-bit mmap offsets, reset scheduling, and exception reporting.
