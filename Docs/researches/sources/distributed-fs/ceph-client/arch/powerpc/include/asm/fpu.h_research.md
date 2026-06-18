## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fpu.h

Purpose: exposes safe kernel FPU usage helpers for PowerPC.

Important APIs/types/functions: `kernel_fpu_available()`, `kernel_fpu_begin()`, and `kernel_fpu_end()`.

Control flow: availability checks that the CPU does not advertise `CPU_FTR_FPU_UNAVAILABLE`. Begin disables preemption and enables kernel FP state; end disables kernel FP and reenables preemption.

State and persistence: manipulates per-CPU/thread floating-point ownership and preemption state through `enable_kernel_fp()` and `disable_kernel_fp()`.

Dependencies and integration: depends on CPU feature checks, preemption control, and switch-to/FPU state management. Used by kernel code that needs floating-point operations without corrupting userspace FP state.

Risks and test signals: missing `kernel_fpu_end()` leaves preemption disabled or FP state exposed. Calling on CPUs without FPU support is invalid. Test signals include kernel FPU selftests/users, preempt debug, context-switch FP state preservation, and builds with `CPU_FTR_FPU_UNAVAILABLE` paths.
