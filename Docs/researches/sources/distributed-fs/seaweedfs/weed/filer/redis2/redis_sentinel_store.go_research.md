# sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_sentinel_store.go

## Purpose

`redis2/redis_sentinel_store.go` registers the Redis v2 Sentinel-backed filer store. It was read as a complete 48-line file.

## Important APIs, Types, and Functions

`Redis2SentinelStore` embeds `UniversalRedis2Store`. `GetName` returns `redis2_sentinel`. `Initialize` reads Sentinel addresses, `masterName`, username/password, database, and key prefix. `initialize` creates a `redis.NewFailoverClient` with retry/read/write timeouts.

## Control Flow

On startup it constructs failover options and stores the client/key prefix for universal entry and KV methods.

## State and Persistence Behavior

Persistent data follows the v2 schema in `universal_redis_store.go`. The sentinel client handles master discovery and failover externally.

## Dependencies and Integration Points

Uses go-redis failover options and SeaweedFS store registration/configuration.

## Risks and Edge Cases

`loadSuperLargeDirectories` is not called here, so `superLargeDirectoryHash` remains nil; map lookup is safe but configured super-large-directory behavior is unavailable for Sentinel v2. Failover consistency depends on Redis Sentinel and client behavior.

## Test Signals

No direct tests. Integration should exercise failover, key-prefix isolation, listing, and missing-server errors.
