# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.h

## Purpose
Declares the io-cache translator's shared data structures, defaults, locking helpers, and cross-file function prototypes.

## Important APIs, types, and functions
`ioc_table_t` stores translator-wide page size, cache size, cache usage, file-size filters, inode LRU buckets, priority list, cache timeout, and memory pools. `ioc_inode_t` binds cache state to a Gluster inode. `ioc_cache` owns the per-inode page table, page LRU, mtime/nsec validation state, and last validation time. `ioc_page_t` represents one cached page, its vectors, iobref, wait queue, ready/stale flags, and lock. `ioc_local_t`, `ioc_waitq_t`, and `ioc_fill_t` model in-flight read assembly. Locking macros wrap table, inode, and local mutexes with trace logging.

## Control flow
The header does not execute logic, but it defines the contracts used across `io-cache.c`, `page.c`, and `ioc-inode.c`: page creation/destruction, waiting/wakeup, page faulting, frame return, inode creation/destruction, cache validity, and pruning.

## State and persistence behavior
All declared state is in-memory translator state. The header fixes the shape of inode contexts, fd-bypass interactions, and page cache accounting, but it has no on-disk format.

## Dependencies and integration points
Includes Gluster dict, call-stub, rbthash, compat errno, iobref/iovec-adjacent types through included headers, fnmatch, and io-cache message IDs. It is the internal ABI among the io-cache implementation files.

## Risks and test signals
Risks include structure fields being accessed without the expected lock, misuse of `char` flags for ready/stale/dirty state, global assumptions around `IOC_PAGE_TABLE_BUCKET_COUNT`, and prototypes that imply lock ownership only through naming. Tests should stress multi-page reads, concurrent invalidation, lock-order safety, and cache accounting around all callers of `__ioc_page_destroy()`.
