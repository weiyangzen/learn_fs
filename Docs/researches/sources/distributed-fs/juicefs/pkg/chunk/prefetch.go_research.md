## sources/distributed-fs/juicefs/pkg/chunk/prefetch.go

Purpose: small concurrent prefetch scheduler for cache reads.

Important APIs/types/functions: `prefetcher` tracks a bounded `pending` channel, a `busy` map to deduplicate keys, and an `op` callback. `newPrefetcher` starts `parallel` workers and sizes the queue to `max(parallel*4, 10)`. `fetch` enqueues a key if it is not already busy and drops it if the queue is full. Workers call `op` and clear the busy marker.

State and persistence: in-memory queue and busy map only.

Dependencies and integration points: used by `cachedStore.loadRange` to trigger full-block cache fill after range reads. The callback in `NewCachedStore` uses singleflight and cache insertion.

Risks and test signals: enqueue drops are silent by design. If `op` blocks, busy keys remain blocked until completion. Tests cover deduplication and bounded parallel execution.
