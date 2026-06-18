<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb0.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb0.c

## Purpose
Implements clear FPSCR bit instruction.

## Important APIs, types, and functions
`int mtfsb0(int crbD)` clears bit `31-crbD` in `__FPU_FPSCR` except for reserved bits 1 and 2.

## Control flow
One conditional mask operation plus optional DEBUG logging.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched for `MTFSB0`.

## Risks and edge cases
Reserved bit protection for bits 1 and 2 must match architecture semantics.

## Test signals
Expected FPSCR bit clears and reserved bits unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb0.c -->
