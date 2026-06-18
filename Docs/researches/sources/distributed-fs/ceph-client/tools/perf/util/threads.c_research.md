# sources/distributed-fs/ceph-client/tools/perf/util/threads.c

## Purpose

`threads.c` implements a sharded in-memory registry of `struct thread` objects keyed by TID. It gives machine code fast lookup, creation, deletion, and iteration for active and retained threads.

## Important APIs, Types, and Functions

The public functions are `threads__init()`, `threads__exit()`, `threads__nr()`, `threads__find()`, `threads__findnew()`, `threads__remove_all_threads()`, `threads__remove()`, and `threads__for_each_thread()`. Internal helpers choose a shard by `tid % THREADS__TABLE_SIZE`, hash long keys, compare keys, and maintain a per-shard `last_match` cache.

## Control Flow and State

Initialization creates eight hashmap shards and rwsems. Find first checks `last_match` under read lock, then falls back to the hashmap and refreshes the cache. Find-new allocates a thread under write lock and handles add races by dropping the new object and returning the existing one. Remove paths clear `last_match`, delete from the shard, and drop references.

## Dependencies and Integration Points

It depends on the perf hashmap, rwsem, machine, and thread reference API. It is embedded in `struct machine` and used by event processing for fork, exit, mmap, comm, samples, and synthetic event replay.

## State and Persistence Behavior

All state is in memory. The registry owns a reference to each stored thread; callers receive additional references from find functions and must put them. The `last_match` cache also owns a reference.

## Risks and Test Signals

Risks include reference leaks in cache replacement, shard races, deleting absent keys, and callback iteration holding read locks too long. Tests should cover find/findnew races, cache hits, negative TIDs, removal, remove-all cleanup, and early-stop iteration.
