# Research Report: subset-b-005687

Work item `subset-b-005687` covers Linux netfs/FS-Cache support files and NFS pNFS block layout files under `sources/distributed-fs/ceph-client/fs`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_cookie.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_cookie.c

## Purpose
Implements FS-Cache data-object cookie lifetime management. A cookie represents one cached netfs object inside a volume; this file handles allocation, key hashing, duplicate detection, asynchronous lookup/create/invalidate/withdraw/relinquish transitions, LRU discard, procfs inspection, and exported cookie reference/access APIs.

## Important APIs, Types, And Functions
Key exports are `__fscache_acquire_cookie()`, `__fscache_use_cookie()`, `__fscache_unuse_cookie()`, `__fscache_relinquish_cookie()`, `__fscache_invalidate()`, `fscache_begin_cookie_access()`, `fscache_end_cookie_access()`, `fscache_withdraw_cookie()`, `fscache_get_cookie()`, and `fscache_put_cookie()`. Internal anchors include `fscache_cookie_hash[]`, `fscache_cookies`, `fscache_cookie_lru`, `fscache_cookie_state_machine()`, `fscache_perform_lookup()`, `fscache_perform_invalidation()`, and `fscache_unhash_cookie()`. The state enum is defined externally, but this file drives states such as `QUIESCENT`, `LOOKING_UP`, `CREATING`, `ACTIVE`, `INVALIDATING`, `LRU_DISCARDING`, `WITHDRAWING`, `RELINQUISHING`, `FAILED`, and `DROPPED`.

## Control Flow
Acquire validates key/aux lengths, allocates a slab cookie, hashes it under a bucket lock, and pins the parent volume. First use increments `n_active`; a quiescent cookie begins volume access, pins cookie access, marks `IS_CACHING`, and queues work for lookup. The worker serializes lookup, prepare-to-write, invalidation, LRU discard, withdrawal, and relinquish. `__fscache_unuse_cookie()` updates aux/size when requested, decrements active use, and moves inactive cached cookies onto the LRU. The timer/workqueue later sets `DO_LRU_DISCARD` and withdraws only if there are no active users/accesses. Invalidation sets `NO_DATA_TO_READ`, updates coherency data and size, and queues the worker if active; lookup-time invalidation is deferred with `DO_INVALIDATE`.

## State And Persistence
Persistent cache identity is `(volume, key_hash, key bytes)` with aux data and object size stored on the cookie. In-memory state is guarded by `cookie->lock`, bucket locks, refcounts, `n_active`, `n_accesses`, and flag bits. Cache backend persistence is reached through `cookie->volume->cache->ops` for `lookup_cookie()`, `prepare_to_write()`, `invalidate_cookie()`, and `withdraw_cookie()`.

## Dependencies And Integration Points
Depends on `internal.h`, tracepoints, FS-Cache cache/volume operations, the shared `fscache_wq`, procfs seq support, timers, and hlist bucket locks. Netfs clients call public wrappers from `<linux/fscache.h>`; cache backends call exported state helpers such as lookup-negative, resume-after-invalidation, and caching-failed.

## Risks
High-risk areas are collision waiting, access gate ordering, LRU races with new use, invalidation while lookup/create is in flight, and ensuring `n_accesses` reaches zero before withdrawal. `fscache_free_cookie()` warns rather than freeing a hashed cookie, so missing unhash paths leak. State transitions rely on barriers around `cookie->state` and flag/counter ordering.

## Test Signals
Exercise duplicate-key acquisition, acquire/relinquish with racing reacquire, use/unuse LRU expiry, invalidation during lookup and active IO, backend lookup failure, cache withdrawal while IO is pinned, and procfs cookie listing. Tracepoints and FS-Cache stats should reflect acquire, LRU, invalidation, relinquish, and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_internal.h -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_internal.h

## Purpose
Tiny compatibility header that includes netfs `internal.h` and changes `pr_fmt()` to report `FS-Cache:` rather than `netfs:`. It exists so FS-Cache-specific implementation files can share the central internal declarations while using cache-specific printk prefixes.

## Important APIs, Types, And Functions
No functions or types are declared here beyond the inherited contents of `internal.h`. Its only local behavior is undefining any existing `pr_fmt` and redefining it as `#define pr_fmt(fmt) "FS-Cache: " fmt`.

## Control Flow
There is no runtime control flow. The file participates at preprocessing time: include `internal.h`, reset the logging prefix, and let FS-Cache source files compile with the shared internal API surface.

## State And Persistence
No state is owned. It indirectly exposes all state declared in `internal.h`, including netfs pools, request lists, FS-Cache stats, cache state helpers, cookie/volume declarations, and debug macros.

## Dependencies And Integration Points
Depends directly on sibling `internal.h`. It integrates with FS-Cache implementation files that want netfs internals plus a cache-specific log prefix.

## Risks
The main risk is include-order confusion. Because it includes `internal.h` before redefining `pr_fmt`, any logging macros expanded inside included headers keep their own definitions, while later source logging uses `FS-Cache:`. It should stay minimal to avoid divergent declarations from `internal.h`.

## Test Signals
Build coverage is the useful signal. Compile FS-Cache files with and without debug enabled and verify messages from files including this header use the expected prefix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_io.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_io.c

## Purpose
Provides FS-Cache cache-object IO helpers for netfs read/write operations. It begins cache operations once a cookie reaches a usable state, writes page-cache/xarray data to the cache, clears deprecated `PG_private_2` bits after copy-to-cache completion, and resizes cached objects under netfs inode serialization.

## Important APIs, Types, And Functions
Exports `fscache_wait_for_operation()`, `__fscache_begin_read_operation()`, `__fscache_begin_write_operation()`, `__fscache_clear_page_bits()`, `__fscache_write_to_cache()`, and `__fscache_resize_cookie()`. Internal `fscache_begin_operation()` pins cookie access and binds a `netfs_cache_resources` to the cache backend. `struct fscache_write_request` carries async write completion context.

## Control Flow
`fscache_begin_operation()` initializes cache resources, calls `fscache_begin_cookie_access()`, examines the cookie state under lock, waits through lookup/create/invalidate/LRU-discard states, and then calls backend `begin_operation()`. If the cookie is dropped/relinquishing/not live, it tears down resources and returns `-ENOBUFS`. `__fscache_write_to_cache()` allocates a write request, begins a `FSCACHE_WANT_WRITE` operation, lets the backend adjust write range via `prepare_write()`, constructs an xarray iterator over mapping pages, and dispatches `fscache_write()` with completion callback `fscache_wreq_done()`.

