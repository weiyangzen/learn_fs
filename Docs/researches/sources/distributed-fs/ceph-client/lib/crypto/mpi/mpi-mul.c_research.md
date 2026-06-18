# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mul.c

## Purpose
Implements high-level signed MPI multiplication and modular multiplication.

## Important APIs, Types, and Functions
- Exports `mpi_mul()` and `mpi_mulm()`.
- Uses `mpihelp_mul()`, `mpi_alloc_limb_space()`, `mpi_assign_limb_space()`, and `mpi_tdiv_r()`.

## Control Flow and State
`mpi_mul()` orders operands by limb count, handles destination aliasing by allocating temporary operand or result limb space, calls low-level multiplication if the smaller operand is nonzero, adjusts result size based on top carry, assigns temporary result space if used, sets sign as XOR of operand signs, and frees temporary operands. `mpi_mulm()` multiplies then reduces by `m`.

## Dependencies and Integration Points
Used by public-key arithmetic and modular exponentiation. It depends on `mpihelp_mul()` requiring `usize >= vsize` and non-overlapping product/input buffers.

## Risks and Test Signals
Alias handling and error cleanup are primary risks. A zero product should conventionally have sign zero; tests should check signed zero normalization expectations. Test with `w == u`, `w == v`, `u == v`, zero operands, negative operands, modular multiplication, and random reference multiplication.
