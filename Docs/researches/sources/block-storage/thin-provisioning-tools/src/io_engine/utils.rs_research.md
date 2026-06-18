# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/utils.rs

This file defines block-I/O adapters and logical-to-physical IO-block mapping helpers.

Important components:
- `ReadBlocks` and `WriteBlocks` traits.
- `VectoredBlockIo<T: VectoredIo>` for vectored reads/writes.
- `SimpleBlockIo<T: FileExt>` for per-block positional I/O.
- `map_small_blocks_to_io()` maps sorted logical 4 KiB blocks to larger IO block bitmasks.
- `process_io_block_result()` splits a larger IO block result back into logical block callbacks.

Important behavior:
- `VectoredBlockIo::read_blocks()` retries after failures by skipping the first failing block, supports optional partial-read acceptance, and zero-fills partial buffers.
- `VectoredBlockIo::write_blocks()` skips failing blocks and continues.
- `SimpleBlockIo` returns one result per buffer using exact positional reads/writes.

Integration points:
- Used by copier code, sync/async IO engines, and tests.
- Bridges `FileExt`, `VectoredIo`, and higher-level copier abstractions.

Risks and notes:
- Some write errors are labeled `"read failed"` in `VectoredBlockIo::write_blocks()`.
- `map_small_blocks_to_io()` assumes sorted/grouped input for optimal mapping.