## State And Persistence
State lives in `netfs_cache_resources` (`ops`, `cache_priv`, `cache_priv2`, `debug_id`, `inval_counter`) and in backend private state attached by `begin_operation()`. Persistent data changes are delegated to cache backend `read/write/resize` operations. `__fscache_resize_cookie()` sets `FSCACHE_COOKIE_NEEDS_UPDATE` and invokes backend `resize_cookie()` synchronously.

## Dependencies And Integration Points
Integrates `struct fscache_cookie`, netfs cache resource operations, xarray iterators, folio private bits, and backend FS-Cache ops. It is used by read/write paths that need a cache operation token before touching cache storage.

## Risks
Risks include deadlock or long waits if cookie state does not progress, stale IO after invalidation if `inval_counter` is ignored by callers, incorrect range truncation from backend `prepare_write()`, and missing `fscache_end_operation()` on error paths. Deprecated `PG_private_2` handling is explicitly transitional.

## Test Signals
Test cache read/write begin during lookup, invalidate, dropped cookie, backend offline, and cache resize. Verify async write completion clears private bits and always ends operations. Fault injection around allocation and backend `prepare_write()` should preserve callbacks and page bit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_main.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_main.c

## Purpose
Initializes and tears down the FS-Cache subsystem embedded in netfs support. It also defines the stable FS-Cache hash used for volume/cookie keys and exports FS-Cache tracepoints and the global FS-Cache workqueue.

## Important APIs, Types, And Functions
Exports tracepoints `fscache_access_cache`, `fscache_access_volume`, and `fscache_access`, plus `fscache_wq`. Important functions are `fscache_hash()`, `fscache_init()`, and `fscache_exit()`. Internal `HASH_MIX()` and `fold_hash()` implement an architecture-stable hash over little-endian 32-bit words.

## Control Flow
During `fscache_init()`, the code allocates an unbound/freezable workqueue named `fscache`, initializes procfs entries, creates the cookie slab cache, and logs successful load. Error paths unwind procfs and the workqueue. `fscache_exit()` destroys the cookie slab, cleans procfs, shuts down the cookie LRU timer synchronously, destroys the workqueue, and logs unload.

## State And Persistence
Persistent on-disk compatibility depends on `fscache_hash()` being stable; comments note that key hash bits may appear on disk. Runtime state includes `fscache_wq` and `fscache_cookie_jar`. The hash caller must pass data padded to a multiple of four bytes.

## Dependencies And Integration Points
Depends on `internal.h`, module/init APIs, trace/events/fscache, proc initialization, cookie slab allocation, and the LRU timer declared in cookie management. Called from `netfs_init()` when `CONFIG_FSCACHE` is enabled.

## Risks
Changing the hash algorithm breaks cache identity compatibility. Teardown order matters: workers/timers must not outlive slabs or proc entries they reference. Initialization failure must avoid leaving `/proc/fs/netfs` partial FS-Cache files.

## Test Signals
Build/load/unload FS-Cache repeatedly, verify proc entries appear and disappear, tracepoints are exported, workqueue exists, and collision-sensitive volume/cookie keys hash consistently across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_proc.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_proc.c

## Purpose
Creates the FS-Cache procfs inspection interface under the netfs proc tree and a compatibility symlink `/proc/fs/fscache` to `/proc/fs/netfs`.

## Important APIs, Types, And Functions
Defines `fscache_proc_init()` and `fscache_proc_cleanup()`. It installs seq files for `fs/netfs/caches`, `fs/netfs/volumes`, and `fs/netfs/cookies` using seq operations from cache, volume, and cookie code.

## Control Flow
Initialization creates the symlink first, then each seq file. Any failure removes the symlink and returns `-ENOMEM`. Cleanup removes the `fs/fscache` subtree; the broader `fs/netfs` subtree is owned by netfs main initialization and cleanup.

## State And Persistence
No persistent storage. Runtime visibility reflects global cache, volume, and cookie lists guarded in their respective modules.

## Dependencies And Integration Points
Depends on `CONFIG_PROC_FS`, procfs helpers, `seq_file`, and `internal.h` declarations for `fscache_caches_seq_ops`, `fscache_volumes_seq_ops`, and `fscache_cookies_seq_ops`. Called by FS-Cache init/exit.

## Risks
Partial proc creation failures are simple but only remove the symlink by name; ownership with netfs main proc tree must stay aligned. Seq operation providers must remain valid for the lifetime of proc entries.

## Test Signals
With procfs enabled, verify `/proc/fs/fscache` symlink, `caches`, `volumes`, and `cookies` files exist after load and are removed on unload. Failure injection in proc creation should not leave stale entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_stats.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_stats.c

## Purpose
Owns FS-Cache statistic counters and renders them through seq_file output, normally as the FS-Cache tail of `/proc/fs/netfs/stats`.

## Important APIs, Types, And Functions
Defines counters for volumes, cookies, LRU, acquisitions, invalidations, updates, relinquishes, resizes, IO, no-space events, culling, and DIO misfits. Several backend-facing counters are exported: `fscache_n_updates`, `fscache_n_read`, `fscache_n_write`, `fscache_n_no_write_space`, `fscache_n_no_create_space`, `fscache_n_culled`, and `fscache_n_dio_misfit`. `fscache_stats_show()` prints grouped counts.

## Control Flow
There is no state machine. Callers increment/decrement atomic counters through `fscache_stat()` helpers from `internal.h`; proc display atomically snapshots them and includes LRU timer remaining time when pending.

## State And Persistence
All state is in `atomic_t` counters and the externally declared cookie LRU timer. Counters reset at module load and are not persistent.

## Dependencies And Integration Points
Depends on `CONFIG_FSCACHE_STATS`, seq_file, procfs, and `internal.h`. Called by `netfs_stats_show()` after netfs statistics so users can inspect netfs and FS-Cache behavior together.

## Risks
Counters are diagnostic only and may be approximate under concurrency. Miscounted increments/decrements can mislead troubleshooting, particularly active cookie/volume counts and LRU depth.

## Test Signals
Run cache acquisition/use/relinquish, invalidation, no-space/cull, read/write, and resize paths and confirm expected counter movement. Check `LRU at=` changes when the LRU timer is armed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_volume.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_volume.c

## Purpose
Manages FS-Cache volume cookies. A volume groups data-object cookies under a cache and volume key, handles backend volume acquisition/free, collision waiting, access pinning, withdrawal, relinquish coherency data, and procfs display.

## Important APIs, Types, And Functions
Exports `fscache_try_get_volume()`, `fscache_end_volume_access()`, `__fscache_acquire_volume()`, `fscache_put_volume()`, `__fscache_relinquish_volume()`, and `fscache_withdraw_volume()`. Internal functions include `fscache_alloc_volume()`, `fscache_hash_volume()`, `fscache_create_volume()`, `fscache_create_volume_work()`, `fscache_unhash_volume()`, and `fscache_free_volume()`.

