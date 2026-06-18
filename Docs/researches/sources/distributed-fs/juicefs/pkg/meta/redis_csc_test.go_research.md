# sources/distributed-fs/juicefs/pkg/meta/redis_csc_test.go

## Purpose

`redis_csc_test.go` tests Redis client-side cache behavior for inode cache invalidation, entry cache invalidation, entry generation staleness checks, expiry, and concurrent refill safety.

## Important APIs, Types, and Functions

`mockRedisCSCMeta` creates a Redis metadata engine at `127.0.0.1:6379/10?client-cache=true`. `TestRedisCache` contains subtests for invalidation handling, cache expiration, inode hook, entry hook, entry generation invalidation, idle term expiry, term refresh on access, mark refill rules, stale entry rejection, and concurrent stale refill attempts. It uses `require` from testify and Redis push notification types.

## Control Flow

The test flushes Redis DB 10, then manipulates cache internals and Redis keys directly. It adds inode attrs or entry values into LRUs, mutates Redis with `SET`, `HSET`, and `HDEL`, sleeps where necessary for async invalidations or expiry, and asserts cache entries are removed or considered stale. Several subtests construct standalone `redisCache` instances with very short expiry to check LRU timing without Redis. The concurrency subtest starts multiple goroutines that attempt to refill an old generation mark and verifies they cannot overwrite a newer mark.

## State and Persistence Behavior

The test mutates a live local Redis database and in-memory cache objects. `FlushAll` clears the Redis instance, not only DB 10, which makes this test unsuitable for shared Redis environments. Most assertions inspect process-local LRU state rather than persisted metadata.

## Dependencies and Integration Points

It depends on Redis client-side tracking behavior, async invalidation timing, go-redis hooks from `redis_csc.go`, `Attr.Marshal`/`Unmarshal`, and the test Redis server. It validates behavior that `redis.go` relies on for `doLookup` cache marks and term checks.

## Risks and Edge Cases

Time-based sleeps make the test sensitive to slow Redis or overloaded CI. `FlushAll` can interfere with other Redis-backed tests if run in parallel. Push invalidation behavior depends on Redis server version and protocol behavior. Short expiry tests need enough margin to avoid flakes, and the current sleeps are deliberately multiples of expiry.

## Test Signals

The file gives direct evidence that cached inode reads are served through the Redis hook, `SET` invalidates inode cache, `HSET`/`HDEL` invalidate exact entry names, parent invalidation bumps terms, stale cache entries are not accepted after a term bump, refill requires an existing mark and current generation, and concurrent old-generation refills do not overwrite a newer mark.
