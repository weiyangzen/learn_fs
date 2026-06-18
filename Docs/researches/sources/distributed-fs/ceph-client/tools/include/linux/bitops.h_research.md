# sources/distributed-fs/ceph-client/tools/include/linux/bitops.h

## Purpose

This is the main tools bit-operations header. It defines bit sizing macros, exposes hweight software hooks, wraps generic atomic and non-atomic bitops, and provides bit iteration helpers.

## APIs, State, and Dependencies

Macros include `BITS_PER_TYPE`, `BITS_TO_LONGS`, `BITS_TO_U64`, `BITS_TO_U32`, `BITS_TO_BYTES`, and `BYTES_TO_BITS`. It declares `__sw_hweight*`, maps public `__set_bit`, `__clear_bit`, `test_bit`, and related names to generic implementations, includes `asm-generic/bitops.h`, and defines `for_each_set_bit`, `for_each_clear_bit`, and `for_each_set_bit_from`. Inline helpers include `hweight_long`, `fls_long`, `rol32`, and `sign_extend64`.

## Risks and Test Signals

This header is a central include-order point for bitmap code. Missing external hweight/find implementations cause link failures. Tests should compile all tools bit users, exercise iteration over empty/full/sparse bitmaps, and validate sign extension and rotations.
