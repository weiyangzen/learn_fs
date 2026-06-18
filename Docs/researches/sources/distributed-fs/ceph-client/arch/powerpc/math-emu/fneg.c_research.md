<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fneg.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fneg.c

## Purpose
Implements floating negate by toggling the double sign bit.

## Important APIs, types, and functions
`int fneg(u32 *frD, u32 *frB)` XORs the high word with `0x80000000`.

## Control flow
Straight-line bit manipulation and optional DEBUG output.

## State and persistence behavior
Only the destination FPR image is updated; FPSCR is not touched.

## Dependencies and integration points
Dispatched for `FNEG`.

## Risks and edge cases
It must preserve NaN payloads and signed-zero payload bits other than sign.

## Test signals
Destination equals source with sign flipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fneg.c -->
