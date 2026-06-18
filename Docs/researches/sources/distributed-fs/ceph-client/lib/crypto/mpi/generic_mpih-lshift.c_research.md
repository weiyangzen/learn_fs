# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-lshift.c

## Purpose
Implements limb-array left shift by a nonzero bit count smaller than one limb.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_lshift(mpi_ptr_t wp, mpi_ptr_t up, mpi_size_t usize, unsigned int cnt)`.
- Returns bits shifted out of the most significant limb.

## Control Flow and State
Starting from the most significant limb, it combines high/low source limbs with `cnt` and `BITS_PER_MPI_LIMB - cnt`, stores the shifted result, and returns the outgoing high bits. The destination is adjusted by one so the loop can fill overlapping output safely when `wp >= up`.

## Dependencies and Integration Points
Used by division normalization, modular exponentiation, and MPI bit operations. Preconditions require `0 < cnt < BITS_PER_MPI_LIMB` and correct overlap direction.

## Risks and Test Signals
Calling with `cnt == 0`, `cnt >= limb bits`, or wrong overlap direction is undefined for this helper. Tests should cover all shift counts 1 through limbbits-1, one-limb and multi-limb inputs, returned carry bits, and in-place left shifts.
