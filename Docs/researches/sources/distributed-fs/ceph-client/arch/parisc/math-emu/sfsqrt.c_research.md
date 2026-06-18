# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsqrt.c

Purpose: implements `sgl_fsqrt`, single-precision square root emulation.

Important APIs and types: source and destination are `sgl_floating_point` words; the second pointer argument is unused for decoder signature compatibility. Status controls invalid and inexact behavior.

Control flow: the function handles signaling NaNs, quiet NaNs, positive infinity, zeros, and invalid negative inputs. It normalizes denormal operands and determines whether the exponent is even. If needed it pre-shifts the significand, then performs a digit-by-digit square-root construction using `newbit`, `sum`, and subtract/shift steps. Remaining source bits indicate inexact; rounding uses current mode, with `ROUNDPLUS` and `ROUNDNEAREST` relevant for positive roots. It then computes the halved exponent and writes the result.

State and persistence: destination and status are the only mutated external state.

Dependencies and integration: called by `fpudispatch.c` for `FSQRT`. Depends on `sgl_float.h` helpers and PA-RISC exception macros from `float.h`.

Risks: comments admit the core algorithm is under-documented. Exponent parity and pre/post shifts are easy to break. Negative zero must return zero, while negative finite and negative infinity must signal invalid.

Test signals: include perfect squares, non-perfect inexact roots, subnormal inputs, smallest normal, positive infinity, quiet and signaling NaNs, negative finite values, negative infinity, signed zeros, and inexact trap behavior.
