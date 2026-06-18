# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpiutil.c

## Purpose
Provides allocation, resizing, freeing, and copying utilities for MPI objects and their limb arrays.

## Important APIs, Types, and Functions
- Exports `mpi_alloc()` and `mpi_free()`.
- Defines `mpi_alloc_limb_space()`, `mpi_free_limb_space()`, `mpi_assign_limb_space()`, `mpi_resize()`, and `mpi_copy()`.

## Control Flow and State
`mpi_alloc()` allocates the MPI header and optional limb storage, initializing metadata. `mpi_resize()` grows only; it allocates zeroed new limb space, copies old allocated limbs, and frees old storage sensitively. `mpi_assign_limb_space()` replaces owned limb storage. `mpi_free()` clears limb storage, warns on invalid flags, and frees the header. `mpi_copy()` duplicates metadata and limbs but clears immutable/constant flags.

## Dependencies and Integration Points
All MPI operations depend on these memory helpers. They use kernel allocation APIs and `kfree_sensitive()` for limb data.

## Risks and Test Signals
Integer overflow in `nlimbs * sizeof(mpi_limb_t)` would be a concern for unchecked external sizes, but external decoders cap input size. Copying `alloced` limbs during resize instead of `nlimbs` relies on old allocation being initialized or non-sensitive cleared on free. Tests should include allocation failure, zero-limb allocation, resize grow/no-op, copy independence, and sensitive free paths.
