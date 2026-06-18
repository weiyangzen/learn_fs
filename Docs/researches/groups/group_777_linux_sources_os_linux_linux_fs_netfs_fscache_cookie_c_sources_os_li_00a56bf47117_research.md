# Group Research: group_777_linux_sources_os_linux_linux_fs_netfs_fscache_cookie_c_sources_os_li_00a56bf47117

Scope: `Docs/research_subset_a.md`.  
Coverage: read all listed files completely, 9,161 source lines total.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_cookie.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_cookie.c

Implements FS-Cache data-object cookie lifecycle management for the netfs cache API.

Key responsibilities:
- Allocates/free cookies from `fscache_cookie_jar`.
- Maintains global cookie hash table keyed by volume plus index key.
- Tracks cookies in `/proc` list and LRU list.
- Drives the cookie state machine: `QUIESCENT`, `LOOKING_UP`, `CREATING`, `ACTIVE`, `INVALIDATING`, `FAILED`, `LRU_DISCARDING`, `WITHDRAWING`, `RELINQUISHING`, `DROPPED`.
- Pins cache access with `n_accesses` and netfs use with `n_active`.
- Handles lookup, prepare-to-write, invalidation, withdrawal, relinquishment, LRU discard, and collision waiting.

Important exported APIs:
- `__fscache_acquire_cookie()`: creates and hashes a cookie.
- `__fscache_use_cookie()`: starts using a cookie and may begin lookup.
- `__fscache_unuse_cookie()`: stops using a cookie and places it on LRU if cacheable.
- `__fscache_relinquish_cookie()`: releases a cookie permanently.
- `__fscache_invalidate()`: invalidates object data and updates auxiliary coherency data.
- `fscache_begin_cookie_access()` / `fscache_end_cookie_access()`: guard I/O access against cache withdrawal.
- `fscache_withdraw_cookie()`, `fscache_get_cookie()`, `fscache_put_cookie()`.

Concurrency model:
- Cookie state protected by `cookie->lock`, published with release/acquire semantics.
- Hash buckets use `hlist_bl_lock`.
- Proc list uses `fscache_cookies_lock`.
- LRU list uses `fscache_cookie_lru_lock` plus timer/workqueue.
- Waiters use `wait_var_event()` on `cookie->state`.

Notable behavior:
- Duplicate active cookies are rejected; collisions with relinquished cookies wait until the old cookie reaches `DROPPED`.
- LRU discard is postponed if `n_active` or `n_accesses` indicates active use.
- Invalidation can be queued during lookup/creation or performed immediately when active.
- Failure clears `FSCACHE_COOKIE_IS_CACHING` and moves to `FAILED`.
- `/proc/fs/netfs/cookies` exposes debug id, volume id, refs, active/access counts, state, flags, key, and auxiliary data.

