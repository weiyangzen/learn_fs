<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-jaguar2.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-jaguar2.its.S

**Purpose:** FIT fragment for Microsemi Jaguar2 PCB110 and PCB111 boards.

**Important APIs/types/functions:** Embeds `jaguar2_pcb110.dtb` and `jaguar2_pcb111.dtb`, each with SHA1 hashes, and defines configurations `pcb110` and `pcb111` using kernel, matching FDT, and `ramdisk`.

**Control flow:** Build creates FIT nodes; bootloader selects the board-specific config.

**State, dependencies, integration:** Depends on MSCC DTBs and common FIT kernel/ramdisk nodes.

**Risks and test signals:** Missing ramdisk node or DTB path breaks config validation. Test FIT build and bootloader selection for both PCB variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-jaguar2.its.S -->
