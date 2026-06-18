# sources/distributed-fs/juicefs/pkg/meta/redis_csc.go

## Purpose

`redis_csc.go` adds optional Redis client-side caching for the Redis metadata engine. It caches inode attrs and directory entry lookups, subscribes to Redis invalidation push notifications, and hooks go-redis command processing to serve safe local reads and invalidate local entries after writes.

## Important APIs, Types, and Functions

`cachedEntry` stores an inode, entry generation term, and attr; an inode value of zero marks an in-flight lookup. `redisCache` stores the Redis client, prefix, capacity, expiry, preload count, pubsub subscription, inode LRU, entry LRU, and per-parent entry generation LRU. `newRedisCache`, `init`, `parse`, `entryName`, `entryTerm`, `bumpEntryTerm`, `HandlePushNotification`, `beforeProcess`, `afterProcess`, `ProcessHook`, `onInvalidateConnect`, `preloadCache`, and `bytesToString` are the main functions.

## Control Flow

Initialization obtains a standalone Redis client or the cluster master for the metadata prefix, installs `OnConnect`, subscribes to `__redis__:invalidate`, registers a push notification handler, and adds itself as a go-redis hook. On cache-specific reconnect, `onInvalidateConnect` purges all local caches, turns tracking off, and enables Redis `CLIENT TRACKING ON BCAST PREFIX <i-prefix> PREFIX <d-prefix>`.

For `GET i...`, `beforeProcess` returns cached inode bytes when present and not a mark; otherwise it stores an empty mark before allowing Redis access. `afterProcess` fills a marked inode cache entry from successful `GET`, removes inode cache entries after successful `SET`, and removes exact entry cache names after `HSET`/`HDEL` on directory hashes. Push invalidations remove inode cache entries or bump a directory parent generation, making older entry cache records stale without eagerly deleting every child name. `doLookup` in `redis.go` uses marks and generation comparisons to avoid filling stale directory entries. `preloadCache` optionally reads root directory entries after session creation.

## State and Persistence Behavior

All cache state is in-process and expirable. It persists no filesystem metadata and relies on Redis invalidation notifications plus TTL expiry to avoid stale reads. Entry generation terms are kept longer than entry values and are refreshed on access. The cache does not hook pipelines because `ProcessPipelineHook` returns nil.

## Dependencies and Integration Points

It depends on Redis RESP3/push notification support through go-redis, Hashicorp expirable LRU, `redisMeta.doLookup`, `doGetAttr`, and `doReaddir`, plus Redis server-side client tracking. It is configured from `newRedisMeta` query parameters `client-cache`, `client-cache-size`, `client-cache-expire`, and `client-cache-preload`.

## Risks and Edge Cases

Correctness depends on receiving invalidations for all metadata-writing connections and on generation checks preventing stale entry refills. The hook bypasses Redis only for simple `GET` inode commands, not pipelines. `bytesToString` is an unsafe zero-copy conversion, so cached byte slices must not be mutated after being returned as strings. The `DialHook` returning nil is unusual but acceptable for this hook shape. Preloading can conflict with concurrent root directory changes and is bounded by the generation checks.

## Test Signals

Tests should verify invalidation handling, TTL expiry, inode hook read-through and set invalidation, entry hook invalidation on hset/hdel, generation bump behavior, stale entry rejection while generation is active, idle generation expiry/refresh, and concurrent stale refill races. Existing `redis_csc_test.go` covers these signals against a live Redis server.