Dependencies:
- Uses cache backend operations through `cookie->volume->cache->ops`.
- Relies on `fscache_volume.c` for volume lifetime and cache access.
- Statistics are updated through `fscache_stats.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_cookie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_internal.h -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_internal.h

Small include shim for FS-Cache-internal compilation units.

Key content:
- Includes `internal.h`.
- Overrides `pr_fmt` to prefix messages with `FS-Cache: `.

Purpose:
- Allows FS-Cache source files to share the broader netfs internal definitions while using FS-Cache-specific logging prefixes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_io.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_io.c

Implements FS-Cache data I/O operation setup, cache writes, and resize operations.

Key responsibilities:
- Waits for cookie state to become usable for I/O.
- Begins read/write cache operations and attaches backend resources to `netfs_cache_resources`.
- Writes pagecache xarray ranges into cache storage.
- Clears deprecated `PG_private_2` bookkeeping bits after cache writes.
- Resizes backing cache objects synchronously under netfs inode serialization.

Important exported APIs:
- `fscache_wait_for_operation()`: waits until cookie reaches a state suitable for requested operation.
- `__fscache_begin_read_operation()`.
- `__fscache_begin_write_operation()`.
- `__fscache_clear_page_bits()`.
- `__fscache_write_to_cache()`.
- `__fscache_resize_cookie()`.

Important behavior:
- `fscache_begin_operation()` pins cookie access, stores debug/invalidation counters, waits through lookup/creation/invalidation/LRU-discard states, then calls backend `begin_operation`.
- Failed or non-live cookies return `-ENOBUFS` and drop the access pin.
- Cache writes allocate `struct fscache_write_request`, prepare the write through backend ops, build an xarray iterator over `mapping->i_pages`, then issue `fscache_write()`.
- Completion calls optional netfs termination callback, ends cache operation, clears `PG_private_2` if requested, and frees request state.
- Resizes are not deferred because they must be serialized inside the netfs inode lock.

Dependencies:
- FS-Cache cookie state machine.
- Backend cache `ops`: `begin_operation`, `prepare_write`, `resize_cookie`.
- Netfs cache resource helpers from public headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_main.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_main.c

Initializes and tears down the FS-Cache component of netfs support.

Key responsibilities:
- Defines and exports `fscache_wq`.
- Exports FS-Cache tracepoints.
- Provides stable architecture-independent hash function for cache keys.
- Initializes `/proc` entries and cookie slab cache.
- Destroys FS-Cache resources at module exit.

Important APIs:
- `fscache_hash()`: hashes little-endian 32-bit chunks with fixed mixing.
- `fscache_init()`: allocates workqueue, initializes proc entries, creates cookie slab.
- `fscache_exit()`: destroys cookie slab, proc entries, LRU timer, and workqueue.

Notable details:
- Hash function is intentionally architecture-independent because hash bits may be persisted on disk.
- Caller must provide data length rounded to a multiple of four bytes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_proc.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_proc.c

Creates FS-Cache procfs visibility under the shared netfs proc tree.

Key responsibilities:
- Creates compatibility symlink `fs/fscache` pointing to `netfs`.
- Creates sequence files:
  - `fs/netfs/caches`
  - `fs/netfs/volumes`
  - `fs/netfs/cookies`
- Cleans up procfs entries.

Important APIs:
- `fscache_proc_init()`.
- `fscache_proc_cleanup()`.

Notable issue:
- Cleanup removes `fs/fscache` subtree/symlink, while creation also adds files under `fs/netfs`; the broader `netfs_exit()` removes the full `fs/netfs` subtree.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_stats.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_stats.c

Defines FS-Cache statistics counters and procfs rendering.

Counters cover:
- Volumes, collisions, allocation failures.
- Cookies and LRU activity.
- Acquires, invalidates, updates, relinquishes, resizes.
- Cache I/O counts and no-space/cull events.

Important exported counters:
- `fscache_n_updates`.
- `fscache_n_read`.
- `fscache_n_write`.
- `fscache_n_no_write_space`.
- `fscache_n_no_create_space`.
- `fscache_n_culled`.
- `fscache_n_dio_misfit`.

Important API:
- `fscache_stats_show()`: appends FS-Cache statistics to the netfs stats seq file.

Notable behavior:
- Includes LRU timer pending delta in the `LRU` statistics line.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_volume.c -->
# File Research: sources/os/linux/linux/fs/netfs/fscache_volume.c

Implements FS-Cache volume cookie lifecycle management.

Key responsibilities:
- Allocates volume objects and hashes them by cache plus volume key.
- Pins cache access at volume granularity.
- Creates backend volume representation asynchronously.
- Handles hash collisions with relinquished volumes.
- Frees backend volume state and proc list entries.
- Exposes `/proc/fs/netfs/volumes`.

Important exported APIs:
- `__fscache_acquire_volume()`.
- `__fscache_relinquish_volume()`.
- `fscache_try_get_volume()`.
- `fscache_put_volume()`.
- `fscache_end_volume_access()`.
- `fscache_withdraw_volume()`.

Concurrency model:
- Hash buckets use `hlist_bl_lock`.
- Global add/remove and proc listing use `fscache_addremove_sem`.
- Volume creation uses `FSCACHE_VOLUME_CREATING` bit and workqueue.
- Access pins use `volume->n_accesses` and waiters sleep on the atomic variable.

Important behavior:
- Volume key is length-prefixed and padded before hashing.
- Collisions with already-relinquished volumes set pending flags and wait for the old volume to unhash.
- `fscache_create_volume()` pins the cache, schedules `acquire_volume`, and can optionally wait.
- `fscache_withdraw_volume()` decrements the artificial cache pin and waits until all volume accesses drain.

Dependencies:
- Cache lookup/refcounting from `fscache-cache.c`.
- Backend cache ops: `acquire_volume`, `free_volume`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/fscache_volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/internal.h -->
# File Research: sources/os/linux/linux/fs/netfs/internal.h

Central private header for Linux netfs and FS-Cache implementation files.

Major contents:
- Includes core kernel, netfs, fscache, and trace headers.
- Declares internal APIs across buffered read/write, misc helpers, object lifetime, read/write collectors, retry paths, stats, fscache cache/cookie/volume/main/proc.
- Defines proc list helpers for active netfs I/O requests.
- Provides statistic increment/decrement wrappers gated by config options.
- Provides cache state helpers with acquire/release semantics.
- Provides request/subrequest in-progress tests with memory barriers.
- Provides netfs group reference helpers.
- Defines debug logging macros and assertion macros.

Important contracts:
- `netfs_check_rreq_in_progress()` and `netfs_check_subreq_in_progress()` impose ordering for collectors.
- `netfs_wake_rreq_flag()` clears request flags with unlock semantics and wakes waiters.
- `netfs_is_cache_enabled()` gates cache use on valid cookie, backend private state, and enabled cookie.
- FS-Cache config stubs make callers compile when `CONFIG_FSCACHE` or stats/proc config is disabled.

Role in architecture:
- This header ties together the state machines in this group: fscache cookie/volume state, netfs I/O request lifetime, collector/retry paths, and proc/stat visibility.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/iterator.c -->
# File Research: sources/os/linux/linux/fs/netfs/iterator.c

Provides iterator extraction and span-limiting helpers for netfs I/O.

Important exported APIs:
- `netfs_extract_user_iter()`: pins/extracts pages from user iterators into a bvec iterator.
- `netfs_limit_iter()`: returns a byte span limited by max size and max segment count.

Supported iterator types in `netfs_limit_iter()`:
- `ITER_BVEC`.
- `ITER_KVEC`.
- `ITER_XARRAY`.
- `ITER_FOLIOQ`.

Important behavior:
- `netfs_extract_user_iter()` only accepts ubuf/iovec iterators, allocates bvec storage, places temporary page pointers at the end of that allocation, and advances the original iterator.
- Error cleanup only unpins pages when it is safe to trust the partial result.
- Xarray limiting scans folios under RCU and rejects value entries or hugetlb folios.
- Folio-queue limiting walks across linked `folio_queue` structures.

Dependencies:
- Generic `iov_iter` extraction APIs.
- Folio queue iterator support used by rolling buffer write/read machinery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/iterator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/locking.c -->
# File Research: sources/os/linux/linux/fs/netfs/locking.c

Implements serialization between buffered and direct I/O for netfs inodes.

Important exported APIs:
- `netfs_start_io_read()` / `netfs_end_io_read()`.
- `netfs_start_io_write()` / `netfs_end_io_write()`.
- `netfs_start_io_direct()` / `netfs_end_io_direct()`.

Concurrency model:
- Uses `inode->i_rwsem`.
- Uses `NETFS_ICTX_ODIRECT` to indicate direct I/O mode.
- Buffered reads take shared lock if no direct I/O mode is active.
- Buffered writes take write lock, clear/direct-drain O_DIRECT mode, then downgrade.
- Direct I/O takes shared lock if direct mode already active; otherwise takes write lock to block buffered I/O, flush/wait pagecache, then downgrades.

Important behavior:
- `netfs_block_o_direct()` clears direct mode and waits for outstanding DIO.
- `netfs_block_buffered()` sets direct mode, unmaps pagecache, and waits for writeback.
- Interruptible/killable lock acquisition maps to `-ERESTARTSYS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/main.c -->
# File Research: sources/os/linux/linux/fs/netfs/main.c

