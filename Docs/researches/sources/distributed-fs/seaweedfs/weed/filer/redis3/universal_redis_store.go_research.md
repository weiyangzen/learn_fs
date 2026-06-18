# sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store.go

## Purpose

`redis3/universal_redis_store.go` implements Redis3 filer metadata storage, replacing simple directory sets with locked skiplist-backed child indexes. It was read as a complete 203-line file.

## Important APIs, Types, and Functions

`UniversalRedis3Store` owns a `redis.UniversalClient` and `redsync.Redsync`. It implements no-op transactions, `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, unsupported prefixed listing, `genDirectoryListKey`, and `Shutdown`.

## Control Flow

Entry bytes are encoded, optionally gzipped, and stored at full-path keys with TTL. Inserts call `insertChild` for the parent. Deletes remove a possible child-list key for the path, delete the entry key, then call `removeChild`. Folder deletion calls `removeChildren`, deleting each child entry and nested list key through a callback. Listing calls `listChildren`, fetches each entry, lazily deletes expired entries, and stops on callback false or limit.

## State and Persistence Behavior

Redis stores entry keys plus directory-list skiplist data. Directory mutations are protected by Redsync, but entry writes and index writes are not one atomic transaction.

## Dependencies and Integration Points

Depends on `ItemList`, Redis3 child helpers, SeaweedFS entry serialization, gzip helpers, filer errors, and `glog`.

## Risks and Edge Cases

Partial insert/delete failures can leave entries and child indexes inconsistent. Expired entries are removed with `ZRem`, but Redis3 child indexes are not simple sorted sets, so this cleanup path may not match the actual index schema.

## Test Signals

No full store tests in this subset. Needed coverage includes CRUD, large directory listing, TTL cleanup, stale index cleanup, lock contention, and folder child deletion.
