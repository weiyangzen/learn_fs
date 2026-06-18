<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ingenic.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ingenic.c

**Purpose:** Provides generic machine support for Ingenic SoCs.

**Important APIs/types/functions:** `ingenic_of_match[]` maps compatible strings to `MACH_INGENIC_*` IDs. `ingenic_fixup_fdt()` sets `mips_machtype`, `system_type`, adds legacy qi,lb60 memory if missing, and adjusts external oscillator dividers. `MIPS_MACHINE(ingenic)` registers the machine. Late PM init installs suspend/halt support for XBurst.

**Control flow:** Generic FDT selection matches root compatible, runs fixup, potentially writes CGU CPCCR bits for 12 MHz external clock, then later installs wait-based halt/suspend.

**State, dependencies, integration:** Uses FDT APIs, raw MMIO ioremap, bootinfo mach types, `system_type`, and platform PM hooks.

**Risks and test signals:** Direct CGU writes are SoC-specific and happen very early; wrong compatible data mislabels the platform. Test all compatible mappings, qi,lb60 missing memory fallback, 12/24 MHz oscillator behavior, and XBurst suspend/halt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ingenic.c -->
