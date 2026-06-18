<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackframe.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackframe.h

Purpose: defines LoongArch assembly macros for saving, restoring, and returning from exception/syscall frames.
Important APIs and types: macros include `SAVE_ALL`, `RESTORE_ALL_AND_RET`, `RESTORE_STATIC`, `RESTORE_SOME`, `RESTORE_SP_AND_RET`, `BACKUP_T0T1`, CFI helpers, and stack/thread pointer setup helpers.
Control flow: entry assembly uses these macros to build `pt_regs`, switch to kernel stacks, preserve callee/caller registers, restore CSR state, and return through `ertn` or equivalent sequences.
State and persistence: macros materialize transient trap state on the kernel stack and restore user/kernel register state after handlers finish.
Dependencies and integration: tied to `pt_regs`, `asm-offsets.c`, `thread_info.h`, `entry.S`, `genex.S`, KGDB/ftrace unwinding, and objtool unwind hints.
Risks and test signals: offset or CFI mistakes cause silent register corruption or bad unwinds. Signals include boot, syscall/interrupt storm tests, signal delivery, lockdep unwinds, KGDB, and objtool/build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackframe.h -->
