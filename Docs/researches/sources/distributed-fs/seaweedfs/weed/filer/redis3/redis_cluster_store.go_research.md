# sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_cluster_store.go

## Purpose

`redis3/redis_cluster_store.go` registers the Redis3 cluster store. It was read as a complete 45-line file.

## Important APIs, Types, and Functions

`RedisCluster3Store` embeds `UniversalRedis3Store`. `GetName` returns `redis_cluster3`. `Initialize` reads cluster addresses, password, `useReadOnly`, and `routeByLatency`. `initialize` creates a go-redis cluster client and initializes `redsync` with a goredis pool.

## Control Flow

Startup configures cluster routing, assigns the shared client, then creates the distributed-lock manager required by Redis3 directory-child mutations.

## State and Persistence Behavior

Metadata state is handled by `UniversalRedis3Store` and skiplist child indexes. Redsync uses the same Redis client for lock keys.

## Dependencies and Integration Points

Depends on go-redis cluster, `go-redsync/redsync/v4`, `goredis/v9`, filer store registration, and util configuration.

## Risks and Edge Cases

No startup ping is performed. Distributed lock behavior in Redis Cluster depends on key slot placement and redsync configuration; directory-list lock keys must be reachable consistently.

## Test Signals

No direct tests. Integration should cover directory mutation under cluster, read-only routing interactions, and lock behavior during failover.
