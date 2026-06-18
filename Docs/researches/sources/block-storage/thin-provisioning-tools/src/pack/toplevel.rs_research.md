# File Research: sources/block-storage/thin-provisioning-tools/src/pack/toplevel.rs

This file implements top-level metadata pack and unpack commands.

Pack format:
- Header contains magic, version, block size, and number of blocks.
- Payload is a sequence of zlib-compressed chunks.
- Each compressed chunk stores block number plus VM-packed metadata block data for recognized metadata blocks.

Important behavior:
- `pack()` divides input blocks into shuffled chunks across CPU-count worker threads.
- `crunch()` reads ranges, detects metadata block type, packs recognized blocks, and flushes compressed groups every 1024 metadata blocks.
- `unpack()` creates/sizes output, starts decode workers, reads compressed chunks, unpacks blocks, and writes them at original block numbers.
- Only blocks with recognized metadata checksums are packed; unknown blocks are omitted and unpack as zeroes due to file sizing.

Integration points:
- Uses `checksum::metadata_block_type`, `node_encode`, `pack::vm`, `file_utils`, and direct positional file I/O.

Risks and notes:
- `read_header()` error message for unsupported version formats the expected version rather than the actual version.
- Decode worker uses `unwrap()` on VM unpack and asserts recognized metadata type.
