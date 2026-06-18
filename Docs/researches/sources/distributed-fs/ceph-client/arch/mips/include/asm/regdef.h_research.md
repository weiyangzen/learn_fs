# sources/distributed-fs/ceph-client/arch/mips/include/asm/regdef.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/regdef.h

### Purpose
`regdef.h` defines symbolic MIPS general-purpose register numbers and assembler register aliases for ABI32, NABI32, and ABI64 code.

### Important APIs, Types, And Functions
Numeric macros include `GPR_ZERO`, `GPR_AT`, `GPR_V0`, argument registers, temporaries, saved registers, `GPR_GP`, `GPR_SP`, `GPR_FP`, and `GPR_RA`. Under `__ASSEMBLER__`, it defines names such as `zero`, `AT`, `v0`, `a0`, `t0`, `s0`, `gp`, `sp`, `fp`, `s8`, and `ra`, with ABI-dependent argument/temporary mappings.

### Control Flow
There is no runtime flow. Assembly files expand these aliases when assembled for the selected `_MIPS_SIM`.

### State, Persistence, Dependencies, And Integration
No runtime state exists. Dependency is `asm/sgidefs.h` for ABI selection. Integration is broad across hand-written MIPS assembly, low-level entry code, suspend macros, and firmware call glue.

### Risks
ABI-specific alias differences are subtle: N32/N64 have more argument registers and different temporary naming than O32. A wrong alias can corrupt calling convention state in assembly.

### Test Signals
Assemble O32, N32, and N64 kernel/firmware assembly users; inspect generated code for argument/saved register use; run syscall, exception, and suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/regdef.h -->
