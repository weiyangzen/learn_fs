# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitsperlong.h

## Purpose

This header reconciles userspace/compiler word-size information with UAPI `__BITS_PER_LONG` for tools builds.

## APIs, State, and Dependencies

It includes `<uapi/asm-generic/bitsperlong.h>`, defines `BITS_PER_LONG` from `__SIZEOF_LONG__` or `__WORDSIZE`, errors if it differs from `__BITS_PER_LONG`, defines `BITS_PER_LONG_LONG` as 64 if missing, and provides `small_const_nbits(nbits)` for optimized bitmap paths. There is no runtime state.

## Risks and Test Signals

Incorrect word-size macros break every bitmap and bitops helper. Tests should compile tools on 32-bit and 64-bit targets and verify `small_const_nbits` optimizations do not change results.
