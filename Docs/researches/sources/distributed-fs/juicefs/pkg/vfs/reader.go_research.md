# sources/distributed-fs/juicefs/pkg/vfs/reader.go

Purpose: implements VFS file reading, chunk-slice reads, readahead, read-buffer accounting, invalidation, truncation, retry, and cleanup.

Important APIs and types: states `NEW`, `BUSY`, `REFRESH`, `BREAK`, `READY`, `INVALID`; interfaces `FileReader` and `DataReader`; `frange`; `sliceReader`; `session`; `fileReader`; `dataReader`; constructors and methods `NewDataReader`, `Open`, `Read`, `Truncate`, `Invalidate`, `Close`, and slice read helpers.

Control flow and state: each open file has a linked list of `sliceReader` requests guarded by the file mutex. `fileReader.Read` throttles if buffer use is high, computes the requested range, removes stale readahead requests, splits around existing slices, prepares missing requests, updates sequential session readahead, and waits for slice IO. `sliceReader.run` reads metadata slices, uses `dataReader.Read` to fill a page, retries transient metadata/read mismatches, and transitions state. `dataReader` tracks all open readers per inode, periodically releases idle buffers, invalidates overlapping slices, and reads multiple metadata slices concurrently.

Persistence and integration: state is in memory; data comes from `meta.Meta` slice maps and `chunk.ChunkStore`. Handles in `handle.go` own reader lifetimes.

Risks and test signals: concurrency is delicate: state transitions call `runtime.Goexit`, global `readBufferUsed` spans all readers, and BUSY invalidation deliberately does not cancel immediately. `context_cancellation_test.go` documents close/invalidate behavior. No direct tests cover readahead tuning.
