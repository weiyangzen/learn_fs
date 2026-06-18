<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fsp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fsp.c

Purpose: Converts IEEE754 single precision values to double precision.

Important APIs/types/functions: `ieee754dp_fsp(union ieee754sp x)` and helper `ieee754dp_nan_fsp()`.

Control flow: Decodes the single, clears exceptions, flushes denormals as configured, preserves NaN payload/sign into double width, maps infinities and zeros, normalizes denormals, drops the hidden bit, and builds a double with widened mantissa.

State and persistence: Updates `ieee754_csr` for signaling NaN through `ieee754dp_nanxcpt()`.

Dependencies and integration: Used by `cp1emu.c` for `CVT.D.S`.

Risks: NaN payload widening and denormal normalization must preserve architecture semantics.

Test signals: Convert all special classes plus representative exact single values; sNaN should set invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fsp.c -->
