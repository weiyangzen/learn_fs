# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmin.c

Purpose: implements MIPS single-precision `MIN.S` and `MINA.S` semantics.

Important APIs/functions: `ieee754sp_fmin()` returns the numeric minimum; `ieee754sp_fmina()` returns the operand with minimum absolute magnitude. They share the same classification and NaN handling approach as the max helpers.

Control flow: sNaNs raise invalid and are quieted, qNaNs are returned only if both operands are qNaN, and numeric operands are preferred when exactly one input is qNaN. Explicit infinity/zero logic handles signed zero. Finite comparisons examine sign, exponent, and mantissa, with absolute-value comparison in `fmina`.

State and persistence: only current exception flags change on signaling NaNs.

Dependencies and integration: called by COP1 emulator for min/mina instructions. Depends on single-precision classification and denormal macros.

Risks and test signals: test -0 versus +0, negative finite ordering, qNaN numeric preference, both-qNaN behavior, sNaN exceptions, equal magnitude ties, and denormal cases.
