<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/simd.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/simd.h

Purpose: Provides the generic kernel SIMD gating API for RISC-V, mapped to vector-context availability.

Important APIs/types/functions: Defines `may_use_simd()`, `kernel_vector_begin()`, `kernel_vector_end()` integration, and interrupt/preemption checks.

Control flow: Callers test whether SIMD/vector use is safe, then bracket vector operations with begin/end.

State and persistence: State is per-task/vector context ownership and preemption/interrupt state.

Dependencies and integration points: Used by crypto/string routines that may use vector instructions and by vector context code.

Risks: Using vector state in unsafe contexts can corrupt user or kernel vector registers.

Test signals: Kernel-mode vector crypto/string tests, preemption/RT configs, interrupt nesting, and vector save/restore stress.

Source read size: 64 lines, 1772 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/simd.h -->
