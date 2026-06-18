# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvff.c

Purpose: implements floating-point format conversions between single and double precision.

Important APIs/types/functions: `sgl_to_dbl_fcnvff()` and `dbl_to_sgl_fcnvff()`. They use conversion macros from `cnv_float.h`, single/double field macros, and status/rounding helpers.

Control flow: single-to-double is mostly exact: it handles infinity, NaN quieting, zero, denormal normalization, exponent rebiasing, and mantissa expansion. Double-to-single handles infinity/NaN, computes the destination exponent, chooses normal or denormalized conversion, derives inexact/guard/sticky/odd bits, rounds according to the current mode, handles mantissa overflow, and then performs overflow/underflow trap or default-result processing.

State and dependencies: writes the destination and status flags. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, and `cnv_float.h`.

Risks: double-to-single is lossy and contains most of the risk: denormalized conversion, tiny detection, wrapped trap exponent checks, and NaN payload truncation. Single-to-double should be exact except signaling NaN quieting, so any inexact flag there would be suspicious.

Test signals: all single/double class conversions, signaling and quiet NaNs, denormal single to normal double, double values near single overflow/underflow thresholds, tie-to-even cases, all rounding modes, and enabled overflow/underflow/inexact traps.
