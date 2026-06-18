# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls64.h

## Purpose

This header defines `fls64`, the one-based most-significant-set-bit helper for 64-bit values.

## APIs, State, and Dependencies

On 32-bit long builds, `fls64` checks the high 32 bits first and falls back to `fls` on the low half. On 64-bit long builds, it returns `0` for zero or `__fls(x) + 1`. It errors for unsupported word sizes. There is no state.

## Risks and Test Signals

Correctness depends on `BITS_PER_LONG` matching target ABI and on `fls`/`__fls` semantics. Tests should cover zero, 32-bit boundary values, bit 63, and both 32-bit and 64-bit toolchain builds.
