# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-add.c

## Purpose
Implements signed MPI addition/subtraction and modular add/subtract wrappers.

## Important APIs, Types, and Functions
- Exports `mpi_add()`, `mpi_sub()`, `mpi_addm()`, and `mpi_subm()`.
- Uses low-level `mpihelp_add()`, `mpihelp_sub()`, `mpihelp_sub_n()`, `mpihelp_add_n()`, `mpihelp_cmp()`, and `MPN_NORMALIZE()`.

## Control Flow and State
`mpi_add()` orders operands by limb count, resizes the destination, handles zero smaller operand, then either adds magnitudes for equal signs or subtracts magnitudes for differing signs. It normalizes the result and sets sign according to the larger magnitude. `mpi_sub()` copies `v`, flips its sign, and calls `mpi_add()`. Modular wrappers compute the operation then reduce with `mpi_mod()`.

## Dependencies and Integration Points
Used by public-key and modular arithmetic code. It depends on destination resizing before alias-sensitive pointer reads.

## Risks and Test Signals
Risks include sign errors around equal magnitudes and allocation failure when copying for subtraction. Tests should include positive/negative combinations, zero results, aliasing `w == u` or `w == v`, modular add/subtract, and randomized comparisons to a reference big integer library.
