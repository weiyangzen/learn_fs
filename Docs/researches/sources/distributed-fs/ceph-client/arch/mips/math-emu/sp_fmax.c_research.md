# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmax.c

Purpose: implements MIPS single-precision `MAX.S` and `MAXA.S` semantics, including NaN preference rules and signed-zero tie handling.

Important APIs/functions: `ieee754sp_fmax()` returns the numeric maximum; `ieee754sp_fmaxa()` returns the operand with maximum absolute magnitude. Both use classification, denormal flush, invalid exception for sNaN, and direct field comparisons.

Control flow: each function first handles sNaN and qNaN precedence, preferring numeric operands over quiet NaNs. Infinity/zero cases are handled explicitly. The finite path compares signs, exponents, and mantissas; `fmaxa` ignores sign for magnitude then uses sign as a tie breaker.

State and persistence: mutates only exception flags for sNaN invalid operations.

Dependencies and integration: used by MIPS R6 or IEEE-754-2008 max instruction emulation through the COP1 emulator.

Risks and test signals: test qNaN versus numeric, sNaN invalid, +0 versus -0, equal-magnitude opposite signs for `MAXA`, infinities, denormals under `nod`, and exact mantissa tie cases.
