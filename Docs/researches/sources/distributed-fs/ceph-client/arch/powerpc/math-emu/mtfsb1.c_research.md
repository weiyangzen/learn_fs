<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb1.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb1.c

## Purpose
Implements set FPSCR bit instruction.

## Important APIs, types, and functions
`int mtfsb1(int crbD)` sets bit `31-crbD` in `__FPU_FPSCR` except for reserved bits 1 and 2.

## Control flow
One conditional OR operation plus optional DEBUG logging.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched for `MTFSB1`.

## Risks and edge cases
Reserved bit handling and later FEX/VX summary recomputation are external to this file.

## Test signals
Expected FPSCR bit sets and reserved bits unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb1.c -->
