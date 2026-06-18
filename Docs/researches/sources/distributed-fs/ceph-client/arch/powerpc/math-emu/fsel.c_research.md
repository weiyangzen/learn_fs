<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsel.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsel.c

## Purpose
Implements `fsel`, selecting between two floating operands based on the sign/class of `frA`.

## Important APIs, types, and functions
`int fsel(void *frD, void *frA, void *frB, void *frC)` unpacks `frA` and copies either `frC` or `frB` into `frD`.

## Control flow
The selector operand is unpacked. If `A` is NaN or non-negative, `frC` is chosen; otherwise `frB` is chosen. The selected double image is copied directly.

## State and persistence behavior
Destination FPR image is replaced; FPSCR exceptions are not generated.

## Dependencies and integration points
Dispatched for `FSEL`.

## Risks and edge cases
NaN selection behavior and signed-zero treatment must match PowerPC `fsel` semantics.

## Test signals
Destination equals the expected source operand for negative, zero, positive, and NaN selectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsel.c -->
