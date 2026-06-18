# sources/distributed-fs/ceph-client/tools/perf/util/threads.h

## Purpose

`threads.h` defines the sharded thread-registry container used by perf machines.

## Important APIs, Types, and Functions

`THREADS__TABLE_BITS` is 3, giving `THREADS__TABLE_SIZE` of 8. `struct threads_table_entry` contains a hashmap shard, rwsem, and cached `last_match`. `struct threads` is the array of shards. The header exports init, exit, count, find, findnew, remove-all, remove-one, and foreach APIs.

## Control Flow and State

The state model is per-shard locking with refcounted thread ownership. Callers must respect reference ownership from find APIs.

## Dependencies and Integration Points

It depends on hashmap and rwsem utilities and is used by `machine` thread tables.

## Risks and Test Signals

The main risks are misuse of returned references and changing the shard count without validating lookup distribution. Tests should validate lookup and removal under repeated TID patterns.