## Control Flow
Acquire looks up a cache by name, allocates a variable-sized `fscache_volume` with coherency data, builds a length-prefixed padded key, hashes it, links it into proc/cache lists, inserts it into a bucket, and schedules backend volume creation. Hash collision with a non-relinquished equivalent fails with `-EBUSY`; collision with a relinquishing volume sets pending bits and waits for wakeup. `fscache_create_volume()` serializes backend `acquire_volume()` via `FSCACHE_VOLUME_CREATING` and can wait synchronously. Refcount drop calls `fscache_free_volume()`, which may invoke backend `free_volume()`, unlinks proc/cache state, unhashes, frees memory, and drops the cache reference.

## State And Persistence
Volume identity is `(cache, key_hash, key bytes)`. Runtime state includes `ref`, `n_accesses`, `n_cookies`, flags, `cache_priv`, coherency bytes, and proc/hash/list linkage. Access pinning prevents cache withdrawal while a volume is in use.

## Dependencies And Integration Points
Integrates with cache lookup/refcounting, backend cache ops, `fscache_addremove_sem`, cookie acquisition, procfs seq output, and FS-Cache stats. Cookie code pins volumes and increments `volume->n_cookies`.

## Risks
Potential hazards include collision wait deadlocks, incorrect wake of pending colliders, freeing backend volume while accesses remain, and mismatched `n_cookies` accounting. Volume withdrawal decrements the artificial access pin and waits for zero, so callers must balance access pins.

## Test Signals
Acquire/relinquish identical volume keys concurrently, simulate backend create failure, withdraw active volumes, and verify proc `volumes` output. Check collision stats and `n_cookies` transitions when cookies are acquired/relinquished.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/fscache_volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/internal.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/iterator.c -->
# sources/distributed-fs/ceph-client/fs/netfs/iterator.c

## Purpose
Provides iterator helpers used by netfs IO dispatch and retry paths. It can extract user iterators into bvec-backed iterators and compute how much of a given iterator can be submitted under size and segment constraints.

## Important APIs, Types, And Functions
Exports `netfs_extract_user_iter()` and `netfs_limit_iter()`. Internal limiters handle bvec, kvec, xarray, and folio_queue iterators: `netfs_limit_bvec()`, `netfs_limit_kvec()`, `netfs_limit_xarray()`, and `netfs_limit_folioq()`.

## Control Flow
`netfs_extract_user_iter()` verifies the source is ubuf/iovec, allocates one buffer large enough for bvecs and page pointers, repeatedly calls `iov_iter_extract_pages()`, builds bvec entries with offsets and lengths, advances the original iterator, then initializes a bvec iterator. `netfs_limit_iter()` dispatches by iterator type; each limiter skips `start_offset`, walks segments, and returns a span capped by `max_size` and `max_segs`.

## State And Persistence
No persistent state. The extraction result owns allocated bvec storage whose cleanup mode is determined by generic iov_iter extraction APIs. Limiters are read-only over iterator descriptors and underlying arrays/xarrays/folio queues.

## Dependencies And Integration Points
Used by read/write retry code when negotiated max IO length or segment count requires splitting a retry span. Depends on Linux `iov_iter`, xarray, folio queue, bvec, kvec, and page extraction APIs.

## Risks
Risks include iterator type mismatch, off-by-one segment limiting, overrun of allocated bvec/page-pointer storage, and RCU visibility while scanning xarrays. The xarray limiter assumes no hugetlb folios and warns if encountering value entries.

