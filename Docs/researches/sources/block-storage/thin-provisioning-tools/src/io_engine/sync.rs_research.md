# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/sync.rs

This file implements `SyncIoEngine`, the direct synchronous file-backed metadata IO engine.

Important components:
- `SyncReader` streams logical 4 KiB block reads through larger pooled IO blocks.
- `SyncIoEngine` wraps an `O_DIRECT` file and metadata block count.
- `find_runs_nogap()` batches adjacent write blocks.

Important behavior:
- Opens files with `O_DIRECT`, optionally `O_EXCL`.
- `read()` and `write()` use positional single-block I/O.
- `read_many_()` combines requested blocks into `preadv` batches using `generate_runs()` and gap buffers.
- `write_many_()` uses contiguous write batches without gap insertion.
- `read_blocks()` maps logical blocks to larger IO blocks and uses handler callbacks.

Integration points:
- Main default `IoEngine` implementation re-exported by `io_engine/mod.rs`.
- Depends on `VectoredBlockIo`, gap generation, buffer pools, and adjacent chunking utilities.

Risks and notes:
- Gap reads intentionally read unrequested blocks into throwaway buffers.
- Uses assertions to enforce expected block ordering in some internal paths.
