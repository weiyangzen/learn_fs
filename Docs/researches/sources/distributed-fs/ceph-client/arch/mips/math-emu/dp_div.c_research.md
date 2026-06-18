<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_div.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_div.c

Purpose: Divides IEEE754 double precision operands.

Important APIs/types/functions: `ieee754dp_div(x, y)`.

Control flow: Handles NaNs, infinities, zeros, zero-divide and invalid cases, normalizes denormals, then performs bitwise long division with rounding space and sticky remainder before formatting.

State and persistence: Updates `ieee754_csr` for invalid, divide-by-zero, inexact, overflow, or underflow through helper formatting.

Dependencies and integration: Used by FPU `DIV.D`, reciprocal/rsqrt helpers, and sqrt iterations.

Risks: Long division loop and sticky remainder determine correct rounding. Zero divided by zero and infinity divided by infinity must raise invalid.

Test signals: Vectors should include divide by zero, zero dividend, infinities, NaNs, denormals, exact divisions, inexact divisions, and sign combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_div.c -->
