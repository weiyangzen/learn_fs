<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdiv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdiv.c

## Purpose
Implements double-precision floating divide.

## Important APIs, types, and functions
`int fdiv(void *frD, void *frA, void *frB)` uses `FP_DIV_D` and explicitly sets PowerPC invalid/divide-by-zero exception classes.

## Control flow
It unpacks operands, detects `0/0`, `inf/inf`, and nonzero divided by zero, honors enabled divide-by-zero traps by returning before packing, then performs soft-fp division and packs a double result.

## State and persistence behavior
Destination FPR and soft-fp exception state are updated.

## Dependencies and integration points
Called for `FDIV` by `do_mathemu`; `record_exception` converts returned flags to FPSCR status.

## Risks and edge cases
Trap-before-result behavior for divide-by-zero and invalid operation classification must match ISA requirements.

## Test signals
Correct quotient bits plus FPSCR VXZDZ, VXIDI, ZX, and FEX behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdiv.c -->
