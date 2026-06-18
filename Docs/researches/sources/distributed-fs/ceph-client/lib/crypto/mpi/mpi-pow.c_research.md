# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-pow.c

## Purpose
Implements modular exponentiation `res = base ^ exp mod mod`.

## Important APIs, Types, and Functions
- Exports `mpi_powm()`.
- Uses `mpihelp_divrem()`, `mpihelp_lshift()`, `mpihelp_rshift()`, `mpih_sqr_n_basecase()`, `mpih_sqr_n()`, `mpihelp_mul()`, `mpihelp_mul_karatsuba_case()`, and `karatsuba_ctx`.

## Control Flow and State
The function rejects zero modulus, handles zero exponent as `1 mod mod`, normalizes the modulus for division, reduces an oversized base, handles result/base/exp/mod aliasing with temporary limb storage, initializes result to base, then performs left-to-right square-and-multiply over exponent bits. Each square or multiply is reduced via `mpihelp_divrem()` when wider than the modulus. It alternates temporary buffers to avoid copies, calls `cond_resched()` in the loop, denormalizes the final result, and adjusts negative base odd-exponent results with `mod - result`.

## Dependencies and Integration Points
Used by public-key algorithms requiring modular exponentiation. It relies on MPI multiplication, division, Karatsuba scratch management, and scheduler cooperation.

## Risks and Test Signals
The algorithm is variable-time in exponent bits and operand sizes, so it is unsuitable for secret exponents without blinding or constant-time wrappers. Alias handling and temporary cleanup are complex. Tests should cover exponent zero, modulus one, base greater than modulus, negative base with odd/even exponent, alias combinations, threshold sizes around Karatsuba, allocation-failure injection, and reference modular exponent comparisons.
