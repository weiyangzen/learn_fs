<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_rint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_rint.c

Purpose: Rounds a double precision value to an integral-valued double according to current rounding mode.

Important APIs/types/functions: `ieee754dp_rint(x)`.

Control flow: Special classes return or signal as appropriate. Values already integral return unchanged. Fractional mantissa bits are split into residue/round/sticky/odd, rounding mode adjusts the integer mantissa, inexact is set if needed, and the result is rebuilt with original sign.

State and persistence: Reads `ieee754_csr.rm` and sets `IEEE754_INEXACT`.

Dependencies and integration: Used by `cp1emu.c` for R6 `RINT.D`.

Risks: Tie-to-even and sign-directed modes must be exact around half values and very small magnitudes.

Test signals: Test +/-0.5, +/-1.5, just-below/above integers, large integral values, NaNs, infinities, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_rint.c -->
