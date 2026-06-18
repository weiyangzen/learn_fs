<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_simple.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_simple.c

Purpose: Implements double precision absolute value and negation operations.

Important APIs/types/functions: `ieee754dp_neg(x)` and `ieee754dp_abs(x)`.

Control flow: In IEEE754-2008 ABS/NEG mode, directly toggles or clears the sign bit. In legacy mode, temporarily forces round-down and computes zero-minus-x or zero-plus-x via arithmetic helpers.

State and persistence: Temporarily mutates `ieee754_csr.rm` in legacy mode and restores it.

Dependencies and integration: Used by `cp1emu.c` for ABS.D and NEG.D and by non-fused multiply-add emulation.

Risks: Legacy arithmetic path can raise exceptions differently than sign-bit operations; saving/restoring rounding mode is required.

Test signals: Check NaNs, signed zeros, infinities, normals, and both `abs2008` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_simple.c -->
