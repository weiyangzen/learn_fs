# sources/distributed-fs/ceph-client/arch/mips/include/asm/pm.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pm.h

### Purpose
`pm.h` provides MIPS suspend/resume assembly macros and the minimal static CPU-state structure needed for suspend-to-RAM, especially when EVA segment registers must be restored before normal memory access is safe.

### Important APIs, Types, And Functions
Assembler macros include `SUSPEND_SAVE_REGS`, `RESUME_RESTORE_REGS_RETURN`, `LA_STATIC_SUSPEND`, `SUSPEND_SAVE_STATIC`, `RESUME_RESTORE_STATIC`, `SUSPEND_CACHE_FLUSH`, `SUSPEND_SAVE`, and `RESUME_RESTORE_RETURN`. The C-visible type is `struct mips_static_suspend_state`.

### Control Flow
Suspend assembly saves callee-preserved GPRs and CP0 status to a `pt_regs`-sized stack frame, stores early-restore state in `mips_static_suspend_state`, flushes caches to RAM, and later resumes by restoring EVA segment registers if present, reloading the stack pointer, restoring registers, and returning.

### State, Persistence, Dependencies, And Integration
State is volatile CPU register context, CP0 segment configuration, stack frame contents, and flushed cachelines in RAM. Dependencies include assembly offsets, MIPS register definitions, `regdef.h`, hazard macros, and `__flush_cache_all`. Integration is with platform suspend code and low-level resume entry points.

### Risks
The macros are context-sensitive assembly: wrong offsets, missing hazards after EVA register writes, or unflushed cache state can make resume fail before diagnostics are available. The saved static structure must be reachable under early segment mappings.

### Test Signals
Build both C and assembler users with and without `CONFIG_EVA`; run suspend-to-RAM/resume loops, verify CP0 status/segment restoration, and test with cache-disabled or memory-remapped resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pm.h -->
