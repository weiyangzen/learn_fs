# sources/distributed-fs/ceph-client/include/math-emu/op-8.h

## Purpose
`op-8.h` supplies the minimal eight-word fraction helpers needed by the wider math-emulation backends, especially as temporary product storage for four-word multiplication. It defines eight-limb declaration/access macros and left, right, and sticky-right shifts.

## Important APIs, Types, And Data
Eight-word values are represented as `_FP_W_TYPE X_f[8]`, with low limb at index 0 and high limb at index 7. Exposed macros are `_FP_FRAC_DECL_8`, `_FP_FRAC_HIGH_8`, `_FP_FRAC_LOW_8`, `_FP_FRAC_WORD_8`, `_FP_FRAC_SLL_8`, `_FP_FRAC_SRL_8`, and `_FP_FRAC_SRS_8`.

Unlike the smaller operation headers, this file intentionally omits add/subtract, predicates, pack/unpack, multiplication, division, sqrt, and conversion helpers. Its comment states only a few pieces are needed for `op-4`, and more can be added later.

## Control Flow
The shift macros compute the number of whole limbs to skip and the intra-limb shift. Left shifts copy from lower to higher indices, right shifts copy from higher to lower indices, and then zero-fill vacated limbs. Sticky right shift first ORs together all fully discarded low limbs plus the partially discarded bits, performs the right shift, zero-fills high limbs, and ORs the final low bit if any discarded bit was nonzero.

## State And Persistence Behavior
There is no runtime persistence. The macros mutate caller-provided `X_f[8]` arrays and local loop variables only. Sticky information is carried in the shifted result's low bit for downstream rounding.

## Dependencies And Integration Points
The header depends on `_FP_W_TYPE`, `_FP_I_TYPE`, and `_FP_W_TYPE_SIZE`. Its primary integration point is `op-4.h`, where `_FP_FRAC_DECL_8`, `_FP_FRAC_WORD_8`, and `_FP_FRAC_SRS_8` hold and normalize full-width four-by-four-limb products.

## Risks
Shift correctness is the dominant risk. The macros assume valid shift counts for the modeled eight-limb value; out-of-range counts could index beyond the array or perform undefined-width shifts. Sticky-right shift accesses `X_f[_i]` after scanning fully skipped limbs, so callers must not request a shift that skips all eight limbs without guarding elsewhere.

Because the header provides only shift primitives, any future expansion must preserve the low-limb-first convention used by `op-4.h` and GMP-style multiplication arrays.

## Test Signals
Tests should shift eight-limb values by zero, one, word-size minus one, exactly one word, multiple words, and near the full width. Sticky-right tests should place a single set bit in each discarded limb or partial-limb position and verify only the final low bit records discarded data. Integration tests should multiply four-limb fractions in `op-4.h` and verify the eight-limb normalization path.
