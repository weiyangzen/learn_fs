# sources/distributed-fs/lizardfs/src/chunkserver/indexed_resource_pool.h

## Purpose
`indexed_resource_pool.h` defines `IndexedResourcePool`, a small template used to keep integer-indexed resources accessible by ID while also maintaining an LRU-style release list. In this subset it backs the open chunk descriptor pool, allowing descriptors to be retained after close and later freed when old or under pressure.

## Important APIs, Types, and Functions
`IndexedResourcePool<Resource, DefaultCapacity, ReleaseThreshold_s, PopUnusedCount>` stores `Entry` nodes in a vector indexed by resource ID. ID `0` is a sentinel list node. `acquire(id)` removes an existing resource from the unused list. `acquire(id, Resource&&)` installs or replaces resource data, resizing the vector when necessary. `release(id, timestamp)` moves a resource to the LRU tail. `purge(id)` calls `resource.purge()`, moves it to `purge_list_`, and removes it from the list. `freeUnused(now, extra_lock, count)` frees old removable resources by moving them into a local candidate vector whose destructors run outside the pool. `getResource(id)` returns a reference by index.

The `Resource` type must support default construction, move operations, `purge()`, `canRemove()`, and destructor-based release semantics.

## Control Flow
Resources are acquired while active, released with a timestamp when idle, and later scanned from the list front by `freeUnused`. The pool first flushes pending purge resources, snapshots the current front into `garbage_collector_head_`, then repeatedly takes an external lock and the pool mutex before checking age and `canRemove()`. Removable resources are moved to local candidates and erased from the linked list; non-removable entries advance the scan head.

## State and Persistence Behavior
All state is in memory: the indexed vector, sentinel-based doubly linked list, purge list, mutex, and current garbage collector cursor. Persistence effects happen only through the `Resource` destructor or `purge()` implementation, such as closing file descriptors.

## Dependencies and Integration Points
The template uses `common/small_vector.h`, standard mutex/vector machinery, and the chunkserver `Chunk` include for local resource types. `hddspacemgr.cc` uses `IndexedResourcePool<OpenChunk>` to cache and retire open chunk descriptors while coordinating with the global chunk registry lock.

## Risks and Edge Cases
`purge(id)` does not bounds-check `id` before indexing, unlike `acquire` resize behavior. `contains(id)` assumes a valid positive ID. The list implementation relies on sentinel node `data_[0]`; corruption of `prev`/`next` values can affect later erases. `freeUnused` intentionally locks `extra_lock` before `mutex_` inside the loop; callers must ensure this ordering is compatible with the rest of the subsystem. Resource destruction is delayed by `purge_list_` and candidate vectors, so tests must account for destructor timing.

## Test Signals
Unit tests should cover acquire/release order, resize on high IDs, purge and destructor behavior, `freeUnused` age threshold, `canRemove=false` skipping, sentinel front/back updates, and invalid IDs. Concurrency tests should stress acquire/release/freeUnused with a mock resource that records destructor and purge calls.
