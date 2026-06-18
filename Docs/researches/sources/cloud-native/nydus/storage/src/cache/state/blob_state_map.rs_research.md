# sources/cloud-native/nydus/storage/src/cache/state/blob_state_map.rs

Purpose: implements `BlobStateMap`, a concurrency adapter over a base `ChunkMap` or `RangeMap`. Base maps know whether data is ready; this wrapper adds pending/inflight tracking so concurrent readers/prefetchers do not download the same chunk or range repeatedly.

Important APIs and control flow: `Slot` stores `Inflight`/`Complete` with a `Mutex` and `Condvar`; waiters call `wait_for_inflight` with `SINGLE_INFLIGHT_WAIT_TIMEOUT`. `ChunkMap for BlobStateMap` delegates readiness, tracks pending entries in `inflight_tracer`, and implements `check_ready_and_mark_pending`: if ready, return true; if another slot exists, wait and retry; otherwise double-check readiness, insert a slot, and return false. `set_ready_and_clear_pending` updates the base map then clears the slot. Range implementations for `IndexedChunkMap` and `BlobRangeMap` use the base map to find not-ready indices, insert slots only for still-not-ready ranges, clear ranges, and wait on inflight ranges before rechecking readiness.

State and persistence behavior: inflight state is in-memory only in `Mutex<HashMap<I, Arc<Slot>>>`. Persistence depends entirely on the wrapped map (`IndexedChunkMap`/`BlobRangeMap` are bitmap-backed; `DigestedChunkMap` is memory-only). Clearing pending notifies all waiters regardless of success or failure path.

Dependencies and integration points: wraps `IndexedChunkMap`, `BlobRangeMap`, or `DigestedChunkMap` through `ChunkIndexGetter`; exposes downcast-based `as_range_map` for indexed maps; uses `StorageError::Timeout` to report wait expiration.

Risks and test signals: timed-out slots remain until the original owner clears pending, so failed download paths must always call `clear_pending`. The double-checks close common races around slot removal and readiness updates. Tests cover million-entry indexed/digested concurrency, inflight race and timeout behavior, range readiness/pending behavior, and all-ready transitions.
