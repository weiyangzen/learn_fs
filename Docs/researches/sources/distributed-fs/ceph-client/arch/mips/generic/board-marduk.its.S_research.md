<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-marduk.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-marduk.its.S

**Purpose:** FIT fragment embedding the IMG Pistachio Marduk/CI40 FDT.

**Important APIs/types/functions:** Defines `fdt-marduk` from `boot/dts/img/pistachio_marduk.dtb` and `conf-marduk`.

**Control flow:** Used by FIT image tooling; no kernel runtime code.

**State, dependencies, integration:** Depends on the DTB path and common kernel node.

**Risks and test signals:** Ensure configuration naming matches bootloader expectations. Test with `FIT_IMAGE_FDT_MARDUK` and inspect FIT contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-marduk.its.S -->
