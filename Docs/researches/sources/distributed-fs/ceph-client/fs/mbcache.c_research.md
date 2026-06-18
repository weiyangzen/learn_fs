# sources/distributed-fs/ceph-client/fs/mbcache.c

## Purpose

`sources/distributed-fs/ceph-client/fs/mbcache.c` implements the metadata block cache used by ext2/ext4 for extended attribute block/value deduplication. It is a fixed-size hash table keyed by a 32-bit hash with unique key/value pairs, reusable-entry search, reference-counted entries, LRU-like reclaim, and shrinker integration. The source was read as a complete 444-line file for this report.

## Important APIs, Types, and Functions

The private `struct mb_cache` stores hash buckets, bucket sizing, max entries, a list and count protected by `c_list_lock`, a shrinker, and shrink work. Important exported APIs are `mb_cache_entry_create`, `__mb_cache_entry_free`, `mb_cache_entry_wait_unused`, `mb_cache_entry_find_first`, `mb_cache_entry_find_next`, `mb_cache_entry_get`, `mb_cache_entry_delete_or_get`, `mb_cache_entry_touch`, `mb_cache_create`, and `mb_cache_destroy`. Internal helpers include `mb_cache_entry_head`, `__entry_find`, `mb_cache_count`, `mb_cache_shrink`, `mb_cache_scan`, and `mb_cache_shrink_worker`.

## Control Flow

Cache creation allocates the cache, hash buckets, shrinker, and work item. Entry creation may schedule background shrinking or perform synchronous shrinking, allocates an entry with two refs, checks for a duplicate key/value under the bucket bit-lock, inserts into the hash and global list, increments count, and drops the setup ref. Lookup by key scans reusable entries and returns a ref; lookup by key/value returns a matching entry ref. Delete-or-get removes an unused key/value entry by atomically moving refcount from two to zero, otherwise returns a live ref. Shrinking scans the list, gives referenced or busy entries another chance, and frees unreferenced entries.

## State and Persistence Behavior

State is in-memory cache metadata only. Entries persist until dropped by explicit deletion, shrinker reclaim, or cache destruction. A hash-table reference normally holds entries alive; external users hold additional refs. Reusable and referenced bits influence lookup and reclaim but do not persist beyond memory.

## Dependencies and Integration Points

It depends on kernel list, bit-lock hlist, workqueue, shrinker, slab, and exported `linux/mbcache.h` entry helpers such as `mb_cache_entry_put`. ext2/ext4 xattr code are the primary callers.

## Risks and Edge Cases

The key is not unique; the key/value pair must be unique. Reference-count transitions are subtle, especially delete-or-get and shrinker freeing. Locking deliberately avoids nesting list locks into bucket bit-locks for RT. Destruction assumes no users except the shrinker can reach the cache. Background shrink may lag, so synchronous shrinking handles excessive growth.

## Test Signals

Test duplicate insertion, key collision iteration, reusable versus non-reusable lookup, delete-or-get under concurrent refs, shrinker reclaim of referenced and unreferenced entries, cache destroy after user drain, ext2/ext4 xattr block deduplication, and KASAN/KCSAN refcount stress.
