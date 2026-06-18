# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mod.c

## Purpose
Implements modular reduction wrapper.

## Important APIs, Types, and Functions
- Function: `int mpi_mod(MPI rem, MPI dividend, MPI divisor)`.
- Delegates directly to `mpi_fdiv_r()`.

## Control Flow and State
There is a single call to floored remainder. State changes happen inside `mpi_fdiv_r()` and are reflected in `rem`.

## Dependencies and Integration Points
Used by modular add/subtract and callers needing canonical nonnegative remainders for positive moduli.

## Risks and Test Signals
Correctness depends entirely on `mpi_fdiv_r()` and caller-provided divisor validity. Tests should verify positive modulus results are in `[0, m)`, negative dividend behavior, and aliasing through `mpi_fdiv_r()`.
