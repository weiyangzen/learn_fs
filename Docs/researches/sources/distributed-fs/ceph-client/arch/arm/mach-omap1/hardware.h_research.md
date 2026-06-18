<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/hardware.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/hardware.h

Purpose: Legacy OMAP1 hardware-address header. It defines memory controller, chip-select, peripheral, and compatibility constants used by board and platform code.

Important APIs/types/functions: Important helpers/macros include `omap_cs0m_phys`, `omap_cs3_phys`, OMAP chip-select bases, register base constants, and included SoC/IO headers.

Control flow, state, and persistence: There is no mutable state; inline helpers derive physical addresses from TC/EMIFS register settings.

Dependencies and integration points: Important helpers/macros include `omap_cs0m_phys`, `omap_cs3_phys`, OMAP chip-select bases, register base constants, and included SoC/IO headers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are hard-coded physical address assumptions and broad inclusion of legacy definitions into board drivers. Test board flash/CF mappings, chip-select helpers, and compile coverage across OMAP15xx/16xx.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 235 lines, 8575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/hardware.h -->
