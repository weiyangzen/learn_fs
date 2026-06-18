# sources/distributed-fs/ceph-client/lib/crypto/x86/sm3.h

## Purpose
Provides the x86-specific SM3 block-dispatch glue that routes SM3 block processing to the AVX assembly transform when the CPU and kernel FPU state support it.

## APIs, Types, and Functions
The header declares `asmlinkage void sm3_transform_avx(...)`, defines `sm3_blocks_avx()` as the FPU-safe wrapper, declares `DEFINE_STATIC_CALL(sm3_blocks_x86, sm3_blocks_generic)`, defines local `sm3_blocks()` as the static-call dispatch point, and provides `sm3_mod_init_arch()` for feature selection.

## Control Flow
`sm3_blocks_avx()` checks `irq_fpu_usable()`. If usable, it brackets `sm3_transform_avx()` with `kernel_fpu_begin()` and `kernel_fpu_end()`; otherwise it calls `sm3_blocks_generic()`. At init time, the static-call target is updated only when AVX, BMI2, and SSE/YMM xfeatures are all available.

## State and Persistence
The static-call target is the only persistent mutable state. Callers provide and own all SM3 chaining state. No allocations, locks, or permanent buffers are managed here.

## Dependencies and Integration Points
Depends on x86 CPU feature helpers, kernel FPU APIs, static calls, the generic SM3 implementation, and the `sm3_transform_avx` assembly symbol. It integrates with the kernel crypto SM3 module through architecture hook macros.

## Risks and Test Signals
Risks include dispatching AVX code without valid xstate support, failing to fall back in FPU-unsafe contexts, and link failures when assembly support is misconfigured. Test signals are SM3 crypto selftests, feature-selection tests on AVX/BMI2 and non-AVX hosts, forced generic fallback checks, and module builds for configurations with and without the x86 optimized object.
