# sources/distributed-fs/seaweedfs/weed/filer/redis/redis_store.go

## Purpose

`redis/redis_store.go` registers the original single-node Redis filer store. It was read as a complete 36-line file.

## Important APIs, Types, and Functions

`RedisStore` embeds `UniversalRedisStore`. `GetName` returns `redis`. `Initialize` reads `address`, `password`, and `database`; `initialize` creates a `redis.NewClient`.

## Control Flow

The file is startup glue only: `init` registers the store, configuration is converted into Redis options, and later filer operations use the embedded universal implementation.

## State and Persistence Behavior

The connection points at one Redis DB. Metadata keys are full paths and directory children are stored in Redis sets by `universal_redis_store.go`.

## Dependencies and Integration Points

Depends on `go-redis/v9`, SeaweedFS `filer` registration, and `util.Configuration`.

## Risks and Edge Cases

Initialization does not validate the server. There is no username/TLS/key-prefix support in this v1 file, so deployments needing those must use newer Redis store variants.

## Test Signals

No direct test in this subset. Functional evidence should come from generic filer store tests against a real Redis instance.