Module/init code for generic network filesystem support.

Key responsibilities:
- Defines module metadata and `netfs_debug` module parameter.
- Exports `netfs_sreq` tracepoint.
- Creates request and subrequest slab caches plus mempools.
- Creates `/proc/fs/netfs` and `requests` proc file.
- Creates `stats` proc file when FS-Cache stats are enabled.
- Calls `fscache_init()` after netfs base resources are ready.

Important globals:
- `netfs_request_pool`.
- `netfs_subrequest_pool`.
- `netfs_io_requests`.
- `netfs_proc_lock`.

Important behavior:
- `netfs_requests_seq_show()` displays active request debug id, origin, refcount, flags, error, start/submitted/length.
- Init is registered with `fs_initcall(netfs_init)`.
- Exit tears down FS-Cache, procfs, mempools, and slabs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/misc.c -->
# File Research: sources/os/linux/linux/fs/netfs/misc.c

Miscellaneous netfs helper routines for folio queues, dirty/release handling, iterator reset, and request waiting.

Important exported APIs:
- `netfs_alloc_folioq_buffer()`.
- `netfs_free_folioq_buffer()`.
- `netfs_dirty_folio()`.
- `netfs_unpin_writeback()`.
- `netfs_clear_inode_writeback()`.
- `netfs_invalidate_folio()`.
- `netfs_release_folio()`.

