# sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_sentinel_store.go

## Purpose

`redis3/redis_sentinel_store.go` registers the Redis3 Sentinel store. It was read as a complete 49-line file.

## Important APIs, Types, and Functions

`Redis3SentinelStore` embeds `UniversalRedis3Store`. `GetName` returns `redis3_sentinel`. Initialization reads Sentinel addresses, master name, username/password, and DB, creates a failover client, and initializes Redsync.

## Control Flow

Startup configures go-redis failover retry/read/write timeouts and attaches a Redsync pool to the failover client.

## State and Persistence Behavior

Persistent state uses Redis3 entry keys and skiplist directory indexes; lock state is transient Redis lock keys.

## Dependencies and Integration Points

Depends on go-redis failover, Redsync, filer registration, and util config.

## Risks and Edge Cases

Failover can interrupt multi-command skiplist updates. The file does not validate the connection during initialize. Lock semantics during master promotion should be tested.

## Test Signals

No direct tests. Needed coverage includes Sentinel failover during insert/delete/list, lock acquisition failure, and metadata recovery.
