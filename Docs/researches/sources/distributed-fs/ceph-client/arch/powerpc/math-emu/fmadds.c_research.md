<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadds.c

## Purpose
Implements single-precision result multiply-add for `frA * frC + frB`.

## Important APIs, types, and functions
`int fmadds(void *frD, void *frA, void *frB, void *frC)` mirrors `fmadd` and packs through `__FP_PACK_DS`.

## Control flow
It unpacks double operands, flags invalid zero/infinity multiply and infinity subtraction, computes multiply then add, and packs a single-precision result.

## State and persistence behavior
Destination FPR and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched for opcode `FMADDS`.

## Risks and edge cases
Single-result rounding, NaN propagation, and multiply-add exception ordering are sensitive.

## Test signals
Expected single result and FPSCR invalid/inexact/overflow flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadds.c -->
