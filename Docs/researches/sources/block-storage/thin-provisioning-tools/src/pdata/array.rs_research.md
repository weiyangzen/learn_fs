# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array.rs

This file defines persistent array block format helpers and errors.

Important structures:
- `ArrayBlockHeader`: checksum placeholder, max entries, actual entries, value size, block number.
- `ArrayBlock<V>`: header plus typed values.
- `ArrayError`: path-aware errors for I/O, array block validation, value validation, index context, aggregation, and B-tree errors.

Important behavior:
- `unpack_array_block()` validates value size, max entries fitting in metadata block size, and `nr_entries <= max_entries`, then parses typed values.
- `pack_array_block()` serializes header and values.
- `calc_max_entries<V>()` computes maximum typed entries per 4 KiB block.

Integration points:
- Used by array walkers, era array dump/check/invalidate, and array builder.
- Depends on `pdata::unpack::{Pack, Unpack}` and `io_engine::BLOCK_SIZE`.

Risks and notes:
- Header checksum is written as zero here; callers must apply metadata block checksum after packing.
- Error display concatenates aggregate errors without separators.
