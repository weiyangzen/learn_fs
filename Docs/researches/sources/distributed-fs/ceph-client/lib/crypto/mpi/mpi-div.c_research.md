# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-div.c

## Purpose
Implements high-level MPI truncated and floored division/remainder functions.

## Important APIs, Types, and Functions
- Public/internal functions: `mpi_fdiv_r()`, `mpi_tdiv_r()`, and `mpi_tdiv_qr()`.
- Uses `mpihelp_divmod_1()`, `mpihelp_mod_1()`, `mpihelp_divrem()`, `mpihelp_lshift()`, `mpihelp_rshift()`, `mpihelp_cmp()`, and allocation helpers.

## Control Flow and State
`mpi_fdiv_r()` computes a truncated remainder then adjusts it by the divisor when signs require floored semantics. `mpi_tdiv_qr()` resizes quotient/remainder, handles numerator smaller than denominator, optimizes single-limb divisors, copies overlapping operands to temporary marker buffers, normalizes multi-limb divisors/numerators by left shifting, calls `mpihelp_divrem()`, denormalizes the remainder, assigns signs, and frees temporary limb buffers.

## Dependencies and Integration Points
Used by `mpi_mod()`, modular multiplication, modular exponentiation, and callers that need quotient/remainder. Relies on low-level division preconditions that divisor high bit is normalized for multi-limb division.

## Risks and Test Signals
Division by zero is not explicitly guarded at this high level before helper paths in all cases; callers must provide valid divisors. Alias handling and sign correction are complex. Tests should include all alias combinations (`num == rem`, `den == rem`, `num == quot`), one-limb and multi-limb divisors, negative dividend/divisor floored remainder, exact division, numerator smaller than denominator, and randomized identity checks.
