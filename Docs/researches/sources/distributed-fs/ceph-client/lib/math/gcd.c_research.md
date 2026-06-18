# sources/distributed-fs/ceph-client/lib/math/gcd.c

Purpose: Implements greatest common divisor for unsigned longs using binary GCD variants.

Important APIs/types/functions: Exports `gcd(unsigned long a, unsigned long b)` and defines static key `efficient_ffs_key`. Uses `binary_gcd()` when efficient `__ffs()` support is available.

Control flow: Handles zero inputs by returning `a | b`. On efficient-ffs systems, strips powers of two via `__ffs`, subtracts smaller from larger, and restores common factors. Otherwise uses an even/odd loop optimized for CPUs without fast bit-scan.

State and persistence: Stateless except for the global static branch controlling algorithm selection.

Dependencies/integration: Used by `lcm.c`, rational/math users, and exported GPL-only.

Risks: Performance depends on architecture configuration; arithmetic itself is bounded but assumes unsigned-long semantics.

Test signals: `tests/gcd_kunit.c` covers normal, reversed, coprime, zero, identical, and `ULONG_MAX` cases.