Important internal APIs:
- `netfs_reset_iter()`.
- `netfs_wake_collector()`.
- `netfs_subreq_clear_in_progress()`.
- `netfs_wait_for_in_progress_stream()`.
- `netfs_wait_for_read()`.
- `netfs_wait_for_write()`.
- `netfs_wait_for_paused_read()`.
- `netfs_wait_for_paused_write()`.

Important behavior:
- Dirtying a folio can pin the FS-Cache cookie for later writeback using inode state `I_PINNING_NETFS_WB`.
- Invalidate/release paths update zero-point metadata and handle private netfs folio state.
- Collectors may run in the application thread or on a workqueue depending on `NETFS_RREQ_OFFLOAD_COLLECTION`.
- Wait helpers collect progress opportunistically before sleeping.
- Completed reads/writes return transferred length unless failure or unexpected short transfer requires an error.

Dependencies:
- Request collectors from `read_collect.c` and `write_collect.c`.
- Folio queue allocation from `rolling_buffer.c`.
- FS-Cache cookie pin/unpin APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/objects.c -->
# File Research: sources/os/linux/linux/fs/netfs/objects.c

Handles lifetime, allocation, refcounting, cleanup, and tracing for netfs I/O requests and subrequests.

Important APIs:
- `netfs_alloc_request()`.
- `netfs_get_request()`.
- `netfs_put_request()`.
- `netfs_put_failed_request()`.
- `netfs_alloc_subrequest()`.
- `netfs_get_subrequest()`.
- `netfs_put_subrequest()`.
- `netfs_clear_subrequests()`.

Important behavior:
- Requests and subrequests are mempool-backed to survive memory pressure.
- Requests start with refcount 2 and `NETFS_RREQ_IN_PROGRESS` set.
- Read origins get read collection work; write origins get write collection work.
- Optional netfs `init_request`, `free_request`, and `free_subrequest` hooks are honored.
- Request cleanup cancels collector work, removes proc visibility, clears subrequests, ends cache operation, unpins direct bvec pages, clears rolling buffer, and decrements inode I/O count.
- Final request memory free is RCU-delayed.
- Subrequests hold a reference on the parent request.

Risk/attention points:
- Mempool allocation loops sleep/retry indefinitely.
- `netfs_put_failed_request()` assumes the request is newly allocated with exactly two refs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/objects.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_collect.c -->
# File Research: sources/os/linux/linux/fs/netfs/read_collect.c

Collects, assesses, unlocks, completes, and retries netfs read subrequests.

Key responsibilities:
- Consumes completed read subrequests in stream order.
- Advances collected and cleaned positions.
- Unlocks folios when all data covering them has arrived or been zero-filled.
- Detects short reads, EOF, retry requests, cache read failures, and permanent server failures.
- Completes direct/unbuffered/single reads and invokes callbacks.
- Handles cache-read completion callbacks.

