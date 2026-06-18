# sources/distributed-fs/ceph-client/include/math-emu/op-1.h

## Purpose
`op-1.h` implements the one-word fraction backend for the kernel software floating-point emulation framework. It provides declaration, assignment, shifts with sticky bits, arithmetic predicates, raw native-float pack/unpack helpers, multiply/divide/sqrt algorithms, integer assembly/disassembly, and one-word-to-one-word fraction conversion.

## Important APIs, Types, And Data
The one-word fraction is represented as a single `_FP_W_TYPE X_f`. Core macros include `_FP_FRAC_DECL_1`, `_FP_FRAC_COPY_1`, `_FP_FRAC_SET_1`, `_FP_FRAC_HIGH_1`, `_FP_FRAC_LOW_1`, `_FP_FRAC_WORD_1`, `_FP_FRAC_ADDI_1`, `_FP_FRAC_SLL_1`, `_FP_FRAC_SRL_1`, `_FP_FRAC_SRS_1`, `_FP_FRAC_ADD_1`, `_FP_FRAC_SUB_1`, `_FP_FRAC_DEC_1`, `_FP_FRAC_CLZ_1`, and predicates for negative, zero, overflow, equality, greater-than, and greater-or-equal.

Raw conversion macros `_FP_UNPACK_RAW_1`, `_FP_UNPACK_RAW_1_P`, `_FP_PACK_RAW_1`, and `_FP_PACK_RAW_1_P` use `union _FP_UNION_<fs>` fields `frac`, `exp`, and `sign`. Arithmetic meat macros include `_FP_MUL_MEAT_1_imm`, `_FP_MUL_MEAT_1_wide`, `_FP_MUL_MEAT_1_hard`, `_FP_DIV_MEAT_1_imm`, `_FP_DIV_MEAT_1_udiv_norm`, `_FP_DIV_MEAT_1_udiv`, and `_FP_SQRT_MEAT_1`. Conversion helpers are `_FP_FRAC_ASSEMBLE_1`, `_FP_FRAC_DISASSEMBLE_1`, and `_FP_FRAC_CONV_1_1`.

## Control Flow
Callers use this header indirectly through format headers such as `double.h` or other precision definitions. The generic arithmetic layer declares operands, unpacks raw bits, canonicalizes them, and then calls the selected one-word meat macro for multiply, divide, or sqrt.

Left and right shifts mutate the single fraction word. Sticky right shift sets the low bit if any discarded bit was nonzero, preserving rounding information. Multiplication either uses immediate host multiplication, a supplied wide multiply primitive, or a manual half-word split/reassemble algorithm. Division either uses a host divide helper or `udiv_qrnnd` in normalized or non-normalized forms. Square root performs an iterative restoring algorithm, adding work-round/sticky bits if a remainder remains.

## State And Persistence Behavior
There is no persistent state. Every macro mutates caller-provided macro variables in the current expression/block. Rounding state is carried in work bits inside the fraction word, especially `_FP_WORK_ROUND` and `_FP_WORK_STICKY`, and exception/result inhibition is managed outside this file.

## Dependencies And Integration Points
This backend depends on `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_W_TYPE_SIZE`, `_FP_I_TYPE`, `_FP_WORK_ROUND`, `_FP_WORK_STICKY`, `_FP_WFRACBITS_<fs>`, `_FP_WFRACXBITS_<fs>`, `__FP_CLZ`, `udiv_qrnnd`, and optional wide multiply/divide helpers from architecture longlong support. It also depends on format-specific unions with `bits.frac`, `bits.exp`, and `bits.sign`.

It integrates with higher-level math-emu headers that select one-limb storage for formats whose working fraction fits in one machine word, especially on 64-bit hosts for double precision.

## Risks
Macro arguments are evaluated in mutable contexts, so callers must pass simple operand names with the expected suffix variables. Shift counts must stay within assumptions; sticky-shift expressions use `_FP_W_TYPE_SIZE - N` and are unsafe if passed invalid counts. Carry, borrow, and sticky propagation errors directly cause wrong rounding.

The `_FP_MUL_MEAT_1_hard` fallback relies on splitting a word exactly in half and reassembling products without overflow beyond modeled limbs. Division helpers depend on architecture-specific `udiv_qrnnd` semantics, including whether normalization is required.

## Test Signals
Unit-level macro tests can compare one-word operations against high-precision integer arithmetic for shifts, sticky shifts, add/subtract, multiply, divide, sqrt, and conversions. Floating-point instruction emulation tests should stress halfway rounding, sticky-bit tails, exact/inexact division, square-root remainders, overflow-bit clearing, and raw pack/unpack round-trips.
