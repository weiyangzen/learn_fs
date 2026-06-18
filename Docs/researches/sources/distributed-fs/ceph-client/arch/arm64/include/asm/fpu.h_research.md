## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpu.h

Purpose: small generic FPU interface adapter for arm64.

Important APIs/types/functions: exposes `kernel_fpu_available`, `kernel_fpu_begin`, and `kernel_fpu_end` semantics by tying them to FPSIMD/NEON support.

Control flow: callers bracket kernel-mode FP/NEON usage with begin/end helpers implemented elsewhere or as wrappers.

State and persistence: interacts with current task FP ownership and CPU FP enable state.

Dependencies and integration: used by crypto, RAID, networking, and other kernel code that may use vector instructions.

Risks: unbalanced begin/end or wrong availability checks corrupt user FP state. Test signals are crypto SIMD selftests, preemption stress around kernel NEON users, and FPSIMD context-switch tests.