Important exported APIs:
- `netfs_read_subreq_progress()`.
- `netfs_read_subreq_terminated()`.
- `netfs_cache_read_terminated()`.

Important internal APIs:
- `netfs_read_collection()`.
- `netfs_read_collection_worker()`.
- `netfs_cancel_read()`.

Important behavior:
- Buffered reads can mark downloaded folios for copy-to-cache.
- Short reads may zero unread tails if EOF or clear-tail flags are set.
- Cache read failures become retryable server downloads.
- Server download failures become request failures.
- Completed DIO/unbuffered reads flush destination pages, update `ki_pos`, call `ki_complete`, and end DIO.
- Single-object reads mark inode dirty when data downloaded from server should be cached.

Concurrency model:
- Uses stream list head ordering.
- Reads `IN_PROGRESS` with acquire semantics before counters.
- Wakes waiters by clearing `NETFS_RREQ_IN_PROGRESS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_collect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_pgpriv2.c -->
# File Research: sources/os/linux/linux/fs/netfs/read_pgpriv2.c

Deprecated bridge for copying read folios to cache using `PG_private_2`.

Key responsibilities:
- Creates a copy-to-cache write request when a downloaded folio needs cache storage.
- Appends folios to the write request rolling buffer.
- Splits large folios into cache write subrequests.
- Ends copy-to-cache writes and clears `PG_private_2` as copied ranges complete.

Important APIs:
- `netfs_pgpriv2_copy_to_cache()`.
- `netfs_pgpriv2_end_copy_to_cache()`.
- `netfs_pgpriv2_unlock_copied_folios()`.

Important behavior:
- If cache resources are invalid or write request creation fails, copy-to-cache is disabled for the read request.
- Folios beyond EOF are immediately unmarked.
- Copy writes use stream 1, `NETFS_PGPRIV2_COPY_TO_CACHE`, and offloaded collection.
- Completion clears `PG_private_2` only after collected range reaches the folio end or EOF-limited end.

Note:
- File explicitly marks this path deprecated; newer folio-private mechanisms are preferred elsewhere in netfs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_pgpriv2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_retry.c -->
# File Research: sources/os/linux/linux/fs/netfs/read_retry.c

Implements retry handling for failed or partial netfs read subrequests.

Key responsibilities:
- Waits for outstanding reads to quiesce.
- Reissues retryable subrequests.
- Converts failed cache reads to server downloads.
- Renegotiates read sizes through netfs callbacks.
- Splits or discards subrequests when retry sizing changes.
- Unlocks abandoned read folios at request completion.

Important APIs:
- `netfs_retry_reads()`.
- `netfs_unlock_abandoned_read_pages()`.

Important behavior:
- If no `prepare_read` and no cache resources are involved, retry simply resets iterators and reissues subrequests.
- Otherwise, it rebuilds contiguous retry spans, switches source to `NETFS_DOWNLOAD_FROM_SERVER`, and uses `prepare_read()` plus `netfs_limit_iter()` to enforce max length/segment limits.
- Can allocate additional subrequests if a retry span needs more pieces than before.
- If allocation or preparation fails, remaining retryable subrequests are marked failed.
- `NETFS_RREQ_RETRYING` prevents normal collector wake behavior while streams are quiescing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_retry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_single.c -->
# File Research: sources/os/linux/linux/fs/netfs/read_single.c

Supports synchronous reads of single monolithic netfs objects, such as AFS directory blobs.

Important exported APIs:
- `netfs_single_mark_inode_dirty()`.
- `netfs_read_single()`.

Key responsibilities:
- Reads one object into a caller-provided iterator using one subrequest at a time.
- Tries cache first when available, otherwise downloads from server.
- Marks object inode dirty after server download if data should be stored in cache.
- Pins cache cookie for writeback when needed.

Important behavior:
- `netfs_read_single()` allocates a `NETFS_READ_SINGLE` request, begins cache read if possible, dispatches one subrequest, waits synchronously, and returns transferred/error.
- The buffer may be larger than content; unused beyond EOF is handled by read completion logic.
- Cache-only dirty marking is skipped if no cache is enabled and `NETFS_ICTX_SINGLE_NO_UPLOAD` is set.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/read_single.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/rolling_buffer.c -->
# File Research: sources/os/linux/linux/fs/netfs/rolling_buffer.c

Implements rolling folio-queue buffers used by netfs read/write issue and collection paths.

Important exported APIs:
- `netfs_folioq_alloc()`.
- `netfs_folioq_free()`.

Important internal APIs:
- `rolling_buffer_init()`.
- `rolling_buffer_make_space()`.
- `rolling_buffer_load_from_ra()`.
- `rolling_buffer_append()`.
- `rolling_buffer_delete_spent()`.
- `rolling_buffer_clear()`.

Important behavior:
- Rolling buffer starts with an empty queue so producer and consumer pointers can move independently.
- `rolling_buffer_make_space()` allocates a new queue when the head is full and publishes `next` with release semantics.
- Readahead folios are loaded into queue slots and added to a put batch.
- Appended folios may be marked for later put/release decisions.
- Consumer deletes spent queues but keeps the final placeholder queue.
- Clear releases marked folios through a folio batch.

Role:
- Provides the moving backing storage for `ITER_FOLIOQ` request iterators and collector cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/rolling_buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/stats.c -->
# File Research: sources/os/linux/linux/fs/netfs/stats.c

Defines generic netfs statistics counters and seq-file rendering.

Counters cover:
- Read entry points and subrequest/request object counts.
- Downloads, cache reads, zeroing, short reads, read retries.
- Buffered/write-through/direct/writeback/copy-to-cache write paths.
- Upload/cache-write completions and failures.
- Write retries.
- Writeback lock skip/wait counts.
- Folio queue allocations.

Important API:
- `netfs_stats_show()`: prints netfs counters and then calls `fscache_stats_show()`.

Export:
- `netfs_stats_show` is exported for proc integration.

Relationship:
- Displayed from `fs/netfs/stats` when enabled by config.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/write_collect.c -->
# File Research: sources/os/linux/linux/fs/netfs/write_collect.c

Collects, assesses, completes, and retries netfs write subrequests.

Key responsibilities:
- Tracks multiple write streams, typically upload-to-server and write-to-cache.
- Advances request collection point to the minimum collected offset across active streams.
- Ends folio writeback only after all required streams have completed the folio range.
- Handles stream failures, partial writes, retries, cache invalidation on cache write failure, and async kiocb completion.
- Releases netfs writeback group refs after folios are written back.

Important exported APIs:
- `netfs_folio_written_back()`.
- `netfs_write_subrequest_terminated()`.

Important internal APIs:
- `netfs_write_collection()`.
- `netfs_write_collection_worker()`.

Important behavior:
- Streaming write metadata is detached once writeback completes.
- `NETFS_FOLIO_COPY_TO_CACHE` folios are treated specially and do not upload to server.
- Server upload failures set mapping errors.
- Cache write failures can invalidate cache via netfs op but do not necessarily fail server writeback.
- Partial successful writes set `NETFS_SREQ_NEED_RETRY`.
- Completion clears `NETFS_RREQ_IN_PROGRESS`, updates `ki_pos`, and completes async `kiocb` if present.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/write_collect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/write_issue.c -->
# File Research: sources/os/linux/linux/fs/netfs/write_issue.c

High-level writeback and write-through issuing engine for netfs.

Key responsibilities:
- Creates write requests with upload and cache streams.
- Converts dirty folios into write subrequests.
- Handles normal writeback, write-through writes, copy-to-cache writes, and monolithic single-object writeback.
- Drives rolling-buffer iterator advancement.
- Issues subrequests when size/segment limits, discontinuities, EOF, or stream changes require flushing.

Important exported APIs:
- `netfs_prepare_write_failed()`.
- `netfs_writepages()`.
- `netfs_begin_writethrough()`.
- `netfs_advance_writethrough()`.
- `netfs_end_writethrough()`.
- `netfs_writeback_single()`.

Important internal APIs:
- `netfs_create_write_req()`.
- `netfs_prepare_write()`.
- `netfs_reissue_write()`.
- `netfs_issue_write()`.
- `netfs_advance_write()`.

Important behavior:
- `netfs_create_write_req()` initializes stream 0 for server upload and stream 1 for cache write if cache resources are valid.
- `netfs_write_folio()` handles EOF truncation/zeroing, streaming write dirty ranges, writeback groups, cache-copy-only folios, and multi-stream submission ordering.
- `netfs_writepages()` serializes with `ictx->wb_lock`; `WB_SYNC_NONE` can skip on lock contention.
- Unrecoverable startup failure kills dirty pages to avoid endless dirty state.
- Write-through holds `wb_lock` across the operation and can return `-EIOCBQUEUED` for async completion.
- Single-object writeback requires an `ITER_FOLIOQ` iterator and writes all folios as one logical object.

Design note:
- The file documents the core netfs write model: multiple parallel streams overlay a sequence of variable-sized folios.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/write_issue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/netfs/write_retry.c -->
# File Research: sources/os/linux/linux/fs/netfs/write_retry.c

Implements retry handling for netfs write streams.

Key responsibilities:
- Waits for all active write streams to quiesce.
- Reissues retryable write subrequests.
- Renegotiates write sizes through stream `prepare_write`.
- Splits or discards subrequests when retry sizing changes.
- Allocates additional subrequests when a remaining span requires more pieces.

Important API:
- `netfs_retry_writes()`.

Important behavior:
- Retries are per stream; upload streams may call netfs `retry_request()`.
- If a stream has no `prepare_write`, retry resets the iterator and resubmits directly.
- With `prepare_write`, retry rebuilds contiguous spans, applies `netfs_limit_iter()`, and preserves boundary flags where needed.
- Stream sources drive retry accounting: server upload increments upload stats, cache write increments cache write stats.
- Contains TODO hooks for future encrypted-content read-modify-write handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/netfs/write_retry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/nfs/Kconfig

Defines Linux NFS client configuration options.

Major options:
- `NFS_FS`: base NFS client support; depends on networking, file locking, and multiuser support; selects CRC32, LOCKD, SUNRPC, and NFS common code.
- `NFS_V2`, `NFS_V3`, `NFS_V3_ACL`.
- `NFS_V4`, `NFS_V4_0`, `NFS_V4_2`.
- `NFS_SWAP`.
- `PNFS_FILE_LAYOUT`, `PNFS_BLOCK`, `PNFS_FLEXFILE_LAYOUT`.
- `ROOT_NFS`.
- `NFS_FSCACHE`.
- DNS resolver options.
- Debug and UDP-disable options.
- `NFS_V4_2_READ_PLUS`.

Important relationships:
- `NFS_FSCACHE` depends on `NFS_FS` and selects `NETFS_SUPPORT` plus `FSCACHE`.
- `PNFS_BLOCK` depends on `NFS_V4 && BLK_DEV_DM` and defaults to `NFS_V4`.
- NFSv4 selects key management and SUNRPC backchannel support.
- Kernel DNS resolver is selected unless legacy DNS resolver is enabled.

Role in this group:
- Connects NFS client caching to the generic netfs/FS-Cache stack researched above.
- Enables block pNFS layout driver support researched in `blocklayout.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/Makefile -->
# File Research: sources/os/linux/linux/fs/nfs/Makefile

