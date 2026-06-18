<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/init.c

**Purpose:** Implements generic MIPS platform boot, FDT selection, FDT fixups, memory setup, device-tree init, time init, and IRQ init.

**Important APIs/types/functions:** `prom_init()`, `plat_get_fdt()`, `plat_fdt_relocated()`, `plat_mem_setup()`, `device_tree_init()`, `apply_mips_fdt_fixups()`, `plat_time_init()`, and `arch_init_irq()`.

**Control flow:** Boot obtains an FDT from appended/UHI/built-in sources or legacy machine detection. Memory setup applies machine fixups, initializes command line, and calls `__dt_setup_arch`. Device-tree init copies/unflattens the tree and chooses SMP ops. Time init derives counter frequency from a machine hook or CPU clock and then probes timers. IRQ init initializes CPU IRQs if needed and calls `irqchip_init()`.

**State, dependencies, integration:** Caches selected `fdt`, `mach`, and match data in initconst globals. Integrates `MIPS_MACHINE` descriptors, OF/libfdt, firmware args, CPS/vSMP/UP SMP ops, clock framework, and irqchip drivers.

**Risks and test signals:** Bad FDT handling can fail before console is stable; legacy detection requires exactly one matching machine in practice. Test UHI, appended DTB, built-in DTB, legacy board detection, relocation, fixup failure propagation, CPU clock fallback, and GIC/CPU IRQ combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/init.c -->
