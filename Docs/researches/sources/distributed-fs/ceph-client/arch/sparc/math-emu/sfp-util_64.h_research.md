# sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_64.h

Purpose: SPARC64 machine-dependent soft-fp support macros optimized for 64-bit words.

Important APIs/types/macros: `add_ssaaaa` and `sub_ddmmss` implement 128-ish add/sub on paired `UDItype` words. `umul_ppmm` uses `mulx` and 32-bit decomposition to produce high/low product words. `udiv_qrnnd` implements normalized double-word division in C using high/low divisor halves. `UDIV_NEEDS_NORMALIZATION` is `1`; `abort()` returns `0`; byte order is derived from kernel endian macros.

Control flow: macro-expanded into soft-fp code. The multiply macro is inline assembly with temporaries and carry handling. The divide macro performs Knuth-style two-step quotient digit estimation and correction.

State and persistence: no runtime state outside callers. Uses condition codes in asm and caller variables for quotient/remainder.

Dependencies/integration: includes kernel/sched/types and `asm/byteorder.h`. Used by `math_64.c` and generic soft-fp headers for quad/single/double operations.

Risks: `UDIV_NEEDS_NORMALIZATION` must agree with the divide macro implementation; soft-fp callers normalize before invoking it. Carry handling in `umul_ppmm` is compact and architecture-specific. The C divide macro assumes nonzero normalized high divisor halves.

Test signals: FP emulation tests for quad multiply/divide/conversions, compiler checks for inline asm constraints, and randomized soft-fp operation comparison against hardware or IEEE reference where available.