## Test Signals
Unit-style tests should cover ubuf/iovec extraction with offsets, bvec/kvec/xarray/folioq limit calculations, zero count, start offset at boundaries, max segment caps, and retry splitting with negotiated `sreq_max_segs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/iterator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/locking.c -->
# sources/distributed-fs/ceph-client/fs/netfs/locking.c

## Purpose
Coordinates buffered and direct IO exclusion for network filesystems using inode `i_rwsem` and the netfs inode `NETFS_ICTX_ODIRECT` flag. It lets parallel operations of the same class proceed while switching classes waits for outstanding work and flushes page cache state.

## Important APIs, Types, And Functions
Exports `netfs_start_io_read()`, `netfs_end_io_read()`, `netfs_start_io_write()`, `netfs_end_io_write()`, `netfs_start_io_direct()`, and `netfs_end_io_direct()`. Internal helpers are `netfs_inode_dio_wait_interruptible()`, `netfs_block_o_direct()`, and `netfs_block_buffered()`.

## Control Flow
Buffered read starts with a shared `i_rwsem` lock and succeeds quickly if no direct-IO mode is active. If direct IO is active, it upgrades via exclusive lock, clears `NETFS_ICTX_ODIRECT`, waits for outstanding DIO, then downgrades to shared. Buffered write takes exclusive first, blocks direct IO similarly, and downgrades. Direct IO does the inverse: shared fast path when direct mode is already set; otherwise exclusive lock, set `NETFS_ICTX_ODIRECT`, unmap page cache, wait for writeback, then downgrade.

## State And Persistence
No persistent state. Runtime state is `NETFS_ICTX_ODIRECT`, `inode->i_rwsem`, inode DIO count, and mapping dirty/writeback state.

## Dependencies And Integration Points
Used by filesystem read/write/direct-IO entry points before invoking netfs helpers. Depends on generic inode DIO helpers, `filemap_fdatawait()`, and `unmap_mapping_range()`.

## Risks
Deadlock risk is controlled by documented lock assumptions, but callers must pair start/end correctly. Interruptible waits can return `-ERESTARTSYS`. Direct-IO transition must handle writeback errors and clear `ODIRECT` on failure.

## Test Signals
Stress mixed buffered reads, buffered writes, direct IO, truncate, and mmap writeback. Verify lock pairing with lockdep and that page-cache flush failures propagate from direct-mode transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/locking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/main.c -->
# sources/distributed-fs/ceph-client/fs/netfs/main.c

## Purpose
Module/init glue for the netfs support library. It creates request/subrequest slab caches and mempools, exposes procfs diagnostics, publishes tracepoints and debug module parameter, initializes embedded FS-Cache, and tears everything down.

## Important APIs, Types, And Functions
Defines module metadata and `netfs_debug` module parameter. Owns `netfs_request_pool`, `netfs_subrequest_pool`, `netfs_io_requests`, and `netfs_proc_lock`. Main functions are `netfs_init()` and `netfs_exit()`, plus proc seq operations for `/proc/fs/netfs/requests`.

## Control Flow
`netfs_init()` creates request slab, initializes request mempool, creates subrequest slab and mempool, creates `/proc/fs/netfs` and request/stat files when configured, then calls `fscache_init()`. Error paths unwind in reverse order. `netfs_exit()` calls `fscache_exit()`, removes proc subtree, exits mempools, and destroys slab caches.

## State And Persistence
Runtime state includes slabs/mempools and proc list of active IO requests. No persistent data is stored. The request proc output snapshots refcount, flags, error, origin, start/submitted/len.

## Dependencies And Integration Points
Depends on Linux module, mempool, procfs, seq_file, trace/events/netfs, and FS-Cache init. `objects.c` allocates from the pools and links requests into proc state.

## Risks
Initialization order is important: object allocation depends on pools, proc sequence files depend on active request list locking, and FS-Cache teardown must occur before destroying resources it can reference. Proc output reads active request structures under RCU.

## Test Signals
Module boot/init path, proc file creation, stats creation with `CONFIG_FSCACHE_STATS`, allocation pressure against mempools, and clean unload with no active requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/misc.c -->
# sources/distributed-fs/ceph-client/fs/netfs/misc.c

## Purpose
Collects netfs utility routines for folio-queue buffers, iterator reset, dirty/writeback pinning, folio invalidation/release, collector wakeups, and synchronous waits for read/write request completion or pause points.

## Important APIs, Types, And Functions
Exports `netfs_alloc_folioq_buffer()`, `netfs_free_folioq_buffer()`, `netfs_dirty_folio()`, `netfs_unpin_writeback()`, `netfs_clear_inode_writeback()`, `netfs_invalidate_folio()`, and `netfs_release_folio()`. Internal but central functions include `netfs_reset_iter()`, `netfs_wake_collector()`, `netfs_subreq_clear_in_progress()`, `netfs_wait_for_in_progress_stream()`, `netfs_wait_for_read()`, `netfs_wait_for_write()`, and pause wait helpers.

## Control Flow
Folio-queue allocation grows a chain until target size is met, allocating folios and marking slots for release. Dirtying delegates to `filemap_dirty_folio()` and pins the FS-Cache cookie once per inode writeback episode. Invalidation updates `zero_point`, waits for deprecated private_2, adjusts or removes `netfs_folio` dirty-range metadata, and drops dirty groups. Collector waits either sleep for workqueue completion or run collection in the caller via `netfs_collect_in_app()` when offload is disabled.

## State And Persistence
State touched includes folio queues, folio private/group metadata, inode `I_PINNING_NETFS_WB`, netfs inode `zero_point`, request flags (`IN_PROGRESS`, `OFFLOAD_COLLECTION`, `RETRYING`, `PAUSE`), stream active state, waitqueues, and transferred/error fields.

## Dependencies And Integration Points
Used by read/write collectors, retry paths, pagecache address_space ops, and FS-Cache writeback pinning. Depends on folio_queue, swap/pagecache, waitqueues, and fscache cookie helpers.

## Risks
Partial invalidation of streaming-write metadata is subtle. Collector wait logic relies on memory ordering in flag helpers. Release must avoid blocking reclaim improperly on `PG_private_2`. Cookie pin/unpin balance depends on filesystem write_inode/evict hooks.

## Test Signals
Stress partial folio invalidation, dirty/writeback pin balance, kswapd folio release, non-offloaded collection waits, pause/unpause during retry, and short read detection in `netfs_wait_for_in_progress()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/objects.c -->
# sources/distributed-fs/ceph-client/fs/netfs/objects.c

## Purpose
Owns allocation, reference counting, cleanup, and tracing for `netfs_io_request` and `netfs_io_subrequest` objects.

## Important APIs, Types, And Functions
Defines `netfs_alloc_request()`, `netfs_get_request()`, `netfs_clear_subrequests()`, `netfs_put_request()`, `netfs_put_failed_request()`, `netfs_alloc_subrequest()`, `netfs_get_subrequest()`, and `netfs_put_subrequest()`. Internal cleanup is split through `netfs_free_request()`, `netfs_deinit_request()`, `netfs_free_request_rcu()`, and `netfs_free_subrequest()`.

## Control Flow
Request allocation chooses a filesystem-specific mempool or the global pool, sleeps/retries until allocation succeeds, initializes origin-dependent collector work, two IO streams, waitqueue, locks, refcount of two, netfs ops, and optional `init_request()`. It increments the inode IO count and adds proc visibility. Last put queues cleanup work; cleanup cancels collector work, unlinks proc state, clears subrequests, frees netfs private state, ends cache resources, unpins direct pages, clears rolling buffer, decrements inode IO count, and frees via RCU. Subrequests similarly use per-netfs or global mempool and hold a request reference.

## State And Persistence
All state is transient. Request fields track start/len, origin, mapping/inode, i_size, streams, flags, buffer, direct bvecs, cache resources, and debug ids. Refcounting is the persistence boundary for async operations.

## Dependencies And Integration Points
Used by all read/write issue paths. Depends on mempools from `main.c`, netfs inode ops, proc helpers, rolling buffer, FS-Cache resources, RCU, and tracepoints.

## Risks
Refcount imbalance can leak or use-after-free requests/subrequests. `netfs_put_failed_request()` assumes a just-allocated refcount of two. Cleanup cancels work that has no own ref, so changing collector ref rules is risky. Allocation loops sleep indefinitely under severe memory pressure.

## Test Signals
Fault-inject `init_request()` failure, subrequest allocation pressure, async completion after caller return, direct IO bvec unpin cleanup, proc add/delete, and final wake on inode `io_count` reaching zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/objects.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_collect.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_collect.c

## Purpose
Collects read subrequest completions, unlocks/marks folios, handles cache copy-to-cache decisions, detects short/error/retry conditions, finalizes direct/single reads, and exposes termination/progress callbacks for filesystem and cache IO providers.

## Important APIs, Types, And Functions
Exports `netfs_read_subreq_progress()` and `netfs_read_subreq_terminated()`. Defines `netfs_read_collection()`, `netfs_read_collection_worker()`, `netfs_cache_read_terminated()`, `netfs_collect_read_results()`, `netfs_read_unlock_folios()`, `netfs_rreq_assess_dio()`, and `netfs_rreq_assess_single()`.

## Control Flow
The collector walks the front of read stream 0. It advances `stream->collected_to` from completed subrequests, clears unread tails for EOF/clear-tail short reads, marks cache-copy folios, abandons failed ranges, and removes consumed subrequests. Pending front subrequests stall collection. Retry requests set `NEED_RETRY`, pause the issuer, and call `netfs_retry_reads()`. Completion requires `ALL_QUEUED` and an empty stream; then transferred count is set, DIO/single-read completion callbacks run, IO accounting is updated, `IN_PROGRESS` is cleared/woken, abandoned pages are unlocked, and deprecated pgpriv2 copy-to-cache is ended.

