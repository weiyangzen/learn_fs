# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls.h

## Purpose

This header defines `generic_fls`, returning the one-based position of the most significant set bit in a 32-bit integer, with `fls(0) == 0`.

## APIs, State, and Dependencies

`generic_fls(unsigned int x)` uses a binary-search-like shift sequence over high bit ranges and maps `fls` to it unless an architecture override exists. It has no state and only relies on compiler inline attributes.

## Risks and Test Signals

The public zero behavior differs from `__fls`, which is undefined for zero; callers must pick the right helper. Tests should cover zero, one, high bit, and mixed values, plus code paths using `fls_long`.
