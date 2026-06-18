# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__fls.h

## Purpose

This header provides `generic___fls`, the zero-based index of the most significant set bit in an unsigned long, and maps `__fls` to it unless an architecture override exists.

## APIs, State, and Dependencies

`generic___fls` starts from `BITS_PER_LONG - 1` and shifts left while testing high chunks. It depends on `BITS_PER_LONG`, asm types, `__always_inline`, and `__attribute_const__`. The function is undefined for zero input.

## Risks and Test Signals

The helper is sensitive to word size and undefined zero semantics. Tests should cover lowest, highest, and mixed set bits on 32-bit and 64-bit builds and ensure `fls64` uses the right path for `BITS_PER_LONG`.
