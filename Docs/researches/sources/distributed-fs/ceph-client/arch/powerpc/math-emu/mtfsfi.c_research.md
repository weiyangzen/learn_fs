<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsfi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsfi.c

## Purpose
Implements move immediate to FPSCR field.

## Important APIs, types, and functions
`int mtfsfi(unsigned int crfD, unsigned int IMM)` writes a 4-bit immediate into one FPSCR field, using a special mask for field zero.

## Control flow
It clears the selected field bits and ORs in `IMM & 0xf` at the correct field position.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched by `do_mathemu` for `MTFSFI`.

## Risks and edge cases
Field zero masking differs from the general `0xf` mask.

## Test signals
FPSCR selected field equals immediate while other fields remain unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsfi.c -->
