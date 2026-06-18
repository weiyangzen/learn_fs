# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tlong.c

Purpose: converts a single-precision value to a signed 64-bit integer according to FCR31 rounding mode.

Important APIs/functions: `ieee754sp_tlong(union ieee754sp x)` returns `s64`, using `ieee754di_indef()` for NaNs and `ieee754di_overflow(xs)` for invalid infinities/out-of-range inputs.

Control flow: after classification and exception reset, NaN/inf cases set invalid, zero returns 0, the exact `-2^63` corner is accepted, large exponents shift the mantissa left, and smaller exponents compute residue/round/sticky/odd for rounding. If rounding creates a 64-bit overflow, invalid is raised.

State and persistence: updates only current exception flags.

Dependencies and integration: used by CVT.L.S and rounding-mode variants in the COP1 emulator.

Risks and test signals: test near `S64_MIN/S64_MAX`, tie values, negative directed rounding, inexact flag, NaN/inf invalid, and the use of double-width temporary macros with single inputs.
