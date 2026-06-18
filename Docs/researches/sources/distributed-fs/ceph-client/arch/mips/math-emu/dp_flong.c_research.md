<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_flong.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_flong.c

Purpose: Converts a signed 64-bit integer to IEEE754 double precision.

Important APIs/types/functions: `ieee754dp_flong(s64 x)`.

Control flow: Fast paths zero, one, and ten; handles INT64_MIN safely; normalizes or right-shifts with sticky bits when more than double precision; formats with rounding.

State and persistence: Clears and updates `ieee754_csr` via formatting, including inexact for unrepresentable 64-bit integers.

Dependencies and integration: Used by `cp1emu.c` for `CVT.D.L` and by `dp_rint.c` to rebuild rounded integral doubles.

Risks: High-bit normalization and sticky shifts govern correct rounding near 2^53 and INT64 limits.

Test signals: Convert exact values below 2^53, inexact values above it, INT64_MIN/MAX, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_flong.c -->
