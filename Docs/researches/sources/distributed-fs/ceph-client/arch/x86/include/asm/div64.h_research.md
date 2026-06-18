
# sources/distributed-fs/ceph-client/arch/x86/include/asm/div64.h

Purpose: optimized 64-bit division and multiply/divide helpers for x86.

Important APIs and control flow: on 32-bit, `do_div()` modifies the dividend in place and returns the remainder, using power-of-two shifts or `divl` with high-word reduction. `div_u64_rem()`, `mul_u32_u32()`, and `add_u64_u32()` provide efficient 32-bit assembly paths. On 64-bit, generic `div64` is used plus `mul_u64_add_u64_div_u64()` and `mul_u64_u32_div()` using `mulq`, optional add/adc, then `divq`.

State, dependencies, and risks: state is caller variables modified by macros. Dependencies include compiler constraints, `ilog2`, and generic div64. Risks include divide overflow causing #DE on 64-bit helper, macro side effects, zero divisors, and clang/gcc codegen differences. Test signals are arithmetic unit tests, timekeeping frequency calculations, and 32-bit build coverage.
