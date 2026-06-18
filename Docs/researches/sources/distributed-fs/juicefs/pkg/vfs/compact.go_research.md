# sources/distributed-fs/juicefs/pkg/vfs/compact.go

Purpose: compacts multiple metadata slices into a new contiguous chunk object.

Important APIs and types: `compactSizeHistogram`, helper `readSlice`, and exported `Compact(conf, store, slices, id, tierID)`.

Control flow and state: `Compact` waits while allocated memory minus store-used memory exceeds roughly 1.5 buffer sizes, sums slice lengths, records histogram data, opens a new chunk writer with writeback disabled, and copies each input slice into sequential positions. Zero-ID slices are written as zero-filled holes. Nonzero slices are read in block-sized pages with `readSlice`; each page is written to the new writer. When enough data accumulates, it flushes to the current position. Any read/write/finish failure aborts the writer.

Persistence and integration: compaction writes a new chunk to the configured `chunk.ChunkStore`, but metadata replacement is handled elsewhere by `meta.Compact`. It depends on chunk pages, writers, and meta slice layout.

Risks and test signals: `writer.FlushTo` errors panic instead of returning, which can crash compaction callers. Memory wait has no context cancellation. `compact_test.go` validates successful byte preservation and read-failure handling.
