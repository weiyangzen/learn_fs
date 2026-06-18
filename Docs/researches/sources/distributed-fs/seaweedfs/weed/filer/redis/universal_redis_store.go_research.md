# sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store.go

## Purpose

`redis/universal_redis_store.go` implements the original Redis metadata store shared by single-node and cluster Redis stores. It was read as a complete 218-line file.

## Important APIs, Types, and Functions

`UniversalRedisStore` owns a `redis.UniversalClient`. It implements `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, unsupported `ListDirectoryPrefixedEntries`, no-op transaction methods, `genDirectoryListKey`, and `Shutdown`.

## Control Flow

Entries are encoded with `Entry.EncodeAttributesAndChunks`, optionally gzipped for many chunks, and stored at the full path with Redis TTL. Parent directory membership is tracked separately in a Redis set whose key is `dir + "\x00"`. Listing loads all set members, filters by start name, sorts client-side, applies limit, fetches each entry, skips missing children, and lazily removes expired entries.

## State and Persistence Behavior

Metadata and KV data persist in Redis. Directory children are eventually consistent with entry keys because insert/delete update two independent Redis records and transactions are no-ops.

## Dependencies and Integration Points

Integrates with `filer.Entry` encode/decode, `filer_pb.ErrNotFound`, `util.MaybeGzipData`, `glog`, and `redis.UniversalClient`.

## Risks and Edge Cases

Large directories are expensive because `SMembers` loads the full set and sorting is client-side. Partial failures can leave stale directory set entries. TTL cleanup happens during list scans and may not remove directory references until a list occurs.

## Test Signals

No direct tests in this subset. Needed signals include create/find/delete, large directory listing, TTL expiration, stale child cleanup, and Redis outage behavior.
