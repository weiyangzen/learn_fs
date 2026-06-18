# sources/distributed-fs/lustre-release/lustre/osc/osc_io.c research

## Purpose
`osc_io.c` implements `cl_io_operations` for the OSC layer. It translates high-level CLIO operations into OSC page submissions, setattr/fallocate/sync/ladvise/lseek RPCs, attribute updates, active IO accounting, read-ahead setup, LRU reservation, and cleanup of active extents.

## Important APIs, Types, and Functions
Major exported functions include `osc_io_submit()`, `osc_dio_submit()`, `osc_io_commit_async()`, `osc_io_extent_release()`, `osc_io_iter_init()`, `osc_io_iter_fini()`, `osc_io_rw_iter_fini()`, `osc_io_fault_start()`, `osc_punch_start()`, `osc_io_setattr_end()`, `osc_io_read_start()`, `osc_io_write_start()`, `osc_fsync_ost()`, `osc_io_fsync_end()`, `osc_io_end()`, `osc_io_lseek_start()`, `osc_io_lseek_end()`, and `osc_io_lru_reserve()`. The private `osc_io_ops` table maps CLIO operation types to these callbacks.

Key per-IO state is `struct osc_io`, accessed through `osc_env_io()` or `cl2osc_io()`. Observed fields include `oi_active`, `oi_is_active`, `oi_lockless`, `oi_write_osclock`, `oi_read_osclock`, `oi_lru_reserved`, `oi_oa`, `oi_cbarg`, capability flags, and truncate state.

## Control Flow
For normal read/write submission, `osc_io_submit()` prepares pages using `cl_page_prep()` except for transient direct-IO pages, stamps BRW flags, calls `osc_page_submit()`, batches pages up to max pages or write chunk limits, then queues them with `osc_queue_sync_pages()`. `osc_dio_submit()` performs the same batching over `cl_dio_pages` and calls `osc_queue_dio_pages()`.

Buffered dirty-page commit uses `osc_io_commit_async()`. It clips partial lockless writes, loops through input pages, calls `osc_page_cache_add()` if a page is not already pending, updates KMS/size through `osc_page_touch_at()`, batches VM folios for the caller callback, updates shrink timing, and releases `oi_active` early for sync writes.

Operation-specific control is implemented through `osc_io_ops`. Reads update atime unless `ci_noatime`; writes update ctime/mtime. Faults touching writable mappings expand KMS. Setattr/truncate first freezes local cache with `osc_cache_truncate_start()`, sends async setattr, punch, or fallocate RPCs, then `osc_io_setattr_end()` waits for completion and releases truncate state. Fsync writes back the requested range, optionally waits, and sends OST_SYNC. Data-version, ladvise, and lseek allocate PTLRPC requests or call base helpers and complete through per-IO completions.

## State and Persistence Behavior
`osc_io_iter_init()` rejects invalid imports, supports fast mirror switching for non-delay reads with unhealthy imports by returning `-EAGAIN`, increments `oo_nr_ios`, and marks the OSC IO active. Fini decrements `oo_nr_ios` and wakes `oo_io_waitq`. Attribute persistence is indirect: local LVB/KMS updates happen through `cl_object_attr_update()`, while OST persistence happens through BRW, setattr, fallocate, sync, ladvise, getattr, and seek RPCs. `oi_lockless` causes server-lock (`OBD_FL_SRVLOCK`/`OBD_BRW_SRVLOCK`) behavior rather than relying on local LDLM handles.

## Dependencies and Integration Points
The file depends on CLIO page queues, OSC page/cache APIs, LDLM lock references, PTLRPC request packing, OBD `obdo` wire helpers, LNet RDMA-only page detection, and Linux fallocate/lseek constants. It integrates with `osc_cache.c` for all page queueing/writeback/truncation, `osc_page.c` for page submit/touch behavior, `osc_lock.c` through `oi_read_osclock` and `oi_write_osclock`, and `osc_request.c` base RPC wrappers.

## Risks
Risk centers on partial-page and lockless paths, asynchronous completion lifetime, and attribute ordering. `osc_io_submit()` returns success when pages reached `qout`, even if later pages failed, so callers must honor queue semantics. Setattr/truncate must not discard data before server punch support is known; the file flushes before punch/zero-range to avoid reorder loss. Fsync reclaim mode intentionally skips work when active IO, dirty writes, and unstable pages are zero; stale counters would produce data-integrity bugs.

## Test Signals
Tests should exercise buffered and direct read/write batching, chunk-limit splitting, RDMA-only flag propagation, `ci_ndelay` mirror fallback, lockless IO server-lock flags, mtime/ctime/atime updates, writable fault KMS extension, truncate and fallocate punch ordering, data-version fallback/error handling, `SEEK_HOLE`/`SEEK_DATA` with and without server support, fsync local/all/reclaim/discard modes, and LRU reservation under low-cache conditions.
