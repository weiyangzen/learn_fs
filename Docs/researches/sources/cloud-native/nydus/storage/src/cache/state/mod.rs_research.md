# sources/cloud-native/nydus/storage/src/cache/state/mod.rs

Purpose: defines the public cache-state abstraction layer: `ChunkMap` for per-chunk readiness/pending state and `RangeMap` for batch readiness over chunk indices or data-address ranges. It re-exports concrete state map implementations used by cache managers.

Important APIs and control flow: `ChunkMap` requires `is_ready` and provides default non-pending behavior, combined `is_ready_or_pending`, unsupported defaults for pending mutation methods, `is_persist`, and optional `as_range_map`. `RangeMap` exposes all-ready checks, range readiness, pending discovery/marking, setting ranges ready, clearing pending, and waiting for ranges. Defaults return false, `enosys`, or no-op behavior unless an implementation overrides them.

State and persistence behavior: this file owns no state. It establishes contracts that implementations must honor: `check_ready_and_mark_pending` returning `Ok(false)` means the caller owns an inflight slot and must later call `set_ready_and_clear_pending` or `clear_pending`; range pending methods follow the same ownership model.

Dependencies and integration points: used by `BlobCache` implementations, `FileCacheEntry`, prefetch paths, `BlobDevice::all_chunks_ready`, and concrete maps `BlobStateMap`, `BlobRangeMap`, `DigestedChunkMap`, `IndexedChunkMap`, and `NoopChunkMap`.

Risks and test signals: unsupported defaults panic for some `ChunkMap` methods, so cache code must only call pending methods on maps wrapped by `BlobStateMap` or concrete implementations that support them. The comments document concurrency expectations but enforcement is implementation-specific. Tests live in concrete modules.
