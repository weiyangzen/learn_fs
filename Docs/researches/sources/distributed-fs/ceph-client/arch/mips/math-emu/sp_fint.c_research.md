# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fint.c

Purpose: converts signed 32-bit integers to single-precision emulator values.

Important APIs/functions: `ieee754sp_fint(int x)` handles zero, +/-1, +/-10 through special constants, then converts magnitude/sign into an extended mantissa and calls `ieee754sp_format()`.

Control flow: clears current exceptions, detects sign, handles the most-negative integer without unsafe negation, sets an initial exponent of `SP_FBITS + 3`, shifts right with sticky bits if the integer is too wide for extended precision, otherwise normalizes left until the hidden bit reaches the expected position.

State and persistence: only the current exception flags can change via the formatter, mainly inexact for unrepresentable integers.

Dependencies and integration: called by CVT.S.W emulation and uses single helper macros/constants.

Risks and test signals: test `INT_MIN`, exact powers of two, values requiring rounding, +/-1 and +/-10 fast constants, and all rounding modes for integers just above 24-bit precision.
