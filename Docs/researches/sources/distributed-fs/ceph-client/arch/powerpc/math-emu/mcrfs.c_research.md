<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mcrfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mcrfs.c

## Purpose
Implements move from FPSCR field to condition register field.

## Important APIs, types, and functions
`int mcrfs(u32 *ccr, u32 crfD, u32 crfS)` extracts a 4-bit FPSCR field, clears selected FPSCR exception bits, and writes a CR field.

## Control flow
It computes the FPSCR source mask, uses a special clear mask for field zero, moves the field to `*ccr`, and returns zero.

## State and persistence behavior
Mutates `__FPU_FPSCR` and caller CCR image.

## Dependencies and integration points
Dispatched by `do_mathemu` for `MCRFS`.

## Risks and edge cases
Source field zero clearing differs from other fields; CR field bit placement must be correct.

## Test signals
CR destination field matches source FPSCR field and expected sticky bits are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mcrfs.c -->
