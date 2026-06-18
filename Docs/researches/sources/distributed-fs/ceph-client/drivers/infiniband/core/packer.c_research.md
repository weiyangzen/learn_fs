# sources/distributed-fs/ceph-client/drivers/infiniband/core/packer.c

## Purpose
`packer.c` is the generic InfiniBand attribute marshalling helper. It translates between C structures and the network/MAD wire buffers described by arrays of `struct ib_field`. The file is deliberately small but sits underneath SA query record packing and unpacking, so bit offsets, endianness, and zero filling are the critical behavior.

## Important APIs, types, and functions
- `ib_pack(desc, desc_len, structure, buf)` exports structure-to-buffer packing.
- `ib_unpack(desc, desc_len, buf, structure)` exports buffer-to-structure unpacking.
- `value_read()` reads 1, 2, 4, or 8 byte fields from a structure and returns a host-order `u64`, interpreting multi-byte fields as big-endian.
- `value_write()` writes 8, 16, 32, or 64 bit values back to structure fields in big-endian form.
- The controlling type is external `struct ib_field` from `<rdma/ib_pack.h>`, including `offset_words`, `offset_bits`, `size_bits`, `struct_offset_bytes`, `struct_size_bytes`, and `field_name`.

## Control flow and behavior
For each descriptor, `ib_pack()` chooses a <=32 bit, <=64 bit, or bulk byte-copy path. Narrow fields are shifted into their descriptor bit position and ORed into the destination word after clearing the target mask. Fields with `struct_size_bytes == 0` represent reserved or zero fields and cause the target bits or bytes to be zeroed. Wider fields require byte alignment; otherwise the code warns but still copies by byte count. `ib_unpack()` mirrors this logic but skips descriptors that do not map to structure storage.

## State, persistence, and dependencies
The file has no persistent state. Its only visible side effects are writes to caller-supplied buffers and `pr_warn()` messages for unsupported field sizes or unaligned wide fields. It depends on Linux endian helpers, `memcpy`/`memset`, and the RDMA field descriptor ABI.

## Integration points
SA path, multicast member, GUID info, service, and class-port records in `sa_query.c` use these helpers to keep the record layout tables declarative. Any consumer that defines an `ib_field` table can reuse the same pack/unpack routines.

## Risks and test signals
Important risks are off-by-one bit offsets, unsupported field widths, non-zero garbage in caller-provided buffers for fields not described by the table, and endian mismatches in structure definitions. Useful tests are round-trip pack/unpack for every descriptor table, reserved-field zeroing checks, boundary tests for 32 and 64 bit fields, and KUnit-style tests for warning paths on invalid descriptor sizes or unaligned wide fields.
