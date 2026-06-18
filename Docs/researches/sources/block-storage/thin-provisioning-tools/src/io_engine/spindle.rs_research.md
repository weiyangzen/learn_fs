# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/spindle.rs

This file implements `SpindleIoEngine`, an IO engine optimized for slow random-access disks.

It preloads selected metadata blocks, compresses them into memory, and serves reads from the compressed cache when possible. Reads/writes outside cached metadata blocks fall back to direct synchronous file I/O.

Important behavior:
- Scans a `RoaringBitmap` of metadata-interest blocks.
- Reads present ranges in chunks, sends them to a packer thread, and compresses recognized metadata blocks.
- `pack_block()` uses metadata block type to choose pack format.
- `read_()` unpacks cached blocks or reads from disk.
- `write_()` removes stale cache entry and writes through to disk.
- Public `SpindleIoEngine` wraps mutable state in `RwLock`.

Integration points:
- Uses pack VM/node encoding, checksum block typing, `RunIter`, and direct-I/O files.
- Implements `IoEngine`.

Risks and notes:
- `read_blocks()` is unimplemented.
- Cache memory can be large by design.
- Writes invalidate only the exact block cache entry.
