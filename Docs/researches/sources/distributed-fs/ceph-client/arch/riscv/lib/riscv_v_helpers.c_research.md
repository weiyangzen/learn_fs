<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/riscv_v_helpers.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/riscv_v_helpers.c

## Purpose
`riscv_v_helpers.c` bridges scalar and vector user-copy implementations for RISC-V vector-capable kernels.

## Important APIs, Types, And Functions
`riscv_v_usercopy_threshold` controls when vector copy is attempted. `enter_vector_usercopy()` is the exported C entry used by assembly. It calls `__asm_vector_usercopy` or `_sum_enabled` inside `kernel_vector_begin/end`, then falls back to scalar routines for remaining bytes or when SIMD use is not allowed.

## Control Flow
The caller has already checked vector ISA availability. The helper verifies `may_use_simd()`, starts a kernel vector section, performs vector copy, ends the section, and if a fault leaves bytes remaining, adjusts source/destination pointers and invokes the matching scalar fallback.

## State And Persistence
Only the tunable threshold is persistent runtime state. Copies affect user/kernel memory but the helper does not own that memory.

## Dependencies And Integration Points
It depends on vector context management, SIMD preemption rules, assembly usercopy symbols, and MMU-only uaccess integration.

## Risks
The boolean `enable_sum` selects whether SUM is already enabled; mixing the two paths could fault or leave SUM handling wrong. Vector use is only safe inside kernel vector guards.

## Test Signals
Usercopy tests with vector enabled/disabled, threshold tuning, page-fault fallback tests, and preemption/SIMD stress are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/riscv_v_helpers.c -->
