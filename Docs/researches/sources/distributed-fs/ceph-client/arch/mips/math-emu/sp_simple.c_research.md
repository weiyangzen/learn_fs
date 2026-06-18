# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_simple.c

Purpose: implements single-precision absolute value and negation, respecting the MIPS `abs2008` mode bit.

Important APIs/functions: `ieee754sp_neg()` flips sign directly in IEEE-754-2008 mode, or emulates legacy semantics by subtracting from +0 with temporary round-down mode. `ieee754sp_abs()` clears sign directly in 2008 mode, or uses add/sub from +0 with temporary round-down mode in legacy mode.

Control flow: both functions branch on `ieee754_csr.abs2008`. Legacy paths save/restore `ieee754_csr.rm` and call add/sub helpers to preserve historical NaN and signed-zero behavior.

State and persistence: may temporarily modify rounding mode and may set exception flags indirectly through add/sub. Direct 2008 mode only mutates the returned union.

Dependencies and integration: used by ABS.S and NEG.S instruction emulation.

Risks and test signals: verify legacy versus 2008 mode differences for NaNs and signed zeros, preservation of rounding mode after calls, and exception behavior for signaling NaNs.
