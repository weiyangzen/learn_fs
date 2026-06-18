# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/inode.h

## Purpose
Defines the in-memory inode table, inode, dentry, and per-translator inode context APIs used by GlusterFS to cache namespace state and object identity.

## APIs, Types, and Functions
`inode_table_t` stores global table lock, dentry/inode hash sizes, root inode, owning xlator, hash buckets, active/lru/purge/invalidate lists and counts, fd mempool, context slot count, invalidator callback, cleanup state, and root id/level. `dentry_t` links inode, parent, and name into inode and hash lists. `inode_t` stores table, GFID, lock, nlookup/kids atomics, fd counts, refcount, type, fd/dentry/hash/list links, namespace inode, invalidation/lru flags, and flexible `_inode_ctx` array. APIs cover table creation/destruction, inode new/link/unlink/rename/find/path/resolve, lookup/forget/ref/unref, invalidation, dentry grep, context set/get/reset/delete for one or two values, LRU limit changes, fd/inode context merge, linked/dentry checks, lookup-needed checks, directory-name discovery, and namespace-inode assignment.

## Control Flow, State, and Persistence
The inode table is process-local cache state keyed by GFID and parent/name. Lookups and links populate it; forget/unref/LRU/purge/invalidate paths evict or notify. Per-xlator context slots attach translator-private state to shared inode objects.

## Dependencies and Integration
Depends on `iatt.h`, UUIDs, `fd.h`, lists, locks, and xlator callbacks. Integrated with FUSE nlookup semantics, DHT/AFR caches, readdirp inode linking, fd tracking, and graph cleanup.

## Risks and Test Signals
Risks include dentry cycles, stale GFID/name aliases, ref/nlookup leaks, invalidation races, context slot misuse, and LRU/purge list corruption. Test signals include path/link/rename tests, forget/invalidation tests, dentry cycle detection logs, concurrent lookup/ref tests, and statedump ref/context inspection.
