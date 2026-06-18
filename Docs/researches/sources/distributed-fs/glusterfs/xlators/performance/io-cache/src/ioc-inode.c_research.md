# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-inode.c

## Purpose
Provides inode-scoped helpers for io-cache: pointer-string conversion utilities, cache-validation wakeup handling, inode cache object creation, and destruction.

## Important APIs, types, and functions
`ioc_inode_create()` allocates an `ioc_inode_t`, initializes page LRU and mutex state, assigns priority weight, and links it into table inode lists. `ioc_inode_destroy()` removes an inode from table lists, flushes pages, destroys its page table, and frees the object. `ioc_inode_wakeup()` processes the inode-level validation wait queue, either waking ready pages when cache metadata is still valid or issuing new page faults when it is not. `ptr_to_str()` and `str_to_ptr()` convert pointer values for string storage/use.

## Control flow
When `io-cache.c` creates or discovers inode state, this file links it into eviction structures. During fstat validation, pages waiting on inode validation are queued at `ioc_inode->waitq`; the validation callback calls `ioc_inode_wakeup()`, which iterates those pages and either wakes their frame wait queues or restarts page reads.

## State and persistence behavior
State is in-memory only: table inode counters, `inodes` and `inode_lru` lists, page table ownership, and wait queues. Destroy is normally triggered from the inode `forget` callback.

## Dependencies and integration points
Depends on `io-cache.h`, io-cache memory types, Gluster inode contexts, list primitives, rbthash lifecycle, and page helpers from `page.c`.

## Risks and test signals
Risks include using priority weights outside allocated LRU bucket bounds, destroying an inode with active page waiters, races between validation wakeup and page fault callbacks, and pointer-string conversion truncation on unusual platforms. Test signals include inode create/update/forget cycles, validation wait queues with multiple pages, invalidation while faults are in flight, and teardown with empty and non-empty page tables.
