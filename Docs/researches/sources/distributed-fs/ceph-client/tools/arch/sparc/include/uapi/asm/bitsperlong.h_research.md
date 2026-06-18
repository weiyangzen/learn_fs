# sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/bitsperlong.h

## Purpose
SPARC UAPI word-size selector for tools.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` as 64 for `__sparc__ && __arch64__`, otherwise 32, then includes generic bits-per-long. The include guard name is historically Alpha-like but only guards this file.

## Control Flow, State, and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by SPARC UAPI/tools headers.

## Risks and Test Signals
Risk is macro-detection drift or confusing include guard naming during maintenance. Test signals are sparc32/sparc64 preprocessing checks.
