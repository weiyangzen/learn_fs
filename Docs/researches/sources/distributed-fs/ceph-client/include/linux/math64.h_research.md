<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math64.h -->
# sources/distributed-fs/ceph-client/include/linux/math64.h

## Purpose
This header provides portable 64-bit division and multiply/divide helpers that work efficiently on both 32-bit and 64-bit kernels.

## Important APIs, types, and functions
It defines `div64_long`, `div64_ul`, `div_u64_rem`, `div_s64_rem`, `div64_u64_rem`, `div64_u64`, `div64_s64`, `div_u64`, `div_s64`, `iter_div_u64_rem`, `mul_u32_u32`, `add_u64_u32`, `mul_u64_u32_shr`, `mul_u64_u64_shr`, `mul_s64_u64_shr`, `mul_u64_u32_div`, `mul_u64_add_u64_div_u64`, `mul_u64_u64_div_u64`, rounded divide macros, and `roundup_u64`.

## Control flow
On 64-bit builds most division helpers compile to native operators. On 32-bit builds, missing architecture primitives are external declarations or use `do_div()`. Multiplication helpers use `unsigned __int128` when supported, otherwise split operands into 32-bit halves and recombine shifted products.

## State and persistence
There is no persistent state. Remainder pointers are caller-provided output state.

## Dependencies and integration points
It depends on Linux types, `math.h`, architecture `div64`, and VDSO math definitions. It is a low-level utility for timekeeping, drivers, block, networking, and memory code that cannot assume native 64-bit division.

## Risks and test signals
Risks include zero divisors, overflow behavior in generic multiply-add-divide, sign handling in `mul_s64_u64_shr`, shifts at or above word size, and mismatched 32-bit/64-bit code generation. Test signed negative dividends, high 64-bit values, shift boundaries 0/63/64+, divisor overflow cases, and cross-architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math64.h -->
