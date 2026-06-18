# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-bit.c

## Purpose
Provides bit-level MPI operations: normalization, bit length, bit test, bit set, and right shift.

## Important APIs, Types, and Functions
- Exports `mpi_normalize()`, `mpi_get_nbits()`, `mpi_test_bit()`, `mpi_set_bit()`, and `mpi_rshift()`.
- Uses `count_leading_zeros()`, `mpihelp_rshift()`, `RESIZE_IF_NEEDED()`, and `MPN_NORMALIZE()`.

## Control Flow and State
Normalization trims leading zero limbs in place. `mpi_get_nbits()` normalizes and computes significant bits from the top limb. `mpi_test_bit()` indexes the relevant limb and bit. `mpi_set_bit()` grows and zero-fills as needed before setting the bit. `mpi_rshift()` handles in-place and out-of-place shifts, splits whole-limb and intra-limb shifts, and normalizes the result.

## Dependencies and Integration Points
Used throughout MPI comparison, exponentiation, serialization, and public-key routines. The helpers depend on limb-size macros and allocation routines.

## Risks and Test Signals
Risks include preserving sign on right shift, zeroing newly exposed limbs, and avoiding `mpihelp_rshift()` with zero bit count. Tests should cover bit positions across limb boundaries, zero MPI, in-place/out-of-place shifts, large shifts that clear the number, and random reference checks.
