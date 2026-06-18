# sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_fpu.c

Purpose: Provides guarded kernel-mode floating-point access helpers for RISC-V.

Important APIs/types/functions: Implements `kernel_fpu_begin()` and `kernel_fpu_end()` or equivalent wrappers around preemption and FP status management.

Control flow: Callers enter a short critical section, save/disable preemption as required, enable FP state for kernel use, perform FP operations, then restore status and preemption state.

State and persistence: Temporarily mutates CPU status FS bits and per-task FP ownership state; no file-local persistent state.

Dependencies and integration points: Depends on FPU assembly save/restore, `switch_to`, preemption control, and cryptographic or math code that uses kernel FP.

Risks and test signals: Kernel FP use across preemption or interrupt boundaries can corrupt user FP state. Test with preemptible kernels, FP-heavy user workloads, kernel FP callers, and lockdep/preempt debug.
