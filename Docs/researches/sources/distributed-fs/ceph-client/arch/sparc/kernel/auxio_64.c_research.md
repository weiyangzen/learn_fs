<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_64.c

Purpose: SPARC64 platform driver for AUXIO LED and link-test enable controls on SBus/EBus systems.

Important APIs and control flow: `auxio_probe()` matches `auxio`, identifies parent bus as `ebus` or `sbus`, maps a 32-bit or 8-bit register, sets device type, and enables the EBus LED. `__auxio_rmw()` spinlock-protects register updates and uses readl/writel for EBus or SBus byte access for SBus. `auxio_set_led()` and `auxio_set_lte()` expose exported control functions; LTE only applies to SBus.

State, dependencies, and risks: state includes exported `auxio_register`, device type enum, and spinlock. Dependencies include OF platform resources, parent bus naming, `asm/auxio.h`, and platform-device ordering; `fs_initcall` ensures availability before device drivers such as floppy. Risks include singleton behavior when multiple auxio nodes exist, bus-type name assumptions, and EBus/SBus bit polarity differences. Test signals are OF auxio probe on both bus types, LED state changes, LTE no-op on EBus, and early consumers linking against exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_64.c -->
