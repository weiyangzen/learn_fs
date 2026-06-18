# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-inline.h

## Purpose
Defines inline helper functions for adding/subtracting a single limb and combining unequal-size limb arrays.

## Important APIs, Types, and Functions
- Inline `mpihelp_add_1()`, `mpihelp_add()`, `mpihelp_sub_1()`, and `mpihelp_sub()`.
- Uses exported equal-size helpers `mpihelp_add_n()` and `mpihelp_sub_n()`.

## Control Flow and State
Single-limb helpers process the first limb, propagate carry/borrow until it clears or the input is exhausted, copy any remaining unchanged limbs when destination differs from source, and return final carry/borrow. Multi-limb helpers process the smaller equal-size portion, then apply carry/borrow to the remaining longer operand.

## Dependencies and Integration Points
Included by `mpi-internal.h` for GCC builds. Used by public MPI addition/subtraction, multiplication recomposition, and division correction.

## Risks and Test Signals
The helpers assume size relationships supplied by callers. Tests should cover carry/borrow stopping early, full propagation through all limbs, destination/source identity, and unequal operand lengths.
