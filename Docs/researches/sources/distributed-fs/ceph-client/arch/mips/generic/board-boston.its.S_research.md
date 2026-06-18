<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-boston.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-boston.its.S

**Purpose:** FIT image source fragment embedding the Boston board FDT.

**Important APIs/types/functions:** Defines `fdt-boston` with `/incbin/("boot/dts/img/boston.dtb")`, SHA1 hash, and `conf-boston` selecting `kernel` plus the Boston FDT.

**Control flow:** Build tooling preprocesses this into a FIT image; runtime bootloader chooses the configuration.

**State, dependencies, integration:** Depends on the built DTB path and the common `kernel` FIT image node.

**Risks and test signals:** DTB path or configuration name drift breaks FIT generation/boot selection. Test `make` FIT image generation with `FIT_IMAGE_FDT_BOSTON` and inspect `dumpimage` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-boston.its.S -->
