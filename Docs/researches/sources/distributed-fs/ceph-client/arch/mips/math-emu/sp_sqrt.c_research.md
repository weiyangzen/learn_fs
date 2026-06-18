# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sqrt.c

Purpose: implements single-precision square root in software.

Important APIs/functions: `ieee754sp_sqrt(union ieee754sp x)` handles special classes, normalizes the operand, computes the square root bit by bit, and rounds according to FCR31.

Control flow: sNaN raises invalid and quiets, qNaN/zero/+inf return unchanged, negative finite or -inf raises invalid and returns indefinite. Finite positive values are normalized by exponent parity, then a restoring square-root loop builds `q`. Remainder sets inexact, and RU/RN rounding adjusts `q` before rebuilding the raw exponent/mantissa.

State and persistence: mutates only current exception flags, notably invalid and inexact.

Dependencies and integration: called by SQRT.S emulation; uses `ieee754sp.h` constants but implements final packing directly rather than through `ieee754sp_format()`.

Risks and test signals: test negative inputs, +/-0, +inf, sNaN/qNaN, denormals, perfect squares, inexact roots under all rounding modes, and exponent parity transitions.
