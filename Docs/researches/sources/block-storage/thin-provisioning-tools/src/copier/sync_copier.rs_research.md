# File Research: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier.rs

This file implements `SyncCopier`, a block-oriented copier with ordered, aggregated reads and a writer thread.

`SyncCopier<T>` copies batches of `CopyOp` values using `ReadBlocks` and `WriteBlocks` abstractions. It sorts read and write requests by device location, aggregates adjacent operations into larger I/O calls, and pipelines reading with a single writer thread through a bounded channel.

Important behavior:
- Rejects configurations where `block_size > buffer_size`.
- Supports separate source/destination devices and `in_file()` copying behind one mutex for same-file operations.
- Page-aligns optional source and destination byte offsets.
- `do_reads()` sorts source blocks, aggregates adjacent reads, and records per-op success in a `RoaringBitmap`.
- `do_writes()` writes only blocks whose reads succeeded, similarly sorting and aggregating destination writes.
- `copy()` chunks work by buffer capacity, reports read/write errors, joins the writer thread, and commits final stats.

Integration points:
- Generic over `ReadBlocks + WriteBlocks + Send`.
- `from_path()` opens files with `O_DIRECT` and wraps `File` into the chosen I/O adapter.
- Used with `SimpleBlockIo` or `VectoredBlockIo` depending on caller needs.

Risks and notes:
- `progress.update(&stats)` in the writer thread passes cumulative shared stats, while `inc_stats()` is called at the end with the final stats; progress consumers must tolerate that pattern.
- Same-file copying serializes read/write through a shared mutex, which avoids concurrent same-file access but limits parallelism.
