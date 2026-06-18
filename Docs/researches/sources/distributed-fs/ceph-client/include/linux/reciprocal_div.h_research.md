# sources/distributed-fs/ceph-client/include/linux/reciprocal_div.h

## Purpose

This header provides precomputed reciprocal division helpers for fast division by a runtime-invariant 32-bit divisor. It replaces repeated division with multiplication and shifts, based on the Granlund-Montgomery invariant integer division algorithm.

## Important APIs, Types, and Functions

`struct reciprocal_value` stores multiplier `m` and shifts `sh1`/`sh2`. `reciprocal_value(u32 d)` computes this slow-path representation. `reciprocal_divide(u32 a, struct reciprocal_value R)` performs the fast-path division using a 64-bit multiply high and correction shifts.

`struct reciprocal_value_adv` stores multiplier `m`, shift `sh`, exponent `exp`, and `is_wide_m`. `reciprocal_value_adv(u32 d, u8 prec)` computes a more JIT-friendly representation for generated code paths that can trade setup cost for fewer emulated operations.

## Control Flow

Callers compute the reciprocal once for a divisor that remains stable, then use `reciprocal_divide()` for each dividend. The advanced flow handles special divisors, may pre-shift even divisors when the multiplier is wide, and then emits either a simple shift, wide-multiplier correction sequence, or multiply/shift sequence in generated code.

## State and Persistence Behavior

The only state is the caller-owned reciprocal structure. It is deterministic for the divisor and precision and can be cached anywhere the divisor is cached. No global state is modified.

## Dependencies and Integration Points

The header depends on fixed-width kernel types. It integrates with networking, hashing, schedulers, BPF/JIT or emulation code, and other hot paths that repeatedly divide by the same 32-bit value.

## Risks

Using a reciprocal computed for one divisor with another divisor gives silent wrong results. Divisor zero must be rejected before computation. The advanced helper excludes the `d > 1U << 31` case described in comments and requires careful handling around powers of two, wide multipliers, and precision.

## Test Signals

Exhaustive or randomized tests should compare reciprocal results against hardware division across divisors, including 1, powers of two, large values near `2^31`, odd/even divisors, and maximum dividends. JIT tests should verify emitted sequences match `n / d` for the documented exceptional cases.
