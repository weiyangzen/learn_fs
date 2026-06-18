<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/switch_to.h

Purpose: declares LoongArch task-switch helpers and lazy FPU/vector context management hooks.
Important APIs and types: exposes `__switch_to`, `resume`, and macros/helpers to save or restore FPU, LSX, LASX, LBT, and hardware breakpoint state during context switches.
Control flow: scheduler calls the assembly/C switch path; lazy state helpers decide whether current task vector/FPU state needs saving and next task state needs restoring or enabling.
State and persistence: per-task `thread_struct` fields persist callee-saved registers and optional accelerator/debug state across scheduling.
Dependencies and integration: depends on processor/thread layout, FPU/LBT headers, hardware breakpoints, and `kernel/switch.S` plus `asm-offsets.c`.
Risks and test signals: stale lazy state leaks register contents across tasks or corrupts computation. Signals include context-switch stress, FPU/vector tests, ptrace over switched tasks, and hardware breakpoint switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/switch_to.h -->
