# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.c

## Purpose
Implements the main io-cache translator: lifecycle, volume options, FOP interception, cache validation, cache invalidation, page fault dispatch, priority parsing, pruning triggers, and statedump support. It caches read data in per-inode pages and forwards all operations to its single child as needed.

## Important APIs, types, and functions
`ioc_readv()` is the read entry point and either bypasses caching or initializes an `ioc_local_t` and calls `ioc_dispatch_requests()`. `ioc_dispatch_requests()` maps a read range to page offsets, handles ready pages, in-flight pages, cache misses, and timeout validation. `ioc_cache_validate()` and `ioc_cache_validate_cbk()` issue child `fstat` requests when cached pages are older than `cache-timeout`. `ioc_update_pages()` refreshes cached page data after successful writes. Mutating operations such as `ioc_setattr()`, `ioc_truncate()`, `ioc_ftruncate()`, `ioc_discard()`, and `ioc_zerofill()` flush affected inode caches. `init()`, `reconfigure()`, `fini()`, and `mem_acct_init()` define the xlator lifecycle. `ioc_get_priority_list()` and `ioc_get_priority()` implement pattern-based eviction priority.

## Control flow
Lookup, create, mknod, open, and readdirp callbacks create or update `ioc_inode_t` state and apply fd-level bypass for size limits, `O_DIRECT`, or priority zero. A cached read ensures the inode has a page table, checks fd bypass, enqueues the caller on each requested page, then either wakes immediately from ready pages, schedules `ioc_page_fault()` for misses, or schedules `fstat` validation for old pages. Fault and validation callbacks later wake the queued frames; `ioc_frame_return()` unwinds only after the frame has received all page fragments.

## State and persistence behavior
Runtime state lives in `ioc_table_t` at `this->private`, inode contexts containing `ioc_inode_t`, fd contexts used as cache-bypass flags, page tables, LRU lists, wait queues, and per-frame `ioc_local_t` objects. There is no durable persistence. Reconfigure mutates cache size, timeout, file-size filters, pass-through, and priority lists; existing cached pages remain unless normal invalidation/pruning removes them.

## Dependencies and integration points
Depends on Gluster xlator FOP/callback APIs, inode/fd context APIs, `rbthash`, iovec/iobref helpers, memory pools, `dict_t`, statedump, logging/message IDs, option parsing macros, and child translator `readv`/`fstat`/metadata FOPs. It integrates with graph options such as `performance.io-cache`, NFS read behavior through `op_errno`, and inode invalidation callbacks from lower translators.

## Risks and test signals
Key risks are stale data if mtime/nsec validation misses a mutation, wait-count imbalance across page faults and validation, incorrect `cache_used` accounting when pages are stale or destroyed, priority-list reconfigure leaking old entries, missing fd refs in write paths, and lock ordering between table and inode locks during prune. High-value tests include cache hit/miss reads across page boundaries, concurrent readers waiting on the same page, validation timeout with unchanged and changed mtimes, write-through cache updates, truncate/discard/zerofill invalidation, `O_DIRECT` and size-limit bypass, priority zero bypass, cache-size pruning by priority, statedump under contention, and clean teardown after inode forget.
