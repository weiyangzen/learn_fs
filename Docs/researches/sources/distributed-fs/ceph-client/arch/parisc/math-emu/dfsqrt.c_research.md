# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsqrt.c

Purpose: implements double-precision square root.

Important APIs/types/functions: `dbl_fsqrt(dbl_floating_point *srcptr, unsigned int *_nullptr, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: the function handles NaNs, signaling NaNs, positive infinity, zero, and invalid negative inputs. Finite positive operands are normalized; odd/even exponent parity determines a pre-shift. The core square-root algorithm builds result bits using a trial sum (`result + newbit`), subtracting from the shifted source when the trial fits and shifting `newbit` down otherwise. Remaining source bits mark inexactness; rounding then handles plus and nearest modes before final exponent rebiasing.

State and dependencies: writes destination and status flags. Depends on `float.h`, `dbl_float.h`, and current rounding mode.

Risks: the algorithm comments are incomplete and include “Trust me, it works,” so maintainers need reference tests before changing it. Negative zero is returned unchanged through the zero path, while negative nonzero is invalid. Inexact handling treats sticky as always true after remainder remains, which must match the bit-generation algorithm.

Test signals: square roots of zero, negative zero, negative finite, positive infinity, NaNs, perfect squares, values just between representable roots, denormals, all rounding modes, and inexact trap behavior.
