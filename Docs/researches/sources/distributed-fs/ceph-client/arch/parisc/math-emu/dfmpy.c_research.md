# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfmpy.c

Purpose: implements double-precision floating-point multiplication.

Important APIs/types/functions: `dbl_fmpy(dbl_floating_point *srcptr1, dbl_floating_point *srcptr2, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: the result sign is computed first. The function handles NaNs, signaling NaNs, infinities, invalid infinity-times-zero, and zeros. It forms the destination exponent by adding source exponents and subtracting bias, normalizes denormal operands, then multiplies mantissas by inspecting four bits of one operand per loop and accumulating shifted versions of the other operand. After normalization, it derives guard/sticky/inexact bits, rounds, detects overflow, and handles underflow by either returning a wrapped trap result or denormalizing and setting flags.

State and dependencies: writes destination and status flags. Depends on `float.h`, `dbl_float.h`, `Twoword_add`, normalization macros, and rounding-mode state.

Risks: the nibble-at-a-time multiply must maintain sticky bits for discarded product bits. Underflow tiny detection speculatively increments/decrements the mantissa and is easy to desynchronize from rounding rules. Infinity/zero invalid handling has to preserve NaN payload behavior where possible.

Test signals: multiplication vectors for signed zeros, infinities, NaNs, denormals, exact products, half-ulp ties, overflow/underflow boundaries, and all rounding/trap modes.