## State And Persistence
Updates request `collected_to`, `cleaned_to`, `transferred`, `error`, `abandon_to`, stream `transferred`, folio uptodate/private/dirty/locked state, subrequest flags, and request flags such as `PAUSE`, `FAILED`, `SHORT_TRANSFER`, and `FOLIO_COPY_TO_CACHE`.

## Dependencies And Integration Points
Consumes subrequests issued by buffered/direct/single read paths and cache reads. Integrates with retry code, pgpriv2 copy-to-cache, folio queues, task IO accounting, iocb completion, and netfs `done()` callbacks.

## Risks
Ordering around `IN_PROGRESS` and transferred counters is critical. Folio unlock decisions must match collected ranges or pages can remain locked or become uptodate with holes. Cache read errors must retry from server without reporting false user errors unless server download fails.

## Test Signals
Test cache hit, cache miss fallback, short reads with EOF, clear-tail, retry after partial progress, server failure, abandoned ranges, direct IO completion, single-object cache-dirty marking, and copy-to-cache folio tagging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_collect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_pgpriv2.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_pgpriv2.c

## Purpose
Implements deprecated `PG_private_2` based copy-to-cache after reads. When read data was fetched from the server and should be cached, this file builds a separate write request to copy read folios into the local cache and clears `PG_private_2` as cache writes complete.

## Important APIs, Types, And Functions
Defines `netfs_pgpriv2_copy_to_cache()`, `netfs_pgpriv2_end_copy_to_cache()`, and `netfs_pgpriv2_unlock_copied_folios()`. Internal helpers are `netfs_pgpriv2_copy_folio()` and `netfs_pgpriv2_begin_copy_to_cache()`.

## Control Flow
The first folio needing copy-to-cache creates a `NETFS_PGPRIV2_COPY_TO_CACHE` write request if cache resources are valid and cache stream 1 is available. Each folio is marked private_2, appended to the rolling buffer, split into cache write subrequests by `netfs_advance_write()`, and issued as needed. At end of the parent read, outstanding cache writes are issued, `ALL_QUEUED` is set, the collector is poked if empty, and the copy request ref is dropped. The write collector calls `netfs_pgpriv2_unlock_copied_folios()` to end private_2 on completed folios.

## State And Persistence
State includes `rreq->copy_to_cache`, `NETFS_RREQ_FOLIO_COPY_TO_CACHE`, copy request buffer/streams, folio private_2 marks, and cache write subrequests. Persistent effect is backend cache writes.

## Dependencies And Integration Points
Used only from read collection and write collection. Depends on FS-Cache resources, write issue functions, rolling buffer, folio private_2 APIs, and netfs write collector behavior.

## Risks
The file is marked deprecated. Risks include private_2 waits blocking reclaim/invalidation, copy request setup failure silently disabling cache copy, EOF races with changing i_size, and ensuring all marked folios are unmarked even on cache write failure.

## Test Signals
Read-through-cache miss followed by copy-to-cache, cache unavailable during copy setup, partial final folio near EOF, cache write failure, and invalidation/release waiting for private_2 clearance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_pgpriv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_retry.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_retry.c

## Purpose
Retries failed or short read subrequests, especially converting failed cache reads into server downloads and renegotiating request sizes when a filesystem provides `prepare_read()` or `retry_request()`.

## Important APIs, Types, And Functions
Defines `netfs_retry_reads()` and `netfs_unlock_abandoned_read_pages()`. Internal functions are `netfs_reissue_read()` and `netfs_retry_read_subrequests()`.

## Control Flow
`netfs_retry_reads()` sets `RETRYING`, waits for all in-progress subrequests in stream 0 to quiesce, clears `RETRYING`, and rebuilds retryable subrequests. Simple mode resubmits each `NEED_RETRY` subrequest in place. Renegotiation mode decants contiguous retry spans, resets iterators, converts source to `NETFS_DOWNLOAD_FROM_SERVER`, calls `prepare_read()`, truncates iterators to negotiated lengths/segment limits, reissues, discards superfluous subrequests, or allocates extra subrequests when the retried span splits smaller than before. Abandon paths mark remaining retry/failed subrequests failed with `-ENOMEM`.

## State And Persistence
Mutates subrequest `source`, `start`, `len`, `transferred`, `retry_count`, flags, iterators, and stream `sreq_max_len/sreq_max_segs`. It does not persist data but determines whether final read data comes from cache or server.

## Dependencies And Integration Points
Called by `read_collect.c` when the front subrequest requests retry. Uses netfs ops `retry_request()`, `prepare_read()`, `issue_read()`, iterator limiting, and request waitqueues.

## Risks
Retry reconstruction can corrupt coverage if boundaries, donations, transferred offsets, or iterator counts are mishandled. Allocating extra subrequests can fail after partial rebuild. Cache failure fallback must avoid retry loops with no progress.

## Test Signals
Cache read failure fallback to download, partial read with progress, retry needing smaller `rsize`, boundary-preserving split, extra-subrequest allocation failure, and abandoned page unlock after unrecoverable failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_retry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_single.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_single.c

## Purpose
Supports synchronous reads of a single monolithic netfs object, such as an AFS directory blob. The object is fetched as one subrequest from cache or server, then optionally marked dirty for cache writeback if downloaded.

## Important APIs, Types, And Functions
Exports `netfs_single_mark_inode_dirty()` and `netfs_read_single()`. Internal helpers are `netfs_single_begin_cache_read()`, `netfs_single_cache_prepare_read()`, `netfs_single_read_cache()`, and `netfs_single_dispatch_read()`.

## Control Flow
`netfs_read_single()` allocates a `NETFS_READ_SINGLE` request, begins a cache read operation if possible, stores the caller iterator in the request buffer, dispatches exactly one subrequest, waits for read collection, drops the request, and returns bytes/error. Dispatch prepares the subrequest from cache resources; source is either cache read or server download. Cache reads call cache ops `read()`, while server reads call netfs `prepare_read()` and `issue_read()`. Completion in read collector marks downloaded cacheable single objects dirty.

## State And Persistence
The request covers offset zero and the full iterator count. `netfs_single_mark_inode_dirty()` may set inode dirty and pin the FS-Cache cookie using `I_PINNING_NETFS_WB`, unless `SINGLE_NO_UPLOAD` and no cache is enabled.

## Dependencies And Integration Points
Integrates with FS-Cache read resources, netfs `issue_read`, read collector, inode dirty/writeback handling, and the single-object writeback path.

