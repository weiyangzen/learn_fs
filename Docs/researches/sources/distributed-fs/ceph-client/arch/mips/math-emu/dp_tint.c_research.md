<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tint.c

Purpose: Converts double precision values to signed 32-bit integers according to current rounding mode.

Important APIs/types/functions: `ieee754dp_tint(x)`.

Control flow: NaNs and infinities raise invalid and return indefinite/overflow values. Normal/denormal values shift mantissa according to exponent, compute residue/round/sticky/odd bits, apply rounding mode, detect overflow including post-rounding overflow, set inexact, and apply sign.

State and persistence: Reads `ieee754_csr.rm` and sets invalid/inexact exception bits.

Dependencies and integration: Used by `cp1emu.c` for `CVT.W.D` and rounded/trunc/ceil/floor word conversions.

Risks: The valid `0x80000000` negative corner case is special. Shifts around exponent -1 and 31 are edge-sensitive.

Test signals: Test NaNs, infinities, +/-0, fractions around half, INT_MIN/INT_MAX boundaries, overflow after rounding, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tint.c -->
