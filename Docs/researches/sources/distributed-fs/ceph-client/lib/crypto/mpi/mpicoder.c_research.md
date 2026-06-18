# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpicoder.c

## Purpose
Encodes and decodes MPIs from raw big-endian byte streams, length-prefixed external buffers, and scatterlists.

## Important APIs, Types, and Functions
- Exports `mpi_read_raw_data()`, `mpi_read_from_buffer()`, `mpi_read_buffer()`, `mpi_get_buffer()`, `mpi_write_to_sgl()`, and `mpi_read_raw_from_sgl()`.
- Uses `MAX_EXTERN_MPI_BITS` set to 16384 bits.
- Uses scatterlist mapping iteration for SG input/output and endian conversion for limb serialization.

## Control Flow and State
Raw readers skip leading zero bytes, compute significant bits, reject oversized external MPIs, allocate an MPI, and fill limbs from most-significant bytes into little-endian limb order. `mpi_read_from_buffer()` first parses a two-byte bit count. `mpi_read_buffer()` serializes an MPI to a caller buffer, reporting required length on overflow and optionally returning sign. `mpi_get_buffer()` allocates a buffer and delegates serialization. `mpi_write_to_sgl()` writes optional leading zero padding followed by big-endian limbs into SG entries. `mpi_read_raw_from_sgl()` scans leading zeroes across SG entries, computes size, allocates, and fills limbs.

## Dependencies and Integration Points
Used by public-key parsers, signature verification, and key import/export code. Depends on scatterlist APIs, endian helpers, count-zero helpers, and MPI allocation utilities.

## Risks and Test Signals
Risks include SG iterator edge cases, leading-zero accounting, overflow reporting, and size limit enforcement. Tests should cover empty/zero values, leading zeros, maximum allowed size and one byte over, short length-prefixed buffers, buffer overflow reporting, SG boundaries at every byte offset, and round-trip encode/decode.