## Risks
Only one subrequest is permitted; filesystems must support that semantic or retry logic must preserve it. Cache-only objects without caching enabled are not dirtied. Oversized buffers beyond EOF depend on lower layers/collector to zero unused space.

## Test Signals
Read single object from cache, cache miss download then dirty inode, no-cache path, `SINGLE_NO_UPLOAD`, iocb completion through collector, and failure from cache begin returning `-ENOMEM`/interrupt errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/read_single.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/rolling_buffer.c -->
# sources/distributed-fs/ceph-client/fs/netfs/rolling_buffer.c

## Purpose
Implements rolling folio_queue buffers shared by netfs read/write issuers and collectors. The design lets producer and consumer move independently while retaining at least one queue node as a stable placeholder.

## Important APIs, Types, And Functions
Exports `netfs_folioq_alloc()` and `netfs_folioq_free()`. Defines `rolling_buffer_init()`, `rolling_buffer_make_space()`, `rolling_buffer_load_from_ra()`, `rolling_buffer_append()`, `rolling_buffer_delete_spent()`, and `rolling_buffer_clear()`.

## Control Flow
Initialization allocates an empty queue, sets both head and tail, and creates a folio_queue iterator. Producers call make-space before appending or loading readahead folios. When a head queue fills, a new queue is allocated and linked with release ordering because the consumer may delete the old node immediately after `next` becomes visible. Consumers delete spent tail queues only when there is a following node; otherwise they return NULL and keep the placeholder. Clear walks all nodes and drops marked folios in batches.

## State And Persistence
State is transient in `struct rolling_buffer`: head, tail, iterator, next-head slot, and per-queue marks. Mark 1 means folio references are released on clear; mark 2 is used by abandoned read-page handling.

## Dependencies And Integration Points
Used by read readahead buffering, writeback/writethrough buffers, pgpriv2 copy-to-cache, object cleanup, and folio queue stats/tracing. Depends on `linux/rolling_buffer.h`, folio_queue helpers, and tracepoints.

## Risks
Producer/consumer races around queue linking/deletion are the main hazard. Iterator adjustment when head is full prevents pointing at a soon-freed node. Incorrect marks can leak folio refs or release pages still owned elsewhere.

## Test Signals
Readahead loading across multiple queue nodes, append/advance/delete under concurrent producer/collector timing, clear with marked and unmarked folios, and memory allocation failure in make-space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/rolling_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/stats.c -->
# sources/distributed-fs/ceph-client/fs/netfs/stats.c

## Purpose
Defines netfs statistic counters and renders netfs plus FS-Cache statistics through procfs.

## Important APIs, Types, And Functions
Exports `netfs_stats_show()`. Defines atomic counters for read origins, write origins, request/subrequest objects, downloads/cache reads/uploads/cache writes, retry requests/subrequests, writeback lock contention, folio queues, and assorted zero/short/write-stream events.

## Control Flow
No complex control flow. Runtime code increments/decrements counters through `netfs_stat()`/`netfs_stat_d()` in `internal.h`. `netfs_stats_show()` reads counters atomically, prints categorized lines, and then calls `fscache_stats_show()` so the same proc file includes FS-Cache diagnostics.

## State And Persistence
Counters are in-memory diagnostics and reset on module load. They are approximate under concurrency but atomic.

## Dependencies And Integration Points
Depends on seq_file and `internal.h`. Hooked into `/proc/fs/netfs/stats` from `main.c` when stats support is enabled. Many netfs read/write paths update these counters.

## Risks
Stats can become misleading if new code paths skip updates or decrement object counters incorrectly. The printed labels are terse, so mapping between labels and counters should remain documented in code or docs.

## Test Signals
Run representative read/write/cache/retry/writeback workloads and verify counter classes move. Object counters should return to zero after requests/subrequests/folio queues are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/write_collect.c -->
# sources/distributed-fs/ceph-client/fs/netfs/write_collect.c

## Purpose
Collects write subrequest completions across server-upload and cache-write streams, unlocks completed folios, retries short writes, records mapping errors, invalidates cache on cache-write failure, and completes iocbs.

## Important APIs, Types, And Functions
Exports `netfs_write_subrequest_terminated()`. Defines `netfs_folio_written_back()`, `netfs_write_collection()`, `netfs_write_collection_worker()`, `netfs_collect_write_results()`, and `netfs_writeback_unlock_folios()`.

## Control Flow
The collector scans each active stream front-to-back, stopping at in-progress subrequests. It advances each stream's collected/transferred point, records permanent failure, flags short writes for retry, removes consumed subrequests, and computes request `collected_to` as the minimum collected point across active streams. For writeback-like origins, folios are completed only up to that common point. If retry is needed, `netfs_retry_writes()` quiesces and rebuilds streams. Final completion waits for `ALL_QUEUED` and empty active streams, sets transferred bytes, invalidates cache on cache-stream failure if the netfs provides `invalidate_cache()`, clears `IN_PROGRESS`, completes iocbs, and clears subrequests.

## State And Persistence
Updates folio private/group/writeback state, request `collected_to`, `cleaned_to`, `transferred`, stream failure/error/transferred state, mapping writeback error, request flags, and group release counts. Persistent server/cache writes were already issued by stream providers; this file decides completion semantics.

## Dependencies And Integration Points
Used by writeback, writethrough, single-object writeback, pgpriv2 copy-to-cache, and cache/backend write callbacks. Integrates with retry code, folio queues, mapping error state, iocb completion, and netfs group refs.

## Risks
The two-stream minimum-collection rule is subtle. Completing folios before both active streams cover them can lose dirty data or cache writes. Cache failure is tolerated differently from server failure, so disconnected-mode behavior depends on netfs `invalidate_cache()` and policy outside this file.

## Test Signals
Test server-only, cache-only, dual-stream writeback, cache-stream failure, server failure mapping error, partial write retry, writethrough iocb completion, group release, and pgpriv2 copy-to-cache folio unmarking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/write_collect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/write_issue.c -->
# sources/distributed-fs/ceph-client/fs/netfs/write_issue.c

## Purpose
Constructs and issues netfs write requests for writeback, writethrough, copy-to-cache, and single-object writeback. It overlays variable-sized folios with up to two parallel IO streams: upload to server and write to cache.

## Important APIs, Types, And Functions
Exports `netfs_prepare_write_failed()`, `netfs_writepages()`, and `netfs_writeback_single()`. Defines `netfs_create_write_req()`, `netfs_prepare_write()`, `netfs_reissue_write()`, `netfs_issue_write()`, `netfs_advance_write()`, `netfs_begin_writethrough()`, `netfs_advance_writethrough()`, and `netfs_end_writethrough()`.

