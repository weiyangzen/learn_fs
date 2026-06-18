<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ni169445.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ni169445.its.S

**Purpose:** FIT fragment embedding the National Instruments 169445 FDT.

**Important APIs/types/functions:** Defines `fdt-ni169445` from `boot/dts/ni/169445.dtb` and `conf-ni169445`.

**Control flow:** Build-time image metadata only.

**State, dependencies, integration:** Tied to `FIT_IMAGE_FDT_NI169445`.

**Risks and test signals:** DTB path and board description must stay aligned with device tree sources. Test FIT generation and board boot config lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ni169445.its.S -->
