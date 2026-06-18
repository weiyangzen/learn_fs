# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul3.c

## Purpose
Implements subtract-multiply by one limb: `res -= s1 * s2_limb`.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_submul_1(...)`.
- Uses `umul_ppmm()` and borrow detection.

## Control Flow and State
Each iteration multiplies one source limb, adds incoming carry to the low product, subtracts that from the destination limb, stores the result, and accumulates borrow/carry into the returned limb.

## Dependencies and Integration Points
Used heavily by `mpihelp_divrem()` for quotient correction and multi-limb division. Correctness directly affects modular reduction and exponentiation.

## Risks and Test Signals
Borrow propagation is the central risk. Tests should include divisor correction cases in division, all-ones operands, subtracting zero, and random division identity checks `q*d+r == n`.
