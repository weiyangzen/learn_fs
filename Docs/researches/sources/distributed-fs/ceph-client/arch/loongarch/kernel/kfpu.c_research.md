<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kfpu.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kfpu.c

Purpose: provides kernel-mode FPU/vector usage helpers for LoongArch.
Important APIs and types: implements save/restore wrappers that allow kernel code to borrow FPU/LSX/LASX state safely, along with begin/end style APIs.
Control flow: callers disable preemption or otherwise guard ownership, save current task FPU state if needed, enable FPU/vector units, perform work, then restore previous state and permissions.
State and persistence: temporarily stores task FPU/vector state and updates ownership/lazy flags.
Dependencies and integration: depends on low-level `fpu.S` routines, CPU feature bits, scheduler/preemption, and crypto/math code that uses kernel FPU.
Risks and test signals: incorrect nesting or preemption handling corrupts userspace FPU state. Signals include crypto selftests using vector code, preemption stress, FPU signal tests, and KCSAN/lockdep around kernel FPU regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kfpu.c -->
