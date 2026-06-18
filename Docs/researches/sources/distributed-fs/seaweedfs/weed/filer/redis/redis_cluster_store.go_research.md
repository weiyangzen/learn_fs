# sources/distributed-fs/seaweedfs/weed/filer/redis/redis_cluster_store.go

## Purpose

`redis/redis_cluster_store.go` registers and initializes the original Redis cluster filer store. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`RedisClusterStore` embeds `UniversalRedisStore`. `init` appends it to `filer.Stores`. `GetName` returns `redis_cluster`. `Initialize` reads `addresses`, `password`, `useReadOnly`, and `routeByLatency`; `initialize` creates a `redis.NewClusterClient`.

## Control Flow

Startup sets defaults for read-only and latency routing, builds cluster options, and assigns the universal Redis client used by entry and KV methods.

## State and Persistence Behavior

The file owns no data schema itself; persistence is in Redis keys managed by `UniversalRedisStore`.

## Dependencies and Integration Points

Depends on `github.com/redis/go-redis/v9`, `filer.Stores`, and `util.Configuration`. It integrates the common Redis backend with SeaweedFS store discovery.

## Risks and Edge Cases

No ping or connection validation occurs during initialize, so misconfiguration surfaces on first operation. Cluster read-only/latency routing can affect consistency expectations for metadata reads.

## Test Signals

No direct test in this subset. Store-suite coverage would need a live Redis Cluster with directory create/list/delete and KV operations.
