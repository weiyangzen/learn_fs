# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sub.c

Purpose: implements single-precision subtraction for the MIPS IEEE-754 emulator.

Important APIs/functions: `ieee754sp_sub(union ieee754sp x, union ieee754sp y)` mirrors `sp_add.c` but flips the sign of `y` after special-class handling and uses subtraction-specific infinity/zero rules.

Control flow: classification handles NaNs, `inf - inf`, finite minus infinity, infinity minus finite, zeros, and denormals. For finite operands it toggles `ys`, aligns exponents using sticky shifts, adds if signs match or subtracts magnitudes if signs differ, handles exact zero with round-down sign, normalizes, and formats.

State and persistence: updates current exception flags and uses rounding mode for exact-zero sign.

Dependencies and integration: used by SUB.S and by legacy abs/neg paths.

Risks and test signals: test `inf - inf` invalid, signed zero combinations, cancellation, exponent alignment sticky bits, denormal normalization, qNaN/sNaN precedence, and all rounding modes.
