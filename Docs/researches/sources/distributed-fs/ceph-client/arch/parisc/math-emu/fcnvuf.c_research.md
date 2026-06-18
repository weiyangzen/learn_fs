# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvuf.c

Purpose: implements unsigned fixed-point to floating-point conversions.

Important APIs/types/functions: `sgl_to_sgl_fcnvuf`, `sgl_to_dbl_fcnvuf`, `dbl_to_sgl_fcnvuf`, and `dbl_to_dbl_fcnvuf`. Sources are 32-bit unsigned or `dbl_unsigned`; destinations are single or double floats.

Control flow: zero returns signed-positive zero. Nonzero sources use `Find_ms_one_bit()` to locate the most significant one bit, left-justify the integer, set mantissa and biased exponent, and then round only when the destination precision cannot hold all source bits. Single-destination conversions can be inexact; double-destination from 32-bit unsigned is exact, while 64-bit unsigned to double may be inexact.

State and dependencies: writes destination and status flags. Depends on unsigned conversion macros in `cnv_float.h` and field macros from single/double headers.

Risks: normalization depends on `Find_ms_one_bit()` returning the legacy position convention. Shift expressions around `dst_exponent` are range-sensitive. Unsigned-to-float never creates negative results, so `ROUNDMINUS` intentionally does not increment.

Test signals: zero, powers of two, `UINT_MAX`, `ULLONG_MAX`, values just above single/double precision limits, all rounding modes, and inexact trap behavior for lossy conversions.
