# sources/distributed-fs/ceph-client/lib/math/div64.c

Purpose: Supplies generic 64-bit division helpers, mostly for 32-bit architectures and for product-plus-add divided by a 64-bit divisor.

Important APIs/types/functions: Exports weak `__div64_32`, `div_s64_rem`, `div64_u64_rem`, `div64_u64`, `div64_s64`, `iter_div_u64_rem`, and `mul_u64_add_u64_div_u64` when not provided by architecture headers/macros. Internal helpers split multiplication into 32-bit or 16-bit chunks unless native `u128` is available.

Control flow: 32-bit fallback division normalizes high halves and performs shift/subtract long division. `div64_u64*` estimates quotient by shifting divisor/dividend and corrects by one if needed. `mul_u64_add_u64_div_u64()` forms a 128-bit numerator, detects overflow/zero-divisor exceptional cases, normalizes divisor, then performs digit-wise long division.

State and persistence: Stateless arithmetic.

Dependencies/integration: Depends on `asm/div64.h` callers, `linux/math64.h`, bit operations, min/max, and arch override mechanisms.

Risks: Division by zero intentionally triggers a runtime exception in one overflow path. Edge cases include high-half overflow, divisor near 2^64, quotient saturation, and architecture-dependent code paths.

Test signals: Covered by `test_div64.c` and `test_mul_u64_u64_div_u64.c`; also widely exercised by kernel math users.
