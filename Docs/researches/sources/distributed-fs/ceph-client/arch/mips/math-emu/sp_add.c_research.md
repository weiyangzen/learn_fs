# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_add.c

Purpose: implements single-precision IEEE-754 addition for the MIPS FPU emulator.

Important APIs/functions: `ieee754sp_add(union ieee754sp x, union ieee754sp y)` is the exported helper. It uses `EXPLODEXSP`, `EXPLODEYSP`, `FLUSHXSP/YSP`, `ieee754sp_nanxcpt()`, special value constructors, sticky shifts, and `ieee754sp_format()`.

Control flow: after classification and exception reset, a `CLPAIR` switch handles sNaN/qNaN precedence, infinities, signed zero rules, and denormal normalization. For finite nonzero values it adds guard/round/sticky bits, aligns exponents by sticky right shifting, adds equal-sign mantissas or subtracts opposite-sign mantissas, normalizes cancellation, and delegates rounding/overflow/underflow to the formatter.

State and persistence: updates only `ieee754_csr` exception fields. The rounding mode determines signed zero for exact cancellation.

Dependencies and integration: called from `cp1emu.c` for ADD.S and by legacy `abs/neg` helpers when `abs2008` is disabled.

Risks and test signals: test all NaN precedence cases, `+inf + -inf`, signed zero under round-down, denormal inputs with and without `nod`, cancellation normalization, exponent alignment with sticky bits, and each rounding mode.
