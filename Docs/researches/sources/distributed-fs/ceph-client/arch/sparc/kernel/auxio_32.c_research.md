<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_32.c

Purpose: Probes and controls SPARC32 auxiliary I/O and power-control registers.

Important APIs and control flow: `auxio_probe()` skips LEON/sun4d, finds `auxiliary-io` or `obio/auxio` PROM nodes, maps the register with OBIO ranges, applies sun4m address fixup, and turns on the LED bit. `get_auxio()` returns the byte register. `set_auxio()` spinlock-protects read/modify/write on sun4m and preserves `AUXIO_ORMEIN4M`; unsupported models panic if called. `auxio_power_probe()` finds `obio/power`, maps the power register, and reports power-off control availability.

State, dependencies, and risks: global `auxio_register` is exported for assembly floppy completion, and `auxio_power_register` is a volatile mapped pointer. Dependencies include PROM traversal, OBIO range translation, SBus byte I/O, CPU model selection, and `asm/auxio.h` masks. Risks include PROM node absence halting non-PCI systems, singleton global mapping, model-specific panic path, and address alignment fixups. Test signals are sun4m boot, LED set/clear, floppy interrupt paths using `auxio_register`, poweroff register discovery, and VME chassis without auxio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_32.c -->
