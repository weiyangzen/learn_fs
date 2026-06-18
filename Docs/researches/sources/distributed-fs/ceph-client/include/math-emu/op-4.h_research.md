# sources/distributed-fs/ceph-client/include/math-emu/op-4.h

## Purpose
`op-4.h` implements the four-word fraction backend for the software floating-point emulator. It supports wider formats and also provides intermediate storage for two-word multiplication. The header defines four-limb declaration/copy/access operations, multiword shifts with sticky support, add/subtract/borrow helpers, comparisons, raw pack/unpack, four-word multiply/divide/sqrt, integer assembly/disassembly, and conversions to and from one- and two-word formats.

## Important APIs, Types, And Data
Four-word fractions are stored as `_FP_W_TYPE X_f[4]`, low limb at index 0 and high limb at index 3. Core macros include `_FP_FRAC_DECL_4`, `_FP_FRAC_COPY_4`, `_FP_FRAC_SET_4`, `_FP_FRAC_HIGH_4`, `_FP_FRAC_LOW_4`, `_FP_FRAC_WORD_4`, `_FP_FRAC_SLL_4`, `_FP_FRAC_SRL_4`, `_FP_FRAC_SRS_4`, `_FP_FRAC_ADD_4`, `_FP_FRAC_SUB_4`, `_FP_FRAC_DEC_4`, `_FP_FRAC_ADDI_4`, `_FP_FRAC_ZEROP_4`, `_FP_FRAC_NEGP_4`, `_FP_FRAC_OVERP_4`, `_FP_FRAC_CLEAR_OVERP_4`, `_FP_FRAC_EQ_4`, `_FP_FRAC_GT_4`, `_FP_FRAC_GE_4`, and `_FP_FRAC_CLZ_4`.

Raw conversion uses `_FP_UNPACK_RAW_4`, `_FP_UNPACK_RAW_4_P`, `_FP_PACK_RAW_4`, and `_FP_PACK_RAW_4_P`, expecting union fields `frac0` through `frac3`, `exp`, and `sign`. Arithmetic meat macros are `_FP_MUL_MEAT_4_wide`, `_FP_MUL_MEAT_4_gmp`, helper `umul_ppppmnnn`, `_FP_DIV_MEAT_4_udiv`, and `_FP_SQRT_MEAT_4`. Internal add/subtract helpers include `__FP_FRAC_ADD_3`, `__FP_FRAC_ADD_4`, `__FP_FRAC_SUB_3`, `__FP_FRAC_SUB_4`, `__FP_FRAC_DEC_3`, `__FP_FRAC_DEC_4`, and `__FP_FRAC_ADDI_4`.

Conversion helpers include `_FP_FRAC_CONV_1_4`, `_FP_FRAC_CONV_2_4`, `_FP_FRAC_ASSEMBLE_4`, `_FP_FRAC_DISASSEMBLE_4`, `_FP_FRAC_CONV_4_1`, and `_FP_FRAC_CONV_4_2`.

## Control Flow
Shift operations compute a word skip and intra-word shift, then copy limbs in high-to-low or low-to-high order to avoid clobbering source limbs before zero-filling the remainder. Sticky right shift collects all bits shifted out and ORs the final least-significant bit after the shifted result is stable.

Four-word multiplication expands partial products into an eight-word temporary, accumulating all cross terms with three-word and two-word add helpers. It then sticky-right-shifts the eight-word product to working precision and stores the low four limbs in the result. The GMP path delegates to `mpn_mul_n()` on four-limb arrays and then normalizes through the eight-word shift helper.

Division normalizes the denominator, then iterates quotient limbs from high to low using `udiv_qrnnd()` and `umul_ppppmnnn()` to estimate and correct each quotient word. It shifts state through `X_f[]` and an auxiliary `_n` array, decrements overestimated quotient words when multiply-back exceeds the remainder, and sets sticky on the low quotient limb when the final remainder is nonzero. Square root is an iterative restoring algorithm that walks high-to-low limbs and sets round/sticky bits if a remainder remains.

## State And Persistence Behavior
There is no persistent state. The header mutates caller-provided fraction arrays and local temporaries. It may adjust result exponent state through `R_e` inside division. Work bits in the low limb carry rounding information for later generic packing.

## Dependencies And Integration Points
`op-4.h` depends on `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_W_TYPE_SIZE`, `UWtype`, `udiv_qrnnd`, `umul_ppmm`, optional `mpn_mul_n()`, and the eight-word primitives declared by `op-8.h`. It expects caller format unions with four fraction fields.

It integrates with wide soft-float formats and with `op-2.h` as a multiplication scratch backend. Because many helper macros are conditionally defined with `#ifndef`, architecture-specific code can override some carry/borrow operations.

## Risks
The implementation is sensitive to limb order, loop bounds, and shift counts. A notable risk is `_FP_FRAC_CLZ_4()` using `X_f[2]` in the branch where `X_f[1]` is nonzero, which looks inconsistent with the intended leading-zero count over limb 1 and should be checked against upstream or tests. Comments also note some conversion macros may be "somewhat bogus" because they depend on internal variable shapes.

Carry/borrow propagation and quotient correction bugs can create one-bit rounding errors that only appear on edge cases. Assembly/disassembly paths for integer sizes above two words rely on shifts by multiples of `_FP_W_TYPE_SIZE`, so target integer widths and compiler behavior matter.

## Test Signals
Tests should cover exact word-boundary shifts, sticky shifts with discarded bits in every limb, comparisons, add/subtract carry chains, multiply cross terms, division quotient correction, sqrt remainders, and conversions between one-, two-, and four-word representations. A targeted CLZ test should exercise nonzero values exclusively in each limb to detect the apparent limb-1 typo. End-to-end soft-float tests should validate wide-format operations against high-precision references.
