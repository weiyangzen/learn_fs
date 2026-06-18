<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/asm-offsets.c

Purpose: emits C-verified structure offsets for LoongArch assembly code.
Important APIs and types: uses `DEFINE`/`OFFSET` macros for `pt_regs`, `thread_info`, `thread_struct`, CPU boot data, FPU/vector state, sigcontext, and other low-level structures.
Control flow: built during kernel compilation to generate `asm-offsets.h`; no runtime code is linked.
State and persistence: generated constants persist in build artifacts and keep assembly synchronized with C layout.
Dependencies and integration: consumed by `entry.S`, `stackframe.h`, `switch.S`, `fpu.S`, signal code, suspend, and low-level boot paths.
Risks and test signals: missing offsets cause assembly to read/write wrong fields. Signals are build success and runtime tests for syscall entry, context switch, signal restore, FPU save/restore, and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/asm-offsets.c -->
