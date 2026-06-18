<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-prototypes.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-prototypes.h

**Purpose:** Collects C prototypes needed by MIPS assembly files and modversion generation.

**Important APIs/types/functions:** Includes checksum, page, FPU, generic asm prototypes, uaccess, ftrace, and mmu context headers. Declares `clear_page_cpu()` and `copy_page_cpu()`.

**Control flow:** Header-only declarations.

**State, dependencies, integration:** Bridges assembly implementations with C symbol prototypes and modversions.

**Risks and test signals:** Missing prototypes can break CFI/modversions or hide ABI mismatches. Test allmodconfig builds and symbol version generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-prototypes.h -->
