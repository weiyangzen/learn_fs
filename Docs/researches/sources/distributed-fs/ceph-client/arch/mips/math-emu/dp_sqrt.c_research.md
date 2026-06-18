<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sqrt.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sqrt.c

Purpose: Computes correctly rounded IEEE754 double precision square root.

Important APIs/types/functions: `ieee754dp_sqrt(x)` plus an initial approximation lookup table.

Control flow: Handles NaN, zero, infinity, negative invalid, and denormal normalization. It saves CSR, forces round-to-nearest and masks inexact, scales extreme exponents, builds an approximation, refines with division/multiply/add/subtract steps, verifies with a chopped quotient, adjusts for final rounding mode, restores CSR, and rescales.

State and persistence: Temporarily overrides `ieee754_csr` and merges inexact into saved status when required.

Dependencies and integration: Used by `cp1emu.c` for SQRT.D and reciprocal-square-root helper.

Risks: CSR save/restore and final ulp twiddle are delicate. Negative inputs must raise invalid except negative NaNs handled earlier.

Test signals: Validate perfect squares, non-squares under all rounding modes, subnormals, huge/small scaling, negative inputs, infinities, zeros, and NaNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sqrt.c -->
