# sources/distributed-fs/ceph-client/include/math-emu/op-2.h

## Purpose
`op-2.h` implements the two-word fraction backend for software floating-point emulation. It extends the one-word macro contract to fractions stored as low/high limbs, provides two-limb shifts and comparisons, raw pack/unpack helpers, multiple multiplication and division algorithms, square root, integer assembly/disassembly, and conversions between one- and two-word formats.

## Important APIs, Types, And Data
Two-word values are represented as `_FP_W_TYPE X_f0` and `X_f1`. Core macros include `_FP_FRAC_DECL_2`, `_FP_FRAC_COPY_2`, `_FP_FRAC_SET_2`, `_FP_FRAC_HIGH_2`, `_FP_FRAC_LOW_2`, `_FP_FRAC_WORD_2`, `_FP_FRAC_SLL_2`, `_FP_FRAC_SRL_2`, `_FP_FRAC_SRS_2`, `_FP_FRAC_ADDI_2`, `_FP_FRAC_ADD_2`, `_FP_FRAC_SUB_2`, `_FP_FRAC_DEC_2`, `_FP_FRAC_CLZ_2`, predicates, and constants `_FP_ZEROFRAC_2`, `_FP_MINFRAC_2`, and `_FP_MAXFRAC_2`.

Internal helpers define `__FP_FRAC_SET_2` and `__FP_CLZ_2`. Add/subtract/dec macros are mapped to `add_ssaaaa` and `sub_ddmmss` in the active branch, while an unused `#if 0` branch documents portable C fallbacks. Raw pack/unpack macros map `frac0`, `frac1`, `exp`, and `sign` fields from format-specific unions.

Multiplication options include `_FP_MUL_MEAT_2_wide`, `_FP_MUL_MEAT_2_wide_3mul`, `_FP_MUL_MEAT_2_gmp`, and `_FP_MUL_MEAT_2_120_240_double`. Division options include `_FP_DIV_MEAT_2_udiv` and `_FP_DIV_MEAT_2_gmp`. Square-root is `_FP_SQRT_MEAT_2`. Conversion helpers are `_FP_FRAC_ASSEMBLE_2`, `_FP_FRAC_DISASSEMBLE_2`, `_FP_FRAC_CONV_1_2`, and `_FP_FRAC_CONV_2_1`.

## Control Flow
Generic math-emu code performs fraction operations by invoking these macros on named operands. Shifts move bits across the low/high limb boundary, and sticky right shifts OR low discarded bits into the resulting least-significant bit. Add/subtract use longlong primitives to propagate carry or borrow across two limbs.

Wide multiplication computes partial products into a four-word temporary, accumulates cross terms, sticky-right-shifts the product to the target working precision, and stores the low two limbs into the result. The three-multiply variant trades more additions/subtractions for fewer multiplications. GMP variants delegate to `mpn_mul_n()` or `mpn_divrem()` when available. The 120x240 double algorithm uses floating-point arithmetic with controlled exceptions/rounding for certain 64-bit, 106-to-120-bit working fractions.

Division normalizes or aligns the numerator based on operand comparison, estimates quotient limbs with `udiv_qrnnd`, multiplies back to correct overestimates, adjusts quotient words, and sets sticky if a remainder remains. Square root iterates from high to low quotient bits, subtracting trial values and setting round/sticky on leftover remainder.

## State And Persistence Behavior
No persistent state exists. The macros mutate local two-word operand variables and temporary declarations. Exponent adjustments are made through `R_e` in division paths when quotient normalization changes. Rounding information is stored in low-limb work bits.

## Dependencies And Integration Points
`op-2.h` depends on `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_W_TYPE_SIZE`, `UWtype`, `UDItype`, `DItype`, longlong primitives `add_ssaaaa`, `sub_ddmmss`, `umul_ppmm`, `udiv_qrnnd`, optional GMP `mpn_mul_n()`/`mpn_divrem()`, and caller-supplied FPU environment macros for the double-based multiplication path. It also depends on four-word operations from `op-4.h` for multiplication temporaries.

It integrates with double precision on 32-bit-word configurations and with wider emulated formats whose working fractions need two machine words.

## Risks
Carry and borrow handling across limbs is the main correctness risk. The active branch assumes architecture longlong primitives are correct and available. Shift macros have separate paths for counts below or above one word and must not be called with invalid counts outside the modeled fraction size.

The double-based multiply path is highly specialized: it aborts if `wfracbits` is outside 106 to 120, requires exception masking and round-toward-zero setup, and relies on exact properties of double arithmetic and 24-bit chunks. GMP paths depend on array limb order matching the `_f0`/`_f1` convention.

## Test Signals
Macro tests should compare two-limb add, subtract, shifts, sticky shifts, CLZ, comparisons, multiply, divide, sqrt, and conversions against arbitrary-precision reference arithmetic. Architecture tests should exercise exact one-word-boundary shifts, quotient correction cases, nonzero remainders, NaN conversion without sticky rounding, and both 32-bit and 64-bit limb builds where applicable.
