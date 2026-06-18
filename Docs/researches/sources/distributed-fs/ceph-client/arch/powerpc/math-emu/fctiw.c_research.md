<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiw.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiw.c

## Purpose
Implements floating convert to signed integer word with current rounding mode.

## Important APIs, types, and functions
`int fctiw(u32 *frD, void *frB)` unpacks a double and uses `FP_TO_INT_D(r, B, 32, 1)`.

## Control flow
The source is unpacked, converted to a 32-bit signed integer, and stored in `frD[1]`; the high word is not explicitly overwritten.

## State and persistence behavior
Only the destination FPR low word is written. Exceptions are tracked in soft-fp state but this function returns zero.

## Dependencies and integration points
Called by `do_mathemu` for `FCTIW`.

## Risks and edge cases
NaN, overflow, and inexact conversion behavior depends on soft-fp; returning zero may hide exception flags unless macros have side effects visible to caller context.

## Test signals
Expected integer word in `frD[1]` and correct FPSCR behavior in integrated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiw.c -->
