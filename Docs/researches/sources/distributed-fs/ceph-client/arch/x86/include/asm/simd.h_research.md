<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/simd.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/simd.h

Purpose: declares x86 SIMD/FPU-in-kernel availability helpers. Important APIs are `may_use_simd()` and related include glue for code deciding whether vector instructions are safe in kernel context.

Control flow: crypto and optimized routines call these helpers before using SIMD registers; implementation considers preemption, interrupt context, and FPU ownership. State is current CPU/task FPU state managed elsewhere. Dependencies include FPU state management and preemption/context rules.

Risks: using SIMD when not allowed corrupts user FPU state or violates interrupt constraints; being too conservative hurts performance. Test signals include crypto SIMD selftests, preempt/IRQ context checks, KVM/FPU interactions, and kernel_fpu_begin/end validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/simd.h -->
