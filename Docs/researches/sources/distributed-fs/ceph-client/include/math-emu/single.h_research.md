# sources/distributed-fs/ceph-client/include/math-emu/single.h

Purpose: Defines IEEE 754 binary32/single precision constants, raw representation, and `FP_*_S` macro aliases for the soft-fp operation core.

Important APIs/types/functions: `_FP_FRACBITS_S`, `_FP_EXPBITS_S`, `_FP_EXPBIAS_S`, `_FP_EXPMAX_S`, `_FP_QNANBIT_S`, `_FP_IMPLBIT_S`, and `_FP_OVERFLOW_S` configure the format. `union _FP_UNION_S` overlays a `float` with endian-sensitive sign, exponent, and fraction fields. Public macros cover declaration, raw/canonical unpack and pack, sign test, negation, add/subtract, multiply, divide, square root, compare/equality, integer conversion, and integer construction.

Control flow: All public operations delegate to one-word generic helpers: `_FP_UNPACK_RAW_1`, `_FP_PACK_RAW_1`, `_FP_UNPACK_CANONICAL(S,1,...)`, and `_FP_*` arithmetic macros. The header expects the target machine to supply single-precision multiply/divide meat macros.

State and persistence: Contains no persistent data. It defines local macro variables and uses caller-owned exception/rounding state from `soft-fp.h`.

Dependencies and integration: Includes no headers directly beyond the soft-fp inclusion context. It relies on `sfp-machine.h` for word types and on `op-1.h` and `op-common.h` for implementation.

Risks and test signals: Primary risks are endian bitfield correctness, insufficient `_FP_W_TYPE_SIZE`, and target-specific multiply/divide hooks. Test raw bit round-trips for normal, subnormal, signed zero, infinities, quiet/signaling NaNs, plus rounding and exception behavior for add/subtract cancellation and conversion boundaries.
