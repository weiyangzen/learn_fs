# sources/distributed-fs/ceph-client/include/math-emu/op-common.h

Purpose: Provides the shared macro engine for GNU soft-fp operations after format-specific headers have defined exponent, fraction, and word-count parameters. It is the arithmetic core used by single, double, quad, and extended precision wrappers rather than a standalone C API.

Important APIs/types/functions: `_FP_DECL` declares canonical class/sign/exponent/fraction variables. `_FP_UNPACK_CANONICAL` classifies raw bitfields into `FP_CLS_NORMAL`, `FP_CLS_ZERO`, `FP_CLS_INF`, or `FP_CLS_NAN`, normalizing denormals and setting denorm/signaling-NaN exceptions. `_FP_PACK_CANONICAL` applies rounding, overflow, underflow, denormal packing, NaN quieting, and result inhibition. Arithmetic macros include `_FP_ADD`, `_FP_SUB`, `_FP_NEG`, `_FP_MUL`, `_FP_DIV`, `_FP_SQRT`, comparisons, integer conversions, and `FP_CONV`. The helper `__FP_CLZ` and `_FP_DIV_HELP_imm` support leading-zero count and word division.

Control flow: Every arithmetic macro switches on combined operand classes, handles NaN/Inf/zero special cases first, and only performs fraction math for normal operands. Add/sub aligns exponents, adds or subtracts fractions, detects cancellation, and renormalizes. Multiply delegates wide fraction product to `_FP_MUL_MEAT_*`; divide delegates quotient generation to `_FP_DIV_MEAT_*`; square root iterates through `_FP_SQRT_MEAT_*`.

State and persistence: State is compile-time macro state plus caller-local temporaries and `_fex` exception bits from `soft-fp.h`. No persistent storage exists.

Dependencies and integration: Depends on `op-1.h`, `op-2.h`, `op-4.h`, `op-8.h`, target `sfp-machine.h`, rounding mode macros, and format constants from `single.h`, `quad.h`, or siblings.

Risks and test signals: Risks are macro side effects, missing target meat macros, endian/word-size assumptions, exact exception semantics, denormal flush behavior, and unsigned shift edge cases. Test with IEEE edge vectors: signed zero arithmetic, NaN quieting, inf-invalid operations, denormal unpack/pack, directed rounding overflow, integer conversion saturation/truncation, and cross-word quad values.
