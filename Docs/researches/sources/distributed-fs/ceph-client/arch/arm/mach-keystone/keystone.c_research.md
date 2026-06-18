# sources/distributed-fs/ceph-client/arch/arm/mach-keystone/keystone.c

Purpose: TI Keystone2 machine support for PM runtime clock domains, high-memory physical-to-virtual fixups, DMA offset handling, and DT machine selection.

Important APIs/types/functions: Defines `keystone_init()`, `keystone_pm_runtime_init()`, optional `keystone_platform_notifier()`, `keystone_pv_fixup()`, PM domain/notifier objects, compatible tables, and `DT_MACHINE_START(KEYSTONE, ...)`.

Control flow: Init optionally registers a platform bus notifier when LPAE boots from high memory, then installs a pm-clock notifier for matching Keystone SoCs. PV fixup inspects memblock DRAM: no-op for low 32-bit memory, rejects outside the 16G high window, otherwise sets `arch_phys_to_idmap_offset` and returns the high-to-low offset. The LPAE bus notifier assigns DMA offset to non-DT devices.

State and persistence: Global kernel state touched includes `arch_phys_to_idmap_offset`, platform bus notifiers, PM clock domain notifier, and optional DMA offsets on devices. Hardware state is indirect through runtime PM clock operations.

Dependencies and integration points: Depends on memblock, ARM idmap setup, platform bus notifier, DMA direct ops, PM runtime/pm-clock, OF matching, and DT roots for Keystone families.

Risks: High-memory boot depends on exact physical windows. Non-DT device DMA offset handling only applies on BUS_NOTIFY_ADD_DEVICE and logs as errors even on success. PM clock notifier is global once matching node exists.

Test signals: Boot Keystone with low and high DRAM maps, validate DMA for legacy and DT devices, runtime PM clock gating, and idmap correctness under LPAE.
