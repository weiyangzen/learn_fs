<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-xilfpga.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-xilfpga.its.S

**Purpose:** FIT fragment embedding the MIPSfpga/Xilfpga Nexys4DDR FDT.

**Important APIs/types/functions:** Defines `fdt-xilfpga` from `boot/dts/xilfpga/nexys4ddr.dtb` and `conf-xilfpga`.

**Control flow:** Build-time FIT metadata only.

**State, dependencies, integration:** Used by `FIT_IMAGE_FDT_XILFPGA`.

**Risks and test signals:** Keep DTB path aligned with DTS build outputs. Test FIT generation and Xilfpga boot config selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-xilfpga.its.S -->
