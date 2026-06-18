# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfadd.c

Purpose: implements double-precision floating-point addition for the emulator.

Important APIs/types/functions: `dbl_fadd(dbl_floating_point *leftptr, dbl_floating_point *rightptr, dbl_floating_point *dstptr, unsigned int *status)` returns `NOEXCEPTION` or an exception mask. It uses `Dbl_*` macros for classification, alignment, arithmetic, normalization, and status updates.

Control flow: operands are copied into two-word locals. The function first handles NaNs, signaling NaNs, infinities, and invalid opposite-signed infinity addition. It orders finite operands by magnitude, handles zero and denormal fast paths, then aligns the smaller operand into an extension word. Opposite signs trigger subtraction and possible left normalization; same signs trigger addition and possible right prenormalization. Rounding uses extension bits and the current rounding mode. Overflow and underflow trap settings determine whether wrapped results or default finite/infinite values are returned.

State and dependencies: mutates only destination and `*status` flags through macros such as `Set_invalidflag`, `Set_overflowflag`, and `Set_inexactflag`. Depends on `float.h` and `dbl_float.h`.

Risks: add/sub sign selection is encoded through the signed value of an XOR result, making regressions subtle. Denormal exactness and signed-zero selection are rounding-mode-sensitive. A missing `break` after `ROUNDMINUS` intentionally falls through to truncate behavior but should be treated carefully.

Test signals: IEEE-754 addition vectors covering NaNs, infinities, signed zeros, denormals, cancellation, overflow, all rounding modes, underflow traps, and inexact traps.
