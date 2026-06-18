# sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_store.go

## Purpose

`redis3/redis_store.go` registers the Redis3 single-node store with optional mTLS and Redsync locking. It was read as a complete 84-line file.

## Important APIs, Types, and Functions

`Redis3Store` embeds `UniversalRedis3Store`. `Initialize` reads address, password, database, and mTLS paths. `initialize` optionally creates TLS config, constructs `redis.NewClient`, and initializes `redsync`.

## Control Flow

With mTLS enabled, it loads client cert/key, CA certs, parses the Redis host, and sets TLS 1.2+ options before constructing the client. Otherwise it creates a plain Redis client. Both branches create the lock manager.

## State and Persistence Behavior

Connection and distributed lock state are configured here; metadata persistence is delegated to Redis3 universal/skiplist files.

## Dependencies and Integration Points

Depends on TLS/x509 libraries, go-redis, Redsync goredis adapter, `glog.Fatalf`, and SeaweedFS configuration.

## Risks and Edge Cases

Configuration errors terminate the process via `Fatalf`. There is no username or key-prefix support in this Redis3 single-node variant. Startup does not ping Redis.

## Test Signals

Needed tests include mTLS success/failure, redsync initialization, and directory child operations through the full Redis3 store.
