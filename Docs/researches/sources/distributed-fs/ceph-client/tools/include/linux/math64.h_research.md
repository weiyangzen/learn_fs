<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math64.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/math64.h

## Purpose
`math64.h` adapts kernel 64-bit division helpers to user-space tool builds.

## APIs And Flow
It includes standard integer support and exposes macros or inline helpers such as `do_div`, `div_u64`, `div64_u64`, `div64_u64_rem`, `div_u64_rem`, `mul_u64_u64_div_u64`, and rounding variants depending on host word size. Flow is arithmetic-only: callers pass 64-bit numerators, optional remainder pointers, and 32-bit or 64-bit divisors.

## State, Dependencies, Risks, Tests
No persistent state is stored. Dependencies are fixed-width types and compiler support for 64-bit arithmetic. Risks include divide-by-zero, truncation when returning 32-bit remainders, host/compiler differences from kernel assembly helpers, and overflow in multiply-then-divide helpers. Tests should compare against known 128-bit reference arithmetic, cover 32-bit and 64-bit hosts, and exercise max-value numerators and divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math64.h -->
