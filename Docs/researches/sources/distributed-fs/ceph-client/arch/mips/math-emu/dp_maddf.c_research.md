<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_maddf.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_maddf.c

Purpose: Implements double precision fused multiply-add/subtract variants for MIPS R6 and MAC-style operations.

Important APIs/types/functions: Internal `srl128()` performs sticky 128-bit right shifts; `_dp_maddf(z, x, y, flags)` does the fused computation; wrappers include `ieee754dp_maddf`, `msubf`, `madd`, `msub`, `nmadd`, and `nmsub`.

Control flow: Handles NaN precedence across z/x/y, applies product/addition negation flags, resolves invalid infinity/zero products and opposite-signed infinities, multiplies normalized mantissas into 128 bits, aligns addend/product exponents, adds or subtracts 128-bit values, normalizes cancellation, shifts to double rounding precision, and formats once.

State and persistence: Clears and updates `ieee754_csr` through exception and formatting helpers.

Dependencies and integration: Used by `cp1emu.c` for fused R6 `MADDF/MSUBF` and MIPS4-style multiply-add operations.

Risks: Fused semantics require single final rounding; replacing with separate multiply/add changes results. Wrapper flag combinations encode subtle operation differences.

Test signals: FMA tests should compare against known fused results, including cancellation, inf*0 invalid, z infinity conflicts, NaN precedence, and all sign variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_maddf.c -->
