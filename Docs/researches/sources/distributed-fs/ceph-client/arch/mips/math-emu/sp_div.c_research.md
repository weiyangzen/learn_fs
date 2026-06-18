# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_div.c

Purpose: implements single-precision division in software for MIPS FPU emulation.

Important APIs/functions: `ieee754sp_div(union ieee754sp x, union ieee754sp y)` handles all IEEE classes, raises zero-divide or invalid exceptions, performs a bitwise quotient loop, and uses `ieee754sp_format()` for final rounding.

Control flow: after unpacking and clearing exceptions, the class-pair switch handles NaNs, infinities, zero/zero invalid, finite/zero divide-by-zero, zero/finite signed zero, and denormal normalization. The finite path shifts operands into GRS space, computes quotient bits by repeated subtract/shift, sets sticky if remainder remains, normalizes the quotient, and formats with sign `xs ^ ys`.

State and persistence: only exception flags in FCR31 are changed.

Dependencies and integration: called by DIV.S emulation; depends on sticky shift and class macros from `ieee754sp.h`.

Risks and test signals: test exact and inexact quotients, divide by zero, zero divided by finite, infinity combinations, denormal operands, rounding carry, and sticky remainder behavior.
