# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-add1.c

## Purpose
Implements `mpihelp_add_n()`, the low-level addition of two equal-length limb arrays.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_add_n(mpi_ptr_t res_ptr, mpi_ptr_t s1_ptr, mpi_ptr_t s2_ptr, mpi_size_t size)`.
- Uses `mpi_limb_t`, `mpi_ptr_t`, and signed `mpi_size_t` from `mpi-internal.h`.

## Control Flow and State
The function rewrites pointers so a negative loop index runs from `-size` to `-1`. For each limb it adds prior carry to the second source, detects carry, adds the first source, combines carry-out, and stores the result. It returns final carry. It has no persistent state.

## Dependencies and Integration Points
Used by higher-level MPI add, multiply, division correction, and Karatsuba code. Depends on unsigned wraparound semantics for carry detection.

## Risks and Test Signals
Risks are size precondition violations and aliasing combinations not expected by callers. Tests should cover all-carry, no-carry, in-place result/source overlap where callers permit it, and comparison against arbitrary-precision reference addition.
