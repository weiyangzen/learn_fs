# sources/distributed-fs/juicefs/pkg/vfs/compact_test.go

Purpose: verifies compacted chunks contain the concatenated bytes of source slices and that missing source data fails compaction.

Important APIs and types: `TestCompact` constructs `chunk.Config`, a memory object store, `chunk.NewCachedStore`, source `meta.Slice` values, and calls `Compact`.

Control flow and state: the test writes 100 chunks with deterministic byte patterns and increasing sizes, compacts all slices into chunk id 1000, reads back each segment, and checks byte-for-byte correctness. It then removes one source object and expects a subsequent compaction attempt to fail.

Persistence and integration: uses in-memory object storage through the cached chunk store, testing the VFS compaction logic against real chunk store APIs without external services.

Risks and test signals: the test does not inject write or flush failures, matching the TODO in source. It also does not cover zero-fill slices, tier IDs, memory-throttle behavior, or panic path on `FlushTo` failure.
