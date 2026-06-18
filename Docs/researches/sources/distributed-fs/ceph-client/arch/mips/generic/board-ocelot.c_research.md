<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.c

**Purpose:** Supports legacy Microsemi Ocelot boot without UHI/FIT-provided FDT.

**Important APIs/types/functions:** `ocelot_detect()` probes a RedBoot-created TLB mapping and chip ID, optionally copies bootloader command line, and returns board match. `ocelot_fixup_fdt()` installs `late_time_init` for early 8250 printk setup. `MIPS_MACHINE(ocelot)` registers built-in DTB, detect, and fixup hooks.

**Control flow:** Legacy generic boot calls detect functions; Ocelot checks TLB presence before reading chip ID. If matched, generic code uses the built-in DTB and later sets up early printk through `ioremap`.

**State, dependencies, integration:** Uses CP0 TLB probe registers, raw MMIO chip ID, `arcs_cmdline`, early printk setup, and `__dtb_ocelot_pcb123_begin`.

**Risks and test signals:** Assumes RedBoot TLB mapping is valid and firmware argv pointer shape is sane. Test no-TLB fallback, wrong part ID, command-line import, and early printk register mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.c -->