Build rules for the Linux NFS client.

Key behavior:
- Builds `nfs.o` when `CONFIG_NFS_FS` is enabled.
- Core NFS object list includes client, dir, file, inode, super, I/O, direct I/O, pagelist, read/write, namespace, mount client, trace, export, sysfs, and fs_context code.
- Adds optional objects:
  - `nfsroot.o` for `CONFIG_ROOT_NFS`.
  - `sysctl.o` for `CONFIG_SYSCTL`.
  - `fscache.o` for `CONFIG_NFS_FSCACHE`.
  - `localio.o` for `CONFIG_NFS_LOCALIO`.
- Builds separate modules/objects for NFSv2, NFSv3, and NFSv4.
- Adds layout subdirectories:
  - `filelayout/`
  - `blocklayout/`
  - `flexfilelayout/`

Role:
- Wires NFS fscache integration and pNFS block layout into kernel build based on Kconfig.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/Makefile -->
# File Research: sources/os/linux/linux/fs/nfs/blocklayout/Makefile

Builds the pNFS block layout driver.

Key rule:
- `obj-$(CONFIG_PNFS_BLOCK) += blocklayoutdriver.o`

Role:
- Compiles the block layout driver module when pNFS block layout support is configured.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.c -->
# File Research: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.c

Implements the NFSv4.1 pNFS block and SCSI layout driver.

