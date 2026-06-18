<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fint.c

Purpose: Converts a signed 32-bit integer to IEEE754 double precision.

Important APIs/types/functions: `ieee754dp_fint(int x)`.

Control flow: Fast paths zero, one, and ten; records sign, handles minimum negative integer without undefined negation, normalizes mantissa, and builds a double directly.

State and persistence: Clears `ieee754_csr`; conversion is exact and should not set inexact/overflow.

Dependencies and integration: Used by `cp1emu.c` for `CVT.D.W`.

Risks: Minimum integer handling must avoid signed overflow.

Test signals: Convert 0, +/-1, +/-10, INT_MIN, INT_MAX, and random integers exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fint.c -->
