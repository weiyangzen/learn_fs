# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-open-cache.c

## Purpose
Implements a fixed-size LRU-style cache for open bstream file descriptors and an asynchronous deletion mechanism for removed bstream files. It reduces open/close churn for DBPF data files while supporting lazy bstream creation and fast unlink by rename.

## Important APIs, Types, And Functions
Public functions are `dbpf_open_cache_initialize`, `dbpf_open_cache_finalize`, `dbpf_open_cache_get`, `dbpf_open_cache_put`, `dbpf_open_cache_remove`, and `clear_stranded_bstreams`. Internal types include `open_cache_entry`, `open_cache_ref`, `unlink_context`, and `file_struct`. Helpers are `open_fd`, `close_fd`, `dbpf_open_cache_find_entry`, `dbpf_open_cache_entries_finalize`, `fast_unlink`, and the `unlink_bstream` worker thread.

## Control Flow
Initialization preallocates 64 cache entries onto `free_list` and starts a pthread that unlinks queued stranded files. `get` searches `used_list` then `unused_list`, reopens if needed, increments refcount, and moves the entry to the used-list head. On cache miss it consumes a free entry, evicts an unused entry, or bypasses the cache with an uncached fd. `put` decrements cached refcounts and moves zero-ref entries to the unused list, or closes uncached fds. `remove` refuses active used entries, closes/removes unused entries, renames the bstream into `stranded-bstreams`, and queues it for background unlink.

## State And Persistence
Runtime state is guarded by `cache_mutex`: used, unused, and free qlists backed by a 64-entry static array. Persistent state is the bstream file tree under `bstreams/<bucket>` and the `stranded-bstreams` directory. Writes open with `O_CREAT`; reads of missing lazy-created files return `ENOENT`. Fast deletion persists a rename before asynchronous unlink, so crash recovery must clear stranded files at collection lookup.

## Dependencies And Integration Points
Uses path macros and `my_storage_p` from DBPF management, TROVE error mapping, bstream open types, quicklist, pthreads, and POSIX open/close/rename/unlink/stat APIs. Bstream read/write/resize paths acquire references through this cache, while collection lookup invokes `clear_stranded_bstreams`.

## Risks And Test Signals
Risks include pthread cancellation without join, repeated cancellation from entry finalization, active-remove returning failure and relying on callers to retry, stale `remove_flag` diagnostics, fd type mismatch when reusing entries for direct versus buffered I/O, stranded file cleanup errors, and global cache state not scoped per storage. Tests should stress >64 active bstreams, cached reuse, read-missing versus write-create behavior, direct-I/O flags, remove while active/inactive/uncached, crash-style stranded cleanup, and concurrent get/put/remove.
