# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsub.c

Purpose: implements double-precision floating-point subtraction. It is structurally parallel to `dfadd.c`, with sign logic adjusted for subtract semantics.

Important APIs/types/functions: `int dbl_fsub(dbl_floating_point *leftptr, dbl_floating_point *rightptr, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: operands are copied, NaNs and infinities are processed first, and same-signed infinity subtraction is invalid. Right infinity is returned with inverted sign. Finite operands are ordered by magnitude; if the right operand has larger magnitude, operands are swapped and the result sign is inverted. Denormal and zero cases are handled before the general path. The smaller magnitude is aligned into an extension word. Same signs perform subtraction; opposite signs add magnitudes. The result is normalized, rounded, and checked for overflow or underflow.

State and dependencies: writes destination and `*status` through macros. Depends on `float.h` and `dbl_float.h`.

Risks: differs from addition mainly by tests such as `save == 0` versus `save != 0` and `save >= 0` versus `< 0`; copy/paste fixes must preserve those inversions. Signed-zero behavior depends on rounding mode. The `ROUNDMINUS` switch fallthrough is legacy behavior and should be reviewed only with tests.

Test signals: subtraction cancellation, signed zeros, same/opposite infinities, NaNs, denormals, magnitude swaps, overflow/underflow traps, inexact traps, and all rounding modes.
