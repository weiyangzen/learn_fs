<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-serval.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-serval.its.S

**Purpose:** FIT fragment for Microsemi Serval PCB105.

**Important APIs/types/functions:** Embeds `serval_pcb105.dtb` and defines `pcb105` configuration with kernel, FDT, and ramdisk.

**Control flow:** Build-time FIT metadata only.

**State, dependencies, integration:** Tied to `FIT_IMAGE_FDT_SERVAL` and common FIT nodes.

**Risks and test signals:** Missing ramdisk node or DTB path breaks image validation. Test FIT generation and bootloader config selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-serval.its.S -->
