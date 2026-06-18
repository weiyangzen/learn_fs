<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.its.S

**Purpose:** FIT fragment for Microsemi Ocelot PCB123 and PCB120 boards.

**Important APIs/types/functions:** Embeds `ocelot_pcb123.dtb` and `ocelot_pcb120.dtb`, with configurations `conf-ocelot_pcb123` and `conf-ocelot_pcb120`.

**Control flow:** Build-time FIT metadata, selected by bootloader.

**State, dependencies, integration:** Used when booting Ocelot with U-Boot/FIT rather than legacy RedBoot path.

**Risks and test signals:** FIT and legacy Ocelot paths must use compatible DTBs. Test both PCB configurations in generated FIT output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.its.S -->
