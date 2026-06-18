<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/netfs/internal.h

## Purpose
Central private header for netfs and embedded FS-Cache implementation files. It consolidates internal prototypes, inline helpers, stats accessors, group reference helpers, request flag synchronization helpers, cache/cookie/volume declarations, debug logging, and assertion macros.

## Important APIs, Types, And Functions
Declares netfs request, subrequest, read collector, write collector, write issue, retry, rolling buffer, and stats internals. Important inline helpers include `netfs_proc_add_rreq()`, `netfs_proc_del_rreq()`, `netfs_is_cache_enabled()`, `netfs_get_group()`, `netfs_put_group()`, `netfs_wake_rreq_flag()`, `netfs_check_rreq_in_progress()`, `netfs_check_subreq_in_progress()`, `fscache_cache_state()`, `fscache_cache_is_live()`, `fscache_set_cache_state()`, and `fscache_see_cookie()`.

## Control Flow
No standalone runtime flow; it shapes control in all implementation files. It provides acquire/release memory-ordering wrappers for request/subrequest completion flags and cache state, and conditional no-op fallbacks when stats/procfs/FS-Cache are disabled.

## State And Persistence
Declares global netfs request/subrequest mempools, proc request list/lock, stats counters, FS-Cache cookie slab, cookie LRU timer, and seq operations. Group helpers manage lifetime of dirty-folio group tags, including the sentinel `NETFS_FOLIO_COPY_TO_CACHE`.

## Dependencies And Integration Points
Includes slab, seq_file, folio_queue, netfs, fscache, fscache-cache, and trace event headers. It is the shared integration point between netfs library operations, cache backends, procfs, and trace/stat instrumentation.

## Risks
Because this is a private cross-module contract, signature drift or memory-ordering changes can break many files. The flag helpers are especially important: collectors depend on acquire/release ordering for visibility of errors, transferred byte counts, and list state.

## Test Signals
Full netfs build matrix with procfs/stats/FS-Cache enabled and disabled. Runtime tests should stress request completion wakeups, cache state transitions, dirty group refcounting, and stats no-op configurations.
