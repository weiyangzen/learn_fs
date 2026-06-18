# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-cmp.c

## Purpose
Implements equal-size limb-array comparison for natural numbers.

## Important APIs, Types, and Functions
- Function: `int mpihelp_cmp(mpi_ptr_t op1_ptr, mpi_ptr_t op2_ptr, mpi_size_t size)`.

## Control Flow and State
The helper scans from most significant limb down to zero. It returns immediately on the first differing limb with `1` or `-1`, otherwise returns `0`.

## Dependencies and Integration Points
Used by MPI comparison, signed add/subtract magnitude decisions, division normalization/correction, and Karatsuba difference sign detection.

## Risks and Test Signals
The function is variable-time and should not be used for secret comparisons. Tests should include equal arrays, top-limb differences, low-limb differences, and all supported limb sizes.
