# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_maddf.c

Purpose: implements single-precision fused multiply-add/subtract variants for MIPS, computing `z +/- (x*y)` with one final rounding.

Important APIs/functions: internal `_sp_maddf(z, x, y, flags)` handles the operation. Wrappers `ieee754sp_maddf`, `msubf`, `madd`, `msub`, `nmadd`, and `nmsub` select sign transformations using `enum maddf_flags`.

Control flow: the function unpacks three operands, flushes denormals, clears exceptions, computes product sign and optional negations, applies NaN precedence z/x/y with sNaN first, handles invalid `inf*0`, infinity addition conflicts, zero product plus z rules, then multiplies to a 64-bit product, aligns z and product exponents, adds or subtracts, normalizes, and formats once.

State and persistence: updates FCR31 exception flags for invalid/inexact/overflow/underflow through helper calls.

Dependencies and integration: used by fused COP1 instruction emulation and relies on precise single formatter behavior.

Risks and test signals: fused rounding must not double-round. Test `inf*0`, opposite-sign infinities, signed-zero results, cancellation to zero under round-down, denormal z/product, all wrapper sign combinations, and halfway rounding cases.
