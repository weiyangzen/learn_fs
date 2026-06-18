# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_flong.c

Purpose: converts signed 64-bit integers to single-precision emulator values.

Important APIs/functions: `ieee754sp_flong(s64 x)` mirrors the 32-bit conversion with a 64-bit temporary mantissa, special-casing zero, +/-1, +/-10, and the most-negative 64-bit value.

Control flow: after sign/magnitude extraction, it sets an extended single exponent and either sticky-shifts right until the value fits or left-normalizes small magnitudes before calling `ieee754sp_format()`.

State and persistence: formatter updates inexact/overflow only through the current task's FCR31 exception fields. No other state exists.

Dependencies and integration: used by CVT.S.L and by `ieee754sp_rint()` to rebuild rounded integral results.

Risks and test signals: test `S64_MIN`, large values that round to powers of two, exact 24-bit mantissas, low values, and all rounding modes. Watch that the 64-bit temporary interacts correctly with single-precision shift macros.
