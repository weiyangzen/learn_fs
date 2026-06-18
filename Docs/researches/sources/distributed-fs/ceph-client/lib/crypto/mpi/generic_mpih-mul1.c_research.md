# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul1.c

## Purpose
Implements multiplication of a limb array by one limb.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_mul_1(mpi_ptr_t res_ptr, mpi_ptr_t s1_ptr, mpi_size_t s1_size, mpi_limb_t s2_limb)`.
- Uses `umul_ppmm()` from `longlong.h` to obtain high and low product limbs.

## Control Flow and State
The negative-index loop multiplies each source limb by `s2_limb`, adds carry to the low product, calculates the new carry as high product plus carry-out, stores the low limb, and returns final carry.

## Dependencies and Integration Points
Critical base helper for schoolbook multiplication, squaring, and modular exponentiation. Depends on `longlong.h` providing correct `umul_ppmm()` for the active architecture.

## Risks and Test Signals
Risks include broken architecture multiply macros and carry propagation bugs. Tests should include multiplying by 0, 1, maximum limb, carry-heavy operands, and cross-checking `mpi_mul()` for random numbers.
