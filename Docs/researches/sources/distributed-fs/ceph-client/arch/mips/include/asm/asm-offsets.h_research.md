<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-offsets.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-offsets.h

**Purpose:** Provides the standard include point for generated MIPS assembly offsets.

**Important APIs/types/functions:** Includes `<generated/asm-offsets.h>`.

**Control flow:** No local logic; build-generated constants are made visible to assembly and C headers.

**State, dependencies, integration:** Required by assembler macros that use structure offsets such as `THREAD_FPR*` and `THREAD_REG*`.

**Risks and test signals:** Generated offsets must match compiled C structures. Test by rebuilding after structure changes and compiling assembly users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-offsets.h -->
