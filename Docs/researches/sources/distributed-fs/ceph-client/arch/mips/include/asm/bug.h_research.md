<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bug.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bug.h

**Purpose:** Provides MIPS-specific `BUG()` and optimized `BUG_ON()` implementations.

**Important APIs/types/functions:** `BUG()` emits `break BRK_BUG` and marks unreachable. For ISA greater than MIPS1, `__BUG_ON()` uses constant folding or `tne` trap with `BRK_BUG`.

**Control flow:** Compile-time config `CONFIG_BUG` enables arch trap implementations before including generic bug support.

**State, dependencies, integration:** Used by kernel assertions and trap handling.

**Risks and test signals:** Trap code must match exception decoding and must not be emitted on unsupported ISA. Test BUG/BUG_ON disassembly and runtime trap reporting on MIPS1 and newer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bug.h -->
