# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.c

Purpose: single-precision common implementation for classification, signaling-NaN exception conversion, and final result formatting with IEEE-754 rounding and exception behavior.

Important APIs/functions: `ieee754sp_class()` returns a class from raw fields; `ieee754sp_nanxcpt()` raises invalid operation and quiets signaling NaNs according to `nan2008`; `ieee754sp_format(int sn, int xe, unsigned int xm)` creates a final single from sign, unbiased exponent, and a mantissa with guard/round/sticky bits.

Control flow: `ieee754sp_format()` handles subnormal/tiny results, optional no-denormal flush, inexact rounding, exponent carry, overflow to infinity or max finite based on rounding mode, and normal/denormal construction via `buildsp()`.

State and persistence: updates the current task's FCR31 exception cause/sticky bits through `ieee754_setcx()`. No other state is stored.

Dependencies and integration: used by all `sp_*` arithmetic and conversion files, and by double-to-single conversion. It depends on `ieee754sp.h`.

Risks and test signals: highest-risk areas are underflow after rounding, GRS handling, NaN-2008 sNaN conversion, and overflow result selection under RU/RD/RZ/RN. Tests should use raw bit vectors around exponent and mantissa boundaries.
