# sources/distributed-fs/ceph-client/fs/nfs/nfs42xattr.c

## Purpose

`nfs42xattr.c` implements the client-side cache for NFSv4.2 user extended attributes. It stores per-inode xattr name/value entries and listxattr results, integrates with inode cache invalidation, and registers memory shrinkers so cached xattr objects can be reclaimed under pressure.

## Important APIs, Types, and Functions

The file defines `struct nfs4_xattr_cache`, `struct nfs4_xattr_entry`, and `struct nfs4_xattr_bucket`. A cache is attached to `NFS_I(inode)->xattr_cache`, contains 64 hash buckets, has a special `listxattr` entry, tracks entry count in `nent`, and participates in `nfs4_xattr_cache_lru`. Entries contain the xattr name, value pointer, size, hash node, LRU node, reference count, and flags such as `NFS4_XATTR_ENTRY_EXTVAL` for separately allocated large values.

The exported cache API is `nfs4_xattr_cache_get`, `nfs4_xattr_cache_add`, `nfs4_xattr_cache_remove`, `nfs4_xattr_cache_set_list`, `nfs4_xattr_cache_list`, `nfs4_xattr_cache_zap`, `nfs4_xattr_cache_init`, and `nfs4_xattr_cache_exit`.

## Control Flow

Reads call `nfs4_xattr_get_cache(inode, 0)`, then hash by `jhash(name)` and take a bucket lock while finding and refcounting an entry. Adds may optimistically allocate a new cache without holding `i_lock`, then attach it under `i_lock` if the inode cache was not invalidated and another thread did not win the race. Adding a named xattr invalidates the cached listxattr result, replaces an old same-name entry, and adds the entry to the small or large entry LRU.

Invalidation removes the cache from the inode under `i_lock`, marks buckets draining, removes all entries from LRUs/hash tables, marks list cache as `ERR_PTR(-ESTALE)`, and frees objects when final references drop. Shrinkers isolate caches or entries with trylocks to avoid deadlock against the normal lock order.

## State and Persistence Behavior

All state is volatile kernel memory. The cache mirrors server xattr values only while the inode's xattr validity remains acceptable. `NFS_INO_INVALID_XATTR` causes `nfs4_xattr_get_cache` to unlink and discard the old cache. The cache has no persistence across inode eviction, module unload, memory pressure reclamation, or explicit invalidation.

## Dependencies and Integration Points

This file depends on Linux list LRU and shrinker APIs, slab caches, NFS inode state, spinlocks, krefs, xattr UAPI limits, and page-copy helpers. `nfs4proc.c` first attempts cache reads before RPCs and updates/removes cache entries after successful remote mutation; `nfs42proc.c` populates getxattr results into the cache.

## Risks and Edge Cases

Important risks are lock ordering, refcount/LRU consistency, and stale cache exposure. The sentinel `ERR_PTR(-ESTALE)` prevents listxattr results from being added while a cache is draining. Large xattrs use `kvmalloc` and a more aggressive shrinker, so allocation failure and memory pressure behavior need coverage.

## Test Signals

Tests should exercise cache hits after successful `getxattr`, listxattr caching, invalidation after set/remove, inode eviction zap, memory pressure shrinkers for small and large xattrs, concurrent get/add/remove on the same inode/name, and ERANGE length-probe behavior.
