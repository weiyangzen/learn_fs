# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.c

## Purpose
Implements a shared numeric helper for converting register bitfields encoded as two's-complement values into signed integers.

## Important APIs, Types, and Functions
`cxd2880_convert2s_complement(u32 value, u32 bitlen)` returns `value` as a signed integer, sign-extending from `bitlen` when `1 <= bitlen < 32`.

## Control Flow
The helper treats `bitlen == 0` or `bitlen >= 32` as already full-width. Otherwise it checks the sign bit, ORs high bits with `GENMASK(31, bitlen)` for negative values, and masks low bits for positive values.

## State and Persistence
No state. It is pure computation.

## Dependencies and Integration Points
Uses `GENMASK()` from kernel bit helpers via `cxd2880_common.h`. Monitor code uses it for RF level, carrier offset, sampling offset, and other signed register values.

## Risks and Edge Cases
Callers must pass the correct field width; wrong widths invert signs or scale readings incorrectly. The `1 << (bitlen - 1)` expression is safe only because bitlen is guarded against zero and 32+.

## Test Signals
Unit-style checks for widths 1, 8, 11, 27, 31, plus zero and 32. Runtime monitor values should change sign correctly around the hardware sign bit.
