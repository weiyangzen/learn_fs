# sources/cloud-native/nydus/storage/src/cache/worker.rs

Purpose: implements asynchronous cache prefetch worker infrastructure. It converts Nydus prefetch configuration into worker threads, a request channel, optional bandwidth limiting, metrics updates, and blocking handlers for blob-range and filesystem-range prefetch.

Important APIs and control flow: `AsyncPrefetchConfig::from` copies enable/thread/batch/bandwidth settings. `AsyncPrefetchMessage` carries blob-compressed prefetch, filesystem range prefetch, test ping, and rate-limiter messages. `AsyncWorkerMgr::new` creates a channel, zero-permit semaphore, retry counter, counters, and optional leaky-bucket limiter sized at least `RAFS_MAX_CHUNK_SIZE`. `start` spawns configured threads when enabled. Each thread installs a runtime with `with_runtime`, adds one semaphore permit, receives messages, applies rate limiting, and spawns blocking handlers while holding an owned semaphore token. `send_prefetch_message` increments inflight only when enabled. Stop closes the channel and wakes workers until the worker count reaches zero.

State and persistence behavior: all worker state is in-memory atomics plus the channel. `retry_times` globally limits retries for failed `BlobObject::fetch_range_compressed`; retry is scheduled on the global async runtime after one second.

Dependencies and integration points: used by filecache and fscache managers. Handlers call `BlobObject::fetch_range_compressed`, `BlobObject::prefetch_chunks`, or `BlobCache::prefetch_range`, update `BlobcacheMetrics`, and honor `BlobCache::is_prefetch_active`.

Risks and test signals: if a blob is inactive after acquiring a semaphore token, the code drops the message without an explicit token drop in that branch scope only at scope end; inflight is decremented after dispatch, not after blocking work completes. Stop relies on channel close and worker count polling. Tests cover worker start/stop and pings, disabled send behavior, inflight increment, consumed bandwidth accounting, and rate limiter delay/inflight behavior.
