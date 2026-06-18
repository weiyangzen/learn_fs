<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucmpdi2.c -->
# sources/distributed-fs/ceph-client/lib/ucmpdi2.c

## Purpose
Provides the libgcc-style `__ucmpdi2()` helper for comparing two unsigned 64-bit integers on architectures/toolchains that need an out-of-line runtime routine.

## APIs, Types, and Functions
Exports `word_type notrace __ucmpdi2(unsigned long long a, unsigned long long b)`. It uses `DWunion` from `linux/libgcc.h` to access high and low 32-bit halves.

## Control Flow, State, and Persistence
The function compares unsigned high halves first, returning 0 if `a < b` and 2 if `a > b`. If high halves match, it compares low halves with the same return codes. Equal values return 1. There is no state.

## Dependencies and Integration
Depends on module exports and kernel libgcc compatibility types. It integrates with compiler-generated calls that expect GCC's comparison return convention for doubleword unsigned comparisons.

## Risks and Test Signals
Risks include ABI return convention mismatch, endian/union layout assumptions delegated to `DWunion`, and accidental tracing recursion if `notrace` were removed. Test signals include compiler runtime tests for less/equal/greater high and low half combinations and architecture builds that emit `__ucmpdi2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucmpdi2.c -->
