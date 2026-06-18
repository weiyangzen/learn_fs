<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-prototypes.h

## Purpose
This header declares compiler helper routines implemented outside normal C code and referenced by m68k assembly or libgcc-like paths.

## Important APIs, Types, And Functions
- Signed helpers: `__divsi3()`, `__modsi3()`, and `__mulsi3()`.
- Unsigned helpers: `__udivsi3()` and `__umodsi3()`.

## Control Flow
There is no header-local control flow. Callers branch to helper implementations when generated code or assembly needs 32-bit division, modulo, or multiplication support.

## State And Persistence Behavior
No persistent state is defined; helpers are pure arithmetic contracts from the caller perspective.

## Dependencies And Integration Points
This integrates with m68k arithmetic helper implementations and modversion/prototype generation for assembly-exported symbols.

## Risks And Edge Cases
Prototype mismatches can corrupt calling conventions for arithmetic helpers. Division helpers must preserve ABI expectations around registers and signedness.

## Test Signals
Builds with symbol versioning and arithmetic-heavy code paths, plus runtime tests for signed/unsigned division, modulo, and multiplication on CPU variants lacking native support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-prototypes.h -->
