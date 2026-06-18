# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fdp.c

Purpose: converts double-precision emulator values to single precision.

Important APIs/functions: `ieee754sp_fdp(union ieee754dp x)` is the exported conversion helper. `ieee754sp_nan_fdp()` builds a single NaN payload from double sign and mantissa. The implementation uses double unpacking and single formatting.

Control flow: after clearing exceptions and flushing double denormals as configured, it handles sNaN by quieting first, converts qNaN payloads with legacy fallback to indefinite if the truncated payload is not still NaN, preserves infinity and signed zero, treats double denormals as underflow/inexact to zero or min denormal depending on rounding, and formats normal values after a sticky right shift from DP mantissa width to SP plus GRS bits.

State and persistence: updates current exception flags for invalid, underflow, and inexact cases.

Dependencies and integration: used by CVT.S.D emulation and relies on both precision headers.

Risks and test signals: test NaN payload truncation, legacy versus NaN-2008 mode, min double normal/denormal conversion, overflows to single infinity/max, and all rounding modes around halfway values.
