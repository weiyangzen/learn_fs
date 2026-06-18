<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_mul.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_mul.c

Purpose: Multiplies two IEEE754 double precision values.

Important APIs/types/functions: `ieee754dp_mul(x, y)`.

Control flow: Handles NaNs, infinity-zero invalid, infinities, zeros, denormal normalization, computes sign/exponent, multiplies 53-bit mantissas through 32-bit partial products into high/low 64-bit state, applies sticky rounding reduction, and formats.

State and persistence: Updates `ieee754_csr` through exception and formatting helpers.

Dependencies and integration: Used by `cp1emu.c`, sqrt, and non-fused multiply-add emulation.

Risks: Partial-product carry propagation and sticky bit construction are precision-critical.

Test signals: Cover special classes, sign combinations, exact powers of two, denormals, overflow, underflow, and inexact products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_mul.c -->
