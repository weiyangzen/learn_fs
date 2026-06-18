<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/vmlinux.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/vmlinux.its.S

**Purpose:** Base FIT image source for a generic MIPS kernel.

**Important APIs/types/functions:** Defines `/dts-v1/`, kernel image node with preprocessor-provided `KERNEL_NAME`, `VMLINUX_BINARY`, compression, load and entry addresses, and default configuration `conf-default`.

**Control flow:** Build tooling preprocesses constants and incbins the kernel binary into FIT metadata.

**State, dependencies, integration:** Board-specific ITS fragments add FDT configurations referencing the `kernel` node.

**Risks and test signals:** Incorrect address cell size or load/entry macros creates unbootable images. Test FIT generation for 32/64-bit address settings and compression variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/vmlinux.its.S -->
