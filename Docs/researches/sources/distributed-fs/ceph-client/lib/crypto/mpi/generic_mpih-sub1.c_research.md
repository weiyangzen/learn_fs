# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-sub1.c

## Purpose
Implements low-level subtraction of two equal-length limb arrays.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_sub_n(mpi_ptr_t res_ptr, mpi_ptr_t s1_ptr, mpi_ptr_t s2_ptr, mpi_size_t size)`.
- Returns final borrow.

## Control Flow and State
The negative-index loop adds prior borrow to the subtrahend, detects overflow, subtracts from the minuend, detects borrow from the subtraction, stores the result, and returns the combined final borrow.

## Dependencies and Integration Points
Used by high-level signed MPI subtraction, division correction, and Karatsuba difference calculations.

## Risks and Test Signals
Borrow handling and same-size precondition are critical. Tests should cover exact equality, one-limb borrow, full borrow propagation, and random reference comparisons.