## Control Flow
`netfs_create_write_req()` allocates a request, begins cache write resources if cacheable, initializes the rolling buffer, and configures stream 0 for server upload and stream 1 for cache write when available. `netfs_writepages()` serializes with `wb_lock`, obtains dirty folios with `writeback_iter()`, starts writeback, begins netfs writeback when a server-upload folio appears, and hands each folio to `netfs_write_folio()`. That function handles EOF truncation/zeroing, dirty groups, copy-to-cache sentinel groups, streaming dirty ranges, rolling buffer append, and alternating stream advancement by lowest submit offset. End issue flushes constructed subrequests and sets `ALL_QUEUED`.

## State And Persistence
Writes mutate server state via netfs `issue_write()` and cache state via FS-Cache ops. Request state includes rolling buffer, `issued_to`, `len`, stream availability/constructs, `wsize`, dirty group, and cache resources. Folios move through dirty/writeback/private/group states.

## Dependencies And Integration Points
Depends on netfs inode ops (`begin_writeback`, `prepare_write`, `issue_write`), FS-Cache write operations, write collector, retry code, folio queues, VM writeback, and writeback control.

## Risks
High-risk areas include EOF handling, partial streaming writes, dirty group mismatch/redirty, constructed subrequest flush boundaries, and cache/server stream divergence. Allocation failure after dirty folio acquisition calls `netfs_kill_dirty_pages()`, which is intentionally destructive to dirty folios in unrecoverable startup failure.

## Test Signals
Exercise contiguous and discontiguous writeback, Ceph-like dirty groups, copy-to-cache folios, EOF writes, mmap beyond EOF, writethrough partial pages, cache disabled/enabled, writeback lock contention, and negotiated `wsize` splitting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/write_issue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/write_retry.c -->
# sources/distributed-fs/ceph-client/fs/netfs/write_retry.c

## Purpose
Retries short or retry-requested write subrequests in each active stream, with support for renegotiating write sizes and splitting/merging retry spans.

## Important APIs, Types, And Functions
Defines `netfs_retry_writes()` and internal `netfs_retry_write_stream()`.

## Control Flow
`netfs_retry_writes()` sets `RETRYING`, waits for all active streams to quiesce, clears the flag, leaves TODO hooks for encrypted RMW handling, then retries streams marked `need_retry`. For a stream without `prepare_write`, it resets iterators and resubmits `NEED_RETRY` subrequests. With preparation, it finds contiguous retry spans, resets the source iterator, renegotiates `sreq_max_len/sreq_max_segs`, reuses existing subrequests when possible, discards extras if fewer are needed, or allocates inserted subrequests when more splits are required.

## State And Persistence
Mutates stream `need_retry`, subrequest `start`, `len`, `transferred`, `retry_count`, `NEED_RETRY`, `MADE_PROGRESS`, `BOUNDARY`, and iterators. Persistent write effects are retried through stream `issue_write()`.

## Dependencies And Integration Points
Called by `write_collect.c`. Depends on `netfs_wait_for_in_progress_stream()`, `netfs_reissue_write()`, `netfs_limit_iter()`, stream `prepare_write()`, netfs `retry_request()`, and request `wsize`.

## Risks
Retry span reconstruction must preserve coverage and boundaries while accounting for already-transferred bytes. Allocation failure for inserted subrequests is not explicitly handled in this file. Encryption TODOs indicate future complexity where server changes may require read-modify-write and cache rewrite.

## Test Signals
Short write retries, renegotiated smaller write sizes, no-prepare resubmission, boundary preservation, stream failure skip, dual-stream retry, and stress tests with concurrent collector wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/netfs/write_retry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/nfs/Kconfig

## Purpose
Defines kernel configuration options for the NFS client, supported protocol versions/features, pNFS layout modules, local caching, root-over-NFS, DNS behavior, debugging, UDP disabling, and NFSv4.2 READ_PLUS.

## Important APIs, Types, And Functions
This is Kconfig data, not C code. Important symbols include `NFS_FS`, `NFS_V2`, `NFS_V3`, `NFS_V3_ACL`, `NFS_V4`, `NFS_SWAP`, `NFS_V4_0`, `NFS_V4_2`, `PNFS_FILE_LAYOUT`, `PNFS_BLOCK`, `PNFS_FLEXFILE_LAYOUT`, `NFS_FSCACHE`, `ROOT_NFS`, `NFS_USE_LEGACY_DNS`, `NFS_USE_KERNEL_DNS`, `NFS_DEBUG`, `NFS_DISABLE_UDP_SUPPORT`, and `NFS_V4_2_READ_PLUS`.

## Control Flow
Kconfig dependencies and selects drive build inclusion. `NFS_FS` selects core RPC/lock/common support. Protocol version options depend on NFS core. pNFS layouts depend on NFSv4, with block layout also requiring device mapper. `NFS_FSCACHE` selects `NETFS_SUPPORT` and `FSCACHE`. Kernel DNS is default when NFSv4 is enabled and legacy DNS is not selected.

## State And Persistence
The file persists build-time choices in kernel config. It does not manage runtime state.

## Dependencies And Integration Points
Integrated by the kernel Kconfig system and consumed by NFS Makefiles and `#ifdef` code. It gates whether the netfs/FS-Cache files in this group can be used by NFS caching and whether blocklayout code is built.

## Risks
Incorrect dependencies cause link failures or unsupported runtime combinations. `NFS_DISABLE_UDP_SUPPORT` defaults on due to fragmentation/data corruption risk called out in help. `ROOT_NFS` requires built-in NFS and IP autoconfiguration.

