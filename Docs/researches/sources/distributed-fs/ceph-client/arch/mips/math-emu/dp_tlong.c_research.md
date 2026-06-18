<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tlong.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tlong.c

Purpose: Converts double precision values to signed 64-bit integers according to current rounding mode.

Important APIs/types/functions: `ieee754dp_tlong(x)`.

Control flow: Special classes raise invalid or return zero. For normals/denormals, exponent >=63 is overflow except exact negative INT64_MIN. Smaller values shift mantissa, compute rounding bits without undefined 64-bit shifts, apply rounding mode, detect post-round overflow, set inexact, and apply sign.

State and persistence: Reads and updates `ieee754_csr`.

Dependencies and integration: Used by `cp1emu.c` for `CVT.L.D` and long rounded/trunc/ceil/floor conversions.

Risks: Exact INT64_MIN handling and shift-by-64 avoidance are critical. Rounding can overflow after an initially in-range value.

Test signals: Test INT64_MIN exact, INT64_MAX boundary, huge overflow, +/-0.5, denormals, NaNs/infinities, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tlong.c -->
