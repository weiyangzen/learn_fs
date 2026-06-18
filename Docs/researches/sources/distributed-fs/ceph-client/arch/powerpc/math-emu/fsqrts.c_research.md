<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrts.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrts.c

## Purpose
Implements single-precision result square root from a double-format FPR source.

## Important APIs, types, and functions
`int fsqrts(void *frD, void *frB)` mirrors `fsqrt` but packs with `__FP_PACK_DS`.

## Control flow
The handler unpacks, flags invalid negative square-root inputs, computes square root, and rounds/packs as single precision.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FSQRTS`.

## Risks and edge cases
Single-result rounding and negative input classification are the main concerns.

## Test signals
Single sqrt result and VXSQRT/FEX behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrts.c -->