Key responsibilities:
- Maps NFS page I/O to local block-device bios using pNFS extents.
- Handles parallel bio completion and final pNFS callbacks.
- Decodes layout extents from XDR.
- Verifies extent ordering/coverage constraints.
- Manages layout segment allocation/free and range return.
- Registers both block volume and SCSI layout driver types.
- Integrates with NFS pageio coalescing and layoutcommit.

Important components:
- `struct parallel_io`: refcounts multiple bios under one pNFS read/write operation.
- `do_add_page_to_bio()`: translates file sectors through extent/device maps and appends pages to bios.
- `bl_read_pagelist()`: reads pages from block devices or zero-fills holes.
- `bl_write_pagelist()`: writes full pages to block devices.
- `verify_extent()`: validates READ/RW extent sequences.
- `bl_alloc_lseg()`: decodes XDR extent list into the extent tree.
- `bl_pg_init_read/write()` and `bl_pg_test_read/write()`: enforce alignment and initialize pNFS pageio.
- `blocklayout_type` and `scsilayout_type`: registered pNFS layout drivers.

Important behavior:
- Holes are detected from extent state and zero-filled without device I/O.
- Device mapping failures mark device IDs unavailable, set layout failure, and trigger fallback.
- Bio errors set `pnfs_error`, mark layout segment failed, and mark devices unavailable.
- Writes mark extents written and update layoutcommit state after successful I/O.
- Direct I/O requires sector/page alignment depending on read/write path; misaligned requests fall back to metadata server.
- Server `pnfs_blksize` must be nonzero and no larger than `PAGE_SIZE`.

