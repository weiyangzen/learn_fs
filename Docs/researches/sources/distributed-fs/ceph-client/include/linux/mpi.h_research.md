<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpi.h -->
# sources/distributed-fs/ceph-client/include/linux/mpi.h

## Purpose
`mpi.h` declares the kernel multi-precision integer library, derived from GnuPG/GMP-style limb arithmetic, for cryptographic and big-number operations.

## Important APIs, Types, and Functions
It defines limb sizing macros, `mpi_limb_t`, `mpi_limb_signed_t`, `struct gcry_mpi`, and `MPI`. APIs cover allocation (`mpi_alloc()`, `mpi_free()`, `mpi_resize()`, `mpi_copy()`), encoding/decoding (`mpi_read_raw_data()`, `mpi_read_from_buffer()`, `mpi_read_raw_from_sgl()`, `mpi_get_buffer()`, `mpi_read_buffer()`, `mpi_write_to_sgl()`), arithmetic (`mpi_add()`, `mpi_sub()`, `mpi_addm()`, `mpi_subm()`, `mpi_mul()`, `mpi_mulm()`, `mpi_mod()`, `mpi_powm()`), division/remainder (`mpi_tdiv_r()`, `mpi_fdiv_r()`), comparison (`mpi_cmp_ui()`, `mpi_cmp()`), bit operations (`mpi_normalize()`, `mpi_get_nbits()`, `mpi_test_bit()`, `mpi_set_bit()`, `mpi_rshift()`), and `mpi_get_size()`.

## Control Flow and State
Callers allocate an `MPI`, read or construct limb data, perform arithmetic, and serialize results into buffers or scatterlists. Most functions return negative errors on allocation or invalid input failure.

## State and Persistence Behavior
`struct gcry_mpi` owns dynamically allocated limb storage. Sensitive values may be flagged for secure memory by implementation conventions. The header itself does not persist data, but consumers may encode MPI values into keys/signatures.

## Dependencies and Integration Points
It depends on Linux integer types and scatterlists. It is typically used by crypto, public-key, signature, and key parsing code.

## Risks
Big-number code is security-sensitive: length/sign mistakes, non-normalized values, scatterlist truncation, and allocation failures can break signature verification. Arithmetic may not be constant-time unless implementations guarantee it.

## Test Signals
Known-answer cryptographic tests, encode/decode round trips, scatterlist boundary cases, modular exponentiation, negative number handling, allocation failure injection, and 32-bit/64-bit limb builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpi.h -->
