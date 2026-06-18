# sources/distributed-fs/lizardfs/src/mount/direntry_cache.h

## Purpose
`direntry_cache.h` implements a credential-aware directory entry cache for the mount client. It supports lookup by parent/name, parent/index, and inode, plus FIFO expiration/removal.

## Important APIs, Types, And Functions
- `DirEntryCache::DirEntry` stores uid/gid, parent inode, inode, directory index, next index, timestamp, name, attributes, and Boost intrusive hooks.
- Intrusive containers: `LookupSet`, `IndexSet`, `InodeMultiset`, and `FifoList`.
- `lookup(ctx,inode,attr)` and `lookup(ctx,parent,name,inode,attr)` are thread-safe read-lock lookups.
- `insert`, `insertSequence`, and `overwriteEntry` add or update cache entries.
- `invalidate`, `lockAndInvalidateInode`, `lockAndInvalidateParent`, `removeExpired`, `removeOldest`, and `clear` remove entries.
- `updateTime` refreshes internal microsecond time from `Timer`.

## Control Flow
Insertions reject stale data (`timestamp + timeout_ <= current_time_`), remove a bounded number of expired FIFO entries, erase conflicting lookup/index entries, and add new intrusive entries. `insertSequence` updates index-order entries from directory listing batches, resolving name/index collisions and overwriting existing entries in-place when possible. Lookups take a shared lock, update time, find by inode or parent/name, reject expired entries and inode `0`, and copy attributes out.

Invalidation by directory index follows the linked `next_index` chain from a starting index. Parent/inode invalidations take a unique lock and erase matching entries. `erase` removes an entry from all four intrusive containers before deleting it.

## State And Persistence
The cache owns heap-allocated `DirEntry` objects referenced by multiple intrusive containers. `current_time_` is atomic, `timeout_` is configurable, and `rwlock_` protects thread-safe operations where documented. The cache is purely transient and derived from master directory replies.

## Dependencies And Integration Points
It depends on `Attributes`, shared mutex utilities, `Timer`, `LizardClient::Context`, `DirectoryEntry`, and Boost intrusive containers. Mount readdir/lookup/getattr paths can use it to avoid master round trips.

## Risks
- Only explicitly marked methods are thread-safe; raw `find`, `insert`, `insertSequence`, and some removal helpers require external locking discipline.
- `setTimeout` is not synchronized.
- `insert` takes `const std::string name` by value and `addEntry` copies several values; performance is acceptable but not zero-copy.
- `lookup(ctx,inode)` searches multiset by inode then uid/gid but does not include parent/name, so multiple credential-matching aliases return the first.
- Inconsistency logging after `addEntry` detects but does not repair index divergence.

## Test Signals
Existing unit tests cover ordering, overwrite, repetitions, and random-order updates. Additional tests should cover expiration, invalidation chains, credential isolation, inode lookup with multiple names, concurrent lookup under write invalidation, and stale timestamp rejection.
