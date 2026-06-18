# sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_cluster_store.go

## Purpose

`redis2/redis_cluster_store.go` registers the second-generation Redis cluster store. It was read as a complete 48-line file.

## Important APIs, Types, and Functions

`RedisCluster2Store` embeds `UniversalRedis2Store`. It registers as `redis_cluster2`, reads `addresses`, `username`, `password`, `keyPrefix`, `useReadOnly`, `routeByLatency`, and `superLargeDirectories`, and creates a `redis.NewClusterClient`.

## Control Flow

Initialization configures cluster routing options, assigns the universal client, stores the key prefix, and loads the super-large-directory skip list.

## State and Persistence Behavior

Actual metadata layout is handled by `UniversalRedis2Store`: prefixed entry keys and lexicographic sorted-set directory indexes except for configured super-large directories.

## Dependencies and Integration Points

Depends on go-redis cluster options, filer store registration, and `util.Configuration`.

## Risks and Edge Cases

There is no initialization ping. Super-large-directory bypass means those parents will not maintain a Redis directory index; behavior must match external assumptions for listing or separate indexing.

## Test Signals

No direct tests here. Redis cluster integration should include key-prefix isolation, username auth, read-only routing, and super-large-directory behavior.
