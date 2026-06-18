# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_kv.go

## Purpose

`leveldb3_store_kv.go` implements generic KV operations for LevelDB3. Unlike metadata, all KV data is kept in the default `_main` database rather than per-bucket databases.

## Important APIs, Types, and Functions

The methods are `KvPut`, `KvGet`, and `KvDelete` on `LevelDB3Store`. They operate directly on `store.dbs[DEFAULT]`.

## Control Flow

Each method performs a raw LevelDB operation. `KvGet` maps `leveldb.ErrNotFound` to `filer.ErrKvNotFound`; other errors are wrapped. Put and delete return wrapped errors on failure.

## State and Persistence Behavior

KV state persists in `_main`, shared with non-bucket metadata. It is not dropped when individual bucket databases are deleted, which is important for global filer state such as replication offsets.

## Dependencies and Integration Points

The file depends on the default DB having been opened by `initialize`. It supports filer subsystems that require byte-key persistence independently of bucket metadata.

## Risks and Edge Cases

If `_main` is missing from the map due to failed initialization or shutdown races, these methods can panic. Raw KV keys can collide with default metadata keys if not namespaced. There is no transaction or TTL support.

## Test Signals

Tests should cover KV persistence before/after bucket deletion, missing key mapping, binary keys, empty values, and shutdown behavior.
