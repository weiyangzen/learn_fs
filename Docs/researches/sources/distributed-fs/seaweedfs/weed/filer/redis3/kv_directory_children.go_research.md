# sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children.go

## Purpose

`redis3/kv_directory_children.go` manages Redis3 directory-child indexes using `ItemList` plus distributed locks. It was read as a complete 139-line file.

## Important APIs, Types, and Functions

`insertChild`, `removeChild`, `removeChildren`, and `listChildren` operate on a directory-list key. `maxNameBatchSizeLimit` is one million names per list node.

## Control Flow

Writes acquire a Redsync mutex at `key + "lock"`, load the serialized `ItemList`, mutate it, and store the serialized header back if changed. `removeChildren` locks, lists all names while invoking a deletion callback, then removes all skiplist elements. `listChildren` performs unlocked read-only list traversal.

## State and Persistence Behavior

Directory state persists as one serialized skiplist header key plus per-node Redis keys. Insert/remove are protected by distributed locks; list is lock-free and may see concurrent changes.

## Dependencies and Integration Points

Depends on Redis3 `UniversalRedis3Store.redsync`, `ItemList`, `SkipListElementStore`, Redis, and `glog`. `UniversalRedis3Store` calls these functions from entry insert/delete/list paths.

## Risks and Edge Cases

Lock acquisition failures fail metadata writes. `mutex.Unlock()` errors are ignored. `removeChildren` does not delete the serialized header key itself in this file, leaving cleanup expectations to callers or overwritten state.

## Test Signals

Only `kv_directory_children_test.go` benchmarks raw Redis sorted-set insertion. Needed tests should cover concurrent insert/delete, list start positions, lock failure, and complete child cleanup.
