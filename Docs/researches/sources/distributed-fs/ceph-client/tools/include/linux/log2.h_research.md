<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/log2.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/log2.h

## Purpose
`log2.h` supplies integer base-2 logarithm, power-of-two tests, and round-to-power helpers.

## APIs And Flow
It defines `__ilog2_u32()`, `__ilog2_u64()`, `is_power_of_2()`, `__roundup_pow_of_two()`, `__rounddown_pow_of_two()`, and constant-capable macros `ilog2()`, `roundup_pow_of_two()`, and `rounddown_pow_of_two()`. Compile-time constants use a long ternary cascade; runtime values dispatch to `fls`, `fls64`, or `fls_long`.

## State, Dependencies, Risks, Tests
There is no state. Dependencies are `linux/bitops.h` and `linux/types.h`. Risks include undefined behavior for zero in round helpers, `ilog2(0)` returning zero by macro convention, and width differences between `unsigned long` hosts. Tests should cover compile-time and runtime inputs, 32-bit and 64-bit maxima, powers and non-powers, zero edge cases where allowed, and table-size users such as `HASH_BITS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/log2.h -->
