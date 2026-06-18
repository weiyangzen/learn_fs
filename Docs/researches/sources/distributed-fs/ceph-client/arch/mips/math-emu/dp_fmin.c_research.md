<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmin.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmin.c

Purpose: Implements double precision minimum and minimum-by-absolute-value operations for MIPS R6.

Important APIs/types/functions: `ieee754dp_fmin(x, y)` and `ieee754dp_fmina(x, y)`.

Control flow: Mirrors fmax structure for NaN handling, infinity/zero special cases, denormal normalization, sign/exponent/mantissa comparison, and magnitude-based comparison for MINA.

State and persistence: Clears and updates `ieee754_csr` for NaN exceptions.

Dependencies and integration: Called by `cp1emu.c` for `MIN.D` and `MINA.D`.

Risks: Correct signed-zero result is subtle: min returns negative zero when either zero is negative. Magnitude ties have sign-specific behavior.

Test signals: Same class coverage as fmax, with emphasis on negative values and signed zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmin.c -->
