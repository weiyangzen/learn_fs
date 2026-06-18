<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compiler.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/compiler.h

**Purpose:** Provides MIPS compiler workarounds, inline-asm constraints, and ISA level strings.

**Important APIs/types/functions:** Overrides `barrier_before_unreachable()` with `.insn`, defines `GCC_OFF_SMALL_ASM()`, `MIPS_ISA_LEVEL`, `MIPS_ISA_ARCH_LEVEL`, and raw ISA tokens for MIPSR6/R5/default R2 builds.

**Control flow:** Compile-time selection handles GCC unreachable delay-slot bugs and suboptimal noreturn stack behavior.

**State, dependencies, integration:** Used by inline assembly across atomics, bitops, cmpxchg, and generated code.

**Risks and test signals:** Changing constraints or ISA strings can break assembler acceptance or code scheduling. Test affected GCC versions, microMIPS link requirements, and inline asm builds for R5/R6/default configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compiler.h -->