Dependencies:
- NFS pNFS core APIs.
- Block device/bio APIs.
- Extent tree helpers from `extent_tree.c`.
- Device registration helpers from `dev.c`.
- rpc_pipefs helpers for block device resolution.

Module registration:
- Registers aliases `nfs-layouttype4-3` and `nfs-layouttype4-5`.
- Init creates pipefs integration and registers both layout types.
- Exit unregisters both layout types and cleans pipefs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.h -->
# File Research: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.h

Private header for the NFS pNFS block layout driver.

Key definitions:
- Sector/page constants: `PAGE_CACHE_SECTORS`, `PAGE_CACHE_SECTOR_SHIFT`, `SECTOR_SIZE`.
- Limits for UUIDs, devices, and UUID length.
- `struct pnfs_block_volume`: represents simple, slice, concat, stripe, and SCSI volume descriptions.
- `struct pnfs_block_dev_map`: maps a logical range to a block device and disk offset.
- `struct pnfs_block_dev`: pNFS device node with hierarchy, block device file, disk offset, flags, persistent reservation key, and map callback.
- `struct pnfs_block_extent`: sector-granular file extent with device, file offset, length, volume offset, state, and commit tags.
- `struct pnfs_block_layout`: layout header plus read/write extent trees, lock, SCSI flag, and last-written byte.
- rpc_pipefs message structures and constants.

Important helpers:
- `BLK_LO2EXT()`.
- `BLK_LSEG2EXT()`.

Declared cross-file APIs:
- Device registration/allocation/free from `dev.c`.
- Extent tree insert/remove/lookup/commit helpers from `extent_tree.c`.
- Device resolution and pipefs init/cleanup from `rpc_pipefs.c`.

Role:
- Defines the shared data model used by `blocklayout.c` to translate NFS pNFS extents into local block-device I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.h -->