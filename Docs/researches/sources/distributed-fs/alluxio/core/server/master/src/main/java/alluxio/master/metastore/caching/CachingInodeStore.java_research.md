# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CachingInodeStore.java

## Purpose
`CachingInodeStore` is a write-back, heap-cached `InodeStore` wrapper over another `InodeStore` backing store. It caches inode records, parent-child edges, and complete directory listings to reduce slow backing-store access while preserving checkpointability.

## Important APIs and Types
- Implements `InodeStore` and `Closeable`.
- Holds backing `InodeStore`, `InodeLockManager`, `InodeCache`, `EdgeCache`, `ListingCache`, and `mBackingStoreEmpty`.
- Public store methods delegate to caches for inode/edge reads and writes.
- Checkpoint methods flush inode and edge caches before delegating to the backing store.
- `InodeCache extends Cache<Long, MutableInode<?>>`.
- `EdgeCache extends Cache<Edge, Long>` and maintains parent-to-child index plus unflushed deletes.
- `ListingCache` is a weighted complete-listing cache, not a source of truth.

## Control Flow
Construction validates cache size/watermark configuration, creates the three caches, and registers heap-size metrics. Inode writes go to `InodeCache`; new directory writes prime an empty listing. Edge writes go to `EdgeCache`, which updates `ListingCache` through callbacks. Reads first consult caches and load from backing store as needed. `hasChildren` uses cached listings when available, otherwise queries merged edge/backing data.

`InodeCache.flushEntries` and `EdgeCache.flushEntries` try to acquire inode or edge write locks before writing/removing from the backing store, optionally using backing-store write batches. Entries whose locks cannot be acquired remain dirty for later. `EdgeCache.getChildIds` merges cache entries, unflushed deletes, and backing-store child IDs to provide consistency despite asynchronous eviction. `ListingCache.getChildIds` creates a loading placeholder, computes complete listings from `EdgeCache`, and caches them only if no concurrent modification was observed.

## State and Persistence
The authoritative recent state is the cache plus backing store. Dirty cache entries represent updates not yet persisted to the backing store. Checkpointing flushes dirty inode and edge entries, then checkpoints the backing store. Restore clears caches, restores backing store, and marks `mBackingStoreEmpty=false`.

## Dependencies and Integration Points
Integrates `InodeStore`, `InodeLockManager`, lock resources, `ReadOption`, metrics, object-size calculation, `HeapInodeStore.sortedMapToIterator`, and optional backing-store batch writes. It is used when the master metastore is configured for caching over RocksDB or another persistent store.

## Risks and Edge Cases
- The external lock contract is essential; cache eviction serializes mutable inodes under inode/edge locks.
- `clear()` clears inode and edge caches and backing store but does not clear listing cache in the public method, leaving potential stale listing entries unless callers reset the whole store lifecycle.
- `close()` registers backing store before caches with `Closer`, relying on reverse close order so cache eviction threads close before the backing store.
- `mBackingStoreEmpty` is an optimization; once false, it never becomes true except new instance creation.
- Listing cache weight must stay accurate across concurrent add/remove/evict paths.
- Skipping cache can still merge with cached edge state to preserve unflushed updates.

## Test Signals
Tests should cover cache hits/misses, dirty flush with lock acquisition failure and retry, backing-store-empty fast paths, edge merge with unflushed deletes, listing cache concurrent modification invalidation, checkpoint flush delegation, restore clearing caches, batch write usage, close ordering, and index verification.
