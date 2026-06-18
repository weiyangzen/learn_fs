# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffs.h

## Purpose

This header defines the generic `__ffs` helper, which returns the zero-based index of the least significant set bit in an unsigned long.

## APIs, State, and Dependencies

`__ffs(unsigned long word)` uses staged tests and shifts, with an extra 32-bit step on 64-bit long builds. It depends on `__BITS_PER_LONG` and basic asm types. The function is undefined for zero input, matching kernel semantics. There is no persistent state.

## Risks and Test Signals

Callers must test for nonzero before calling. Word-size macros must match the compiler ABI or bit positions will be wrong. Tests should cover representative 32-bit and 64-bit inputs, single-bit positions, and compile-time integration through `find_*_bit` helpers.
