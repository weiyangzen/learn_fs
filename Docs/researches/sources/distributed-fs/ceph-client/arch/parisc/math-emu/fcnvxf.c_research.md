# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvxf.c

Purpose: implements signed fixed-point to floating-point conversions.

Important APIs/types/functions: `sgl_to_sgl_fcnvxf`, `sgl_to_dbl_fcnvxf`, `dbl_to_sgl_fcnvxf`, and `dbl_to_dbl_fcnvxf`. Sources are 32-bit signed or two-word `dbl_integer`; destinations are single or double floats.

Control flow: each function determines the source sign, converts negative inputs to magnitude with `Int_negate` or `Dint_negate`, returns positive zero for zero inputs, normalizes the magnitude by finding the most significant one bit, deposits mantissa and exponent fields, and rounds if low bits are lost. Rounding plus and minus are sign-aware; nearest uses the conversion helper tie rules.

State and dependencies: writes destination and status flags. Depends on signed conversion macros in `cnv_float.h`, single/double field macros, and current rounding mode.

Risks: negating the most negative signed integer must preserve the intended magnitude in two's-complement arithmetic. 64-bit signed to single/double paths have complex shifts when the high word is zero versus nonzero. Inexact flagging must occur after destination is written when traps are raised.

Test signals: zero, negative zero absence for integer input, `INT_MIN`, `LONG_LONG_MIN`, max signed values, powers of two, precision-loss cases, all rounding modes, and inexact traps.
