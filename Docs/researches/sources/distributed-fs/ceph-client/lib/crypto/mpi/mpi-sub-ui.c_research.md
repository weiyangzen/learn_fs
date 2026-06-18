# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-sub-ui.c

## Purpose
Implements subtraction of an unsigned long from an MPI.

## Important APIs, Types, and Functions
- Exports `mpi_sub_ui(MPI w, MPI u, unsigned long vval)`.
- Uses `mpi_resize()`, `mpihelp_add_1()`, `mpihelp_sub_1()`, and `mpi_normalize()`.

## Control Flow and State
If `u` is zero, the result is `-vval` or zero. For negative `u`, subtracting an unsigned value increases the magnitude and keeps a negative sign. For nonnegative `u`, it compares one-limb values to decide whether the result becomes negative or can subtract in place from `u`'s magnitude. It normalizes before returning.

## Dependencies and Integration Points
Used by code that needs small integer adjustments without constructing a full MPI for the small operand.

## Risks and Test Signals
The path assumes `unsigned long` fits one `mpi_limb_t` for comparison semantics; this is true for normal kernel MPI limb sizing. Tests should include `u=0`, `vval=0`, `u < vval`, `u == vval`, `u > vval`, negative `u`, and aliasing `w == u`.
