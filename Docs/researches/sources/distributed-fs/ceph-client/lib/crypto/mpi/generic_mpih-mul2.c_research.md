# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul2.c

## Purpose
Implements add-multiply by one limb: `res += s1 * s2_limb`.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_addmul_1(...)`.
- Uses `umul_ppmm()` and carry detection on both product+carry and result+product additions.

## Control Flow and State
For each source limb the helper multiplies, adds incoming carry into the low product, adds the destination limb, stores the sum, and returns final carry. No persistent state is kept.

## Dependencies and Integration Points
Used by schoolbook multiplication, Karatsuba recomposition, squaring, and odd-size handling. It depends on destination space being valid and overlap restrictions controlled by callers.

## Risks and Test Signals
Incorrect carry accumulation corrupts high limbs in all multiplication paths. Test with random long operands, all-ones operands, single-limb and multi-limb values, and compare against reference big integer multiplication.
