# sources/distributed-fs/ceph-client/include/math-emu/quad.h

Purpose: Defines IEEE 754 binary128/quad precision layout and public `FP_*_Q` macros for the generic soft-fp engine.

Important APIs/types/functions: Constants describe 113 fraction bits, 15 exponent bits, bias 16383, exponent max 32767, implicit bit, quiet-NaN bit, and overflow sentinel. `union _FP_UNION_Q` maps a `long double` to sign/exponent/fraction bitfields with separate 32-bit-word and 64-bit-word layouts. Public macros include `FP_DECL_Q`, raw and canonical unpack/pack variants, `FP_ADD_Q`, `FP_SUB_Q`, `FP_MUL_Q`, `FP_DIV_Q`, `FP_SQRT_Q`, comparisons, integer conversions, and `FP_FROM_INT_Q`.

Control flow: The header selects a four-word fraction implementation when `_FP_W_TYPE_SIZE < 64` and a two-word implementation on 64-bit words. Each public operation simply binds the quad format tag `Q` and the selected word count to the common machinery in `op-common.h` and the matching `op-N.h` primitives.

State and persistence: No runtime state is stored here. It establishes ABI-sensitive bitfield views and macro expansions used by callers' local variables.

Dependencies and integration: Requires `soft-fp.h`-provided `_FP_WORKBITS`, `_FP_W_TYPE_SIZE`, endian definitions, and fraction helpers. It is consumed by architecture math emulation routines implementing compiler/libgcc floating operations.

Risks and test signals: Risks include compiler bitfield packing, long-double ABI mismatch, endian errors, and different behavior on 32-bit versus 64-bit word targets. Test binary128 encode/decode across both layouts, NaN payload preservation, subnormal normalization, conversion to integer near 2^113, and operations where carries cross fraction-word boundaries.
