# sources/distributed-fs/ceph-client/lib/crypto/mpi/longlong.h

## Purpose
Provides architecture-specific and generic macros for double-limb arithmetic used by the MPI library: multiply high/low, divide double-limb by single-limb, add/subtract double words, and leading-zero support.

## Important APIs, Types, and Functions
- Defines or falls back for `umul_ppmm`, `__umulsidi3`, `udiv_qrnnd`, `sdiv_qrnnd`, `add_ssaaaa`, and `sub_ddmmss`.
- Uses compile-time inputs `UWtype`, `UHWtype`, `W_TYPE_SIZE`, and compiler mode typedefs supplied by `mpi-internal.h`.
- Provides architecture branches for many historical CPUs plus active MIPS, ARM, PPC, SPARC, Alpha, x86-style cases and generic C fallback.
- Defines timing hints `UMUL_TIME`, `UDIV_TIME`, and `UDIV_NEEDS_NORMALIZATION`.

## Control Flow and State
This is preprocessor-only code. It selects inline assembly or C formulas based on architecture and word size. The generic multiply splits words into high/low halves. The generic divide `__udiv_qrnnd_c` performs normalized two-half quotient estimation and correction.

## Dependencies and Integration Points
Included by MPI limb helpers and division/multiplication files. It depends on compiler support for inline assembly constraints and GCC integer modes on several paths.

## Risks and Test Signals
Architecture macro bugs can break all MPI arithmetic, and inline assembly constraints are compiler-sensitive. Some old branches may be untested on modern toolchains. Test signals include all-architecture compile coverage, randomized limb multiply/divide property tests, division normalization cases, and comparison of MPI operations across 32-bit and 64-bit limb configurations.
