# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-rshift.c

## Purpose
Implements limb-array right shift by a nonzero bit count smaller than one limb.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_rshift(mpi_ptr_t wp, mpi_ptr_t up, mpi_size_t usize, unsigned cnt)`.
- Returns bits shifted out of the least significant limb.

## Control Flow and State
The helper combines adjacent source limbs from low to high, writes right-shifted result limbs, and returns the outgoing low bits. It adjusts the destination pointer so in-place shifting is safe when `wp <= up`.

## Dependencies and Integration Points
Used by MPI right shift, division denormalization, and modular exponentiation final reduction. Preconditions require `0 < cnt < BITS_PER_MPI_LIMB`.

## Risks and Test Signals
Risks are invalid zero/full-limb shifts and wrong overlap direction. Tests should cover every bit count, one-limb/multi-limb values, returned low bits, and in-place shifts.
