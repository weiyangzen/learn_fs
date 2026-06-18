# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dbl_float.h

Purpose: defines the double-precision and double-extended word-manipulation macro layer used by PA-RISC floating-point emulation.

Important APIs/types/functions: macros classify and mutate double fields (`Dbl_isnan`, `Dbl_isinfinity`, `Dbl_setoverflow`, `Dbl_denormalize`), perform two-word shifts, addition/subtraction, normalization, copy-to/from pointer operations, and construct NaNs, infinities, zeros, largest finite values, and wrapped exponents. The `Dblext_*` macros support fused multiply-add extended mantissas.

Control flow: callers operate on pairs of 32-bit words. Arithmetic files use these macros to clear sign/exponent and set the hidden bit, align operands into extension words, normalize by byte/nibble/bit scanning, round with guard/sticky bits, and write results back.

State and dependencies: no standalone storage, but macros mutate passed lvalues and consult `Rounding_mode()` through `float.h`. Depends on raw field macros from `float.h` and `Shiftdouble`/`Variable_shift_double` helpers from PA-RISC headers.

Risks: macro side effects are extensive and easy to misuse. Some double-extended macros contain suspicious copy/identifier patterns inherited from legacy code, so fused paths need focused validation. Shift counts are assumed prebounded. NaN signaling polarity is PA-RISC-specific and should not be generalized blindly.

Test signals: double arithmetic conformance tests, denormal and underflow trap tests, NaN quieting/signaling tests, overflow rounding-mode tests, and fused-operation tests if `Dblext_*` callers are changed.
