# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfdiv.c

Purpose: implements `sgl_fdiv`, single-precision floating-point division.

Important APIs and types: operands and destination are `sgl_floating_point` words; status controls invalid, divide-by-zero, overflow, underflow, and inexact traps. Guard and sticky booleans track rounding information.

Control flow: the function computes result sign, handles NaNs, infinities, zero divisor, and zero dividend, then computes the exponent difference. It normalizes denormal operands, performs a non-restoring divide over `SGL_P` bits, derives guard and sticky bits from the remainder, rounds if needed, installs mantissa and exponent, and handles overflow or underflow with trap wrapping or denormalization.

State and persistence: writes the destination and exception flags in the status word. It has no heap or static state.

Dependencies and integration: called by `fpudispatch.c` for `FDIV`. Depends on `sgl_float.h` for normalization, denormalization, mantissa operations, and rounding mode.

Risks: non-restoring divide is sensitive to sign-bit tests on intermediate remainders. Underflow detection distinguishes tininess before and after rounding; mistakes can set or miss underflow flags. Divide-by-zero and `0/0` must route to different exceptions.

Test signals: include finite exact and inexact divisions, subnormal numerator and denominator, division by zero, zero by zero, infinity by infinity, finite by infinity, overflow, gradual underflow, all rounding modes, and trap-enabled combinations.
