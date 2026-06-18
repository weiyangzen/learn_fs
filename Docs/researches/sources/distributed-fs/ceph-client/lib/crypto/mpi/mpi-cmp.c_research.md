# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-cmp.c

## Purpose
Implements MPI comparison against unsigned long and another MPI.

## Important APIs, Types, and Functions
- Exports `mpi_cmp_ui()` and `mpi_cmp()`.
- Uses `mpi_normalize()` and `mpihelp_cmp()`.

## Control Flow and State
Both functions normalize inputs before comparison. `mpi_cmp_ui()` treats negative MPIs as less than any unsigned value and multi-limb positive MPIs as greater than one-limb values. `mpi_cmp()` compares signs first, then limb counts with sign-aware polarity, then same-size limb values, negating the magnitude comparison for negative operands.

## Dependencies and Integration Points
Used by MPI arithmetic, public-key code, and reduction logic needing ordering.

## Risks and Test Signals
Comparison is variable-time and not suitable for secret-order decisions where timing matters. Functional tests should cover zero, positive/negative numbers, equal magnitudes with different signs where normalized zero should be signless by convention, and multi-limb boundary values.
