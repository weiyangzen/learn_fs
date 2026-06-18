## sources/distributed-fs/ceph-client/include/linux/count_zeros.h

Purpose: This header provides small helpers to count leading and trailing zero bits in an `unsigned long`.

Important APIs, types, and functions: `count_leading_zeros(unsigned long x)` returns the number of zero bits from the most significant bit toward the least significant bit, using `fls()` for 32-bit longs and `fls64()` otherwise. `count_trailing_zeros(unsigned long x)` returns `__ffs(x)` for nonzero values or `BITS_PER_LONG` for zero.

Control flow: Both functions branch only on word size or zero input. The zero case is explicitly defined for both functions as `BITS_PER_LONG`.

State and persistence: No state is stored; functions are pure bit operations.

Dependencies and integration points: It depends on architecture bitops for `fls`, `fls64`, `__ffs`, and `BITS_PER_LONG`. It is useful in algorithms needing normalized bit positions without duplicating zero handling.

Risks and test signals: Risks include architecture bitops with undefined zero behavior, accidental type widening, and confusion between 32-bit and 64-bit long widths. Test signals include values 0, 1, MSB-only, all ones, and randomized comparisons against compiler builtins on 32-bit and 64-bit builds.