## Test Signals
Build matrix across NFSv3/v4, pNFS layouts, `NFS_FSCACHE`, root NFS, legacy/kernel DNS, and debug/stat configurations. Verify `PNFS_BLOCK` is unavailable without `BLK_DEV_DM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/nfs/Makefile

## Purpose
Builds the Linux NFS client objects and conditionally includes version-specific, feature-specific, and pNFS layout subdirectories.

## Important APIs, Types, And Functions
Defines `obj-$(CONFIG_NFS_FS) += nfs.o`, `nfs-y` core objects, optional `nfsroot.o`, `sysctl.o`, `fscache.o`, and `localio.o`, version modules `nfsv2.o`, `nfsv3.o`, `nfsv4.o`, and pNFS subdirs `filelayout/`, `blocklayout/`, and `flexfilelayout/`. Adds include-path flags for trace sources.

## Control Flow
Kbuild composes objects according to Kconfig symbols. `nfsv4-y` includes core NFSv4 files and conditionally adds legacy DNS, sysctl, v4.0, and v4.2 files. pNFS layout directories are descended into only when their configs are enabled.

## State And Persistence
No runtime state. Build output composition is determined by `.config`.

## Dependencies And Integration Points
Consumes symbols from `fs/nfs/Kconfig`. Integrates the blocklayout Makefile researched in this group and includes NFS FS-Cache support when `CONFIG_NFS_FSCACHE` is enabled.

## Risks
Object list drift can omit source needed by a config or include incompatible code. Trace CFLAGS must keep generated trace headers resolvable. Optional localio/fscache objects require matching Kconfig definitions elsewhere.

## Test Signals
Compile NFS as built-in and module across v2/v3/v4, FSCACHE, ROOT_NFS, SYSCTL, v4.0/v4.2, and all pNFS layout combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/Makefile -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/Makefile

## Purpose
Kbuild fragment for the pNFS block layout driver module.

## Important APIs, Types, And Functions
Adds `blocklayoutdriver.o` when `CONFIG_PNFS_BLOCK` is enabled. The composite object is built from `blocklayout.o`, `dev.o`, `extent_tree.o`, and `rpc_pipefs.o`.

## Control Flow
Build-time only. The parent NFS Makefile descends into this directory under `CONFIG_PNFS_BLOCK`, and this Makefile builds the block layout driver pieces as one module/object.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on `PNFS_BLOCK` Kconfig, which itself depends on NFSv4 and device mapper support. The listed objects match the declarations in `blocklayout.h`: layout IO/registration, device resolution/registration, extent tree management, and rpc_pipefs communication.

## Risks
Missing any of the component objects breaks symbols used by `blocklayout.c`. Adding new blocklayout helpers requires updating this composite list.

## Test Signals
Build with `CONFIG_PNFS_BLOCK=y` and `m`, and verify module aliases for NFS layout types are present in the resulting object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.c -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.c

## Purpose
Implements the NFSv4.1 pNFS block and SCSI layout driver. It translates pNFS block extents into block-device BIOs, handles parallel BIO completion, decodes/validates layout segments, manages extent returns/commits, enforces alignment for pageio coalescing, and registers layoutdriver types.

## Important APIs, Types, And Functions
Key layoutdriver callbacks are `bl_read_pagelist()`, `bl_write_pagelist()`, `bl_alloc_layout_hdr()`, `sl_alloc_layout_hdr()`, `bl_free_layout_hdr()`, `bl_alloc_lseg()`, `bl_free_lseg()`, `bl_return_range()`, `bl_prepare_layoutcommit()`, `bl_cleanup_layoutcommit()`, `bl_set_layoutdriver()`, and pageio ops. Internal helpers include `do_add_page_to_bio()`, `bl_submit_bio()`, `bl_mark_devices_unavailable()`, `verify_extent()`, `decode_sector_number()`, `bl_find_get_deviceid()`, and `is_aligned_req()`.

## Control Flow
Read/write pagelist paths allocate a `parallel_io`, start a blk plug, walk pages and pNFS extents, map file sectors through extent volume offsets and device maps, build/submit BIOs, and complete through end_io callbacks. Read holes are zero-filled without device IO. BIO errors set `pnfs_error`, mark layout failure, and mark deviceids unavailable. Last BIO completion schedules cleanup work, which calls `pnfs_ld_read_done()` or `pnfs_ld_write_done()`. Write cleanup marks sectors written in the extent tree and extends layoutcommit state. Layout segment allocation decodes XDR extents into a temporary list, validates spec ordering/coverage, resolves and registers deviceids, inserts extents into rb trees, or cleans up on error.

## State And Persistence
Runtime state includes `pnfs_block_layout` extent rb trees, `bl_lwb`, deviceid cache entries, block device maps, BIOs, and NFS pageio headers. Persistent effects are direct block device reads/writes and layoutcommit metadata marking written sectors.

## Dependencies And Integration Points
Integrates with NFS pNFS core, block layer BIO API, device mapper-backed device discovery, rpc_pipefs device resolution, extent_tree helpers, NFS pageio, layoutcommit, and module layout aliases `nfs-layouttype4-3` and `nfs-layouttype4-5`.

## Risks
Risks are high because IO bypasses the MDS. Sector/page alignment, EOF full-page write behavior, device unavailability caching, extent validation, BIO length clipping, and cleanup work scheduling must be exact. Error fallback relies on marking layout failure so NFS can redo through the metadata server.

## Test Signals
Test aligned buffered and direct reads/writes, read holes, EOF writes, device map boundary splits, BIO failure fallback, unavailable device retry timeout, invalid layout extent decoding, layout return range removal, layoutcommit preparation/cleanup, and registration/unregistration of block and SCSI layout types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.h -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.h

## Purpose
Private header for the NFS pNFS block layout driver. It defines block-volume/device/extent/layout data structures, protocol limits, sector/page constants, rpc_pipefs message structures, and cross-file function declarations.

## Important APIs, Types, And Functions
Defines `struct pnfs_block_volume`, `struct pnfs_block_dev_map`, `struct pnfs_block_dev`, `struct pnfs_block_extent`, `struct pnfs_block_layout`, `struct bl_pipe_msg`, and `struct bl_msg_hdr`. Inline conversions are `BLK_LO2EXT()` and `BLK_LSEG2EXT()`. Declares device functions (`bl_register_dev()`, `bl_alloc_deviceid_node()`, `bl_free_deviceid_node()`), extent tree functions, and rpc_pipefs functions (`bl_resolve_deviceid()`, `bl_init_pipefs()`, `bl_cleanup_pipefs()`).

## Control Flow
No direct runtime flow, but the structures drive `blocklayout.c`, `dev.c`, `extent_tree.c`, and `rpc_pipefs.c`. Device maps provide a `map()` callback that translates logical offsets to block devices/ranges. Extents can live in rb trees or temporary lists through a union node/list member.

## State And Persistence
State represented includes hierarchical block volumes (simple, slice, concat, stripe, SCSI), block device file/device offsets, registration flags, persistent reservation key, extent file/volume offsets and state, layout read/write extent trees, SCSI-layout indicator, and last written byte.

## Dependencies And Integration Points
Includes device mapper, NFS FS, SUNRPC rpc_pipefs, NFSv4 internals, pNFS, and NFS network namespace headers. It is the contract among all blocklayout driver compilation units.

## Risks
Limits such as UUID/designator sizes and max devices protect allocation bounds; protocol changes must update these carefully. Sector units in extents differ from byte units in NFS arguments, so callers must convert consistently. Union use requires an extent to be in only one container at a time.

## Test Signals
Compile all blocklayout objects, decode device trees of each volume type, insert/remove/lookup extents in rw/ro trees, and validate SCSI/block layout registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.h -->
