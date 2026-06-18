# sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.c

## Purpose
Implements a thread-safe fileinfo handle cache for pNFS DS operations.

## Important APIs, Types, And Functions
Defines opaque `liz_fileinfo_cache` with LRU and used lists, AVL lookup by inode, entry count, max entries, min timeout, and mutex. `liz_fileinfo_entry` stores list/tree hooks, inode, attached `liz_fileinfo_t`, timestamp, used flag, and lookup mode. Public functions create/destroy/reset cache, acquire/release/erase entries, pop expired entries, free entries, and attach/extract fileinfo.

## Control Flow
Acquire looks for an unused LRU entry by inode in the AVL tree. If found it removes it from LRU/tree and moves it to used; otherwise it allocates a new entry and increments count. Release marks an entry unused, timestamps it, moves it to LRU tail, and inserts it into the AVL tree. `pop_expired` examines the oldest LRU entry and removes it if the cache is over capacity or its age exceeds the timeout. Erase removes a currently used entry without putting it into cache.

## State And Persistence Behavior
State is process-local and protected by `pthread_mutex_t`. The cache owns entries, not the underlying `liz_fileinfo_t`; callers release the LizardFS file handle after `pop_expired` and before `liz_fileinfo_entry_free`.

## Dependencies And Integration Points
Uses Ganesha `glist`, `avltree`, `gsh_calloc/free`, and pthread wrappers. Integrated by `ds.c` and export cleanup.

## Risks And Edge Cases
`get_time_ms` divides nanoseconds by `1000`, yielding microseconds added to milliseconds; this makes timestamps too large within each second and can distort timeout behavior. The comparator allows multiple entries per inode when not in lookup mode, enabling concurrent opens for the same inode but making tree ordering pointer-dependent. Destroy frees entries but does not release attached fileinfo handles; callers must drain/release first. `liz_fileinfo_cache_acquire` documentation mentions possible NULL on full cache, but implementation always allocates.

## Test Signals
`fileinfo_cache_unittest.cc` covers basic reuse, over-capacity expiry, and parameter reset. Additional timing and concurrency tests would be valuable.
