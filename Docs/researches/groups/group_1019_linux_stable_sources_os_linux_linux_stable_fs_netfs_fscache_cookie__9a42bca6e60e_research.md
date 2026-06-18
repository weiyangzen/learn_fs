# Group Research: group_1019_linux_stable_sources_os_linux_linux_stable_fs_netfs_fscache_cookie__9a42bca6e60e

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_cookie.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_cookie.c

Implements FS-Cache data-object cookie lifecycle management for netfs users. It owns cookie allocation, key hashing, collision handling, use/unuse accounting, state transitions, invalidation, withdrawal, relinquishment, LRU expiry, and `/proc` cookie listing.

Key behavior:
- Maintains a hash table keyed by volume plus object key, with collision waiting when an older relinquished cookie is still dropping.
- Uses `n_active` for netfs use pins and `n_accesses` for active cache backend access pins.
- Cookie states include quiescent, looking up, creating, active, invalidating, failed, LRU discarding, withdrawing, relinquishing, and dropped.
- `__fscache_use_cookie()` starts lookup or marks local-write preparation; `__fscache_unuse_cookie()` updates aux/size and moves idle cached cookies to the LRU.
- Worker-driven state machine calls backend operations such as `lookup_cookie()`, `prepare_to_write()`, `invalidate_cookie()`, and `withdraw_cookie()`.
- LRU expiry sets `FSCACHE_COOKIE_DO_LRU_DISCARD` and withdraws backing storage if the cookie remains idle.
- Relinquish removes the cookie from the hash only after cached state has been withdrawn or immediately if never cached.
- Proc output exposes cookie id, volume id, refs, active/access counts, state, flags, key, and aux data.

Dependencies:
- Uses `fscache_volume.c` for volume references and access pins.
- Uses cache backend ops from `struct fscache_cache_ops`.
- Exports core FS-Cache cookie APIs to netfs/filesystem clients.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_cookie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_internal.h -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_internal.h

Tiny compatibility/internal wrapper for FS-Cache-specific formatting.

Key behavior:
- Includes the shared netfs internal header.
- Overrides `pr_fmt` to prefix messages with `FS-Cache:`.
- Contains no data structures or executable logic beyond preprocessing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_io.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_io.c

Implements cache data I/O entry points around FS-Cache cookies.

Key behavior:
- `fscache_begin_operation()` pins a cookie, waits through lookup/invalidation/creation states, and asks backend `begin_operation()` for operation resources.
- Read and write begin helpers select `FSCACHE_WANT_PARAMS`; write-to-cache uses `FSCACHE_WANT_WRITE`.
- `fscache_wait_for_operation()` waits until a cookie reaches an acceptable state and lazily begins a backend operation.
- `__fscache_write_to_cache()` builds an xarray iterator over pagecache data and dispatches backend cache writes with completion cleanup.
- Handles deprecated `PG_private_2` page-bit clearing for cache-copy completion.
- `__fscache_resize_cookie()` synchronously resizes backend cache objects under the caller’s inode serialization.

Important failure mode:
- If the cookie becomes not-live, dropped, or backend `begin_operation()` fails, the operation returns `-ENOBUFS` and unpins cookie access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_main.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_main.c

Initializes and tears down the FS-Cache subsystem embedded in netfs support.

Key behavior:
- Creates the global `fscache` workqueue.
- Initializes proc entries through `fscache_proc_init()`.
- Creates the `fscache_cookie_jar` slab cache.
- Exports FS-Cache tracepoints and `fscache_wq`.
- Provides an architecture-independent 32-bit hash function derived from `full_name_hash()` but stable for on-disk use.
- Teardown destroys the cookie slab, proc entries, LRU timer, and workqueue.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_proc.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_proc.c

Creates FS-Cache procfs visibility under the netfs proc tree.

Key behavior:
- Adds `/proc/fs/fscache` as a symlink to `netfs`.
- Creates `fs/netfs/caches`, `fs/netfs/volumes`, and `fs/netfs/cookies`.
- Cleanup removes the `fs/fscache` proc subtree.
- Depends on seq operations supplied by cache, volume, and cookie files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_stats.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_stats.c

Defines FS-Cache statistic counters and renders them through seq_file.

Key behavior:
- Tracks volumes, cookies, LRU events, acquisitions, invalidations, updates, relinquishes, resizes, I/O, no-space, culling, and DIO misfit counts.
- Exports selected counters used by cache backends or external code.
- `fscache_stats_show()` appends FS-Cache stats to the broader netfs stats output.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_volume.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_volume.c

Implements FS-Cache volume cookies, the parent objects under which data cookies live.

Key behavior:
- Allocates volume records tied to a named cache and volume key, with optional coherency data.
- Maintains a volume hash table and collision wait logic similar to data cookies.
- Uses `n_accesses` to pin volume/cache access while backend volume operations run.
- `fscache_create_volume()` schedules backend `acquire_volume()` work and can wait for completion.
- Relinquish records updated coherency data or invalidate intent, then drops the caller reference.
- Free path calls backend `free_volume()`, removes proc and hash links, decrements cache volume count, and drops cache reference.
- `fscache_withdraw_volume()` prevents new access by unpinning and waiting for active volume accesses to drain.
- Proc output lists volume refs, cookie counts, accesses, flags, cache name, and key.

Important interactions:
- Cookies hold volume references after successful hash insertion.
- Cookie lookup creates the backend volume on demand if needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/fscache_volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/netfs/internal.h

Shared internal declarations and inline helpers for netfs and FS-Cache implementation files.

Key contents:
- Includes netfs, FS-Cache, folio queue, seq_file, slab, and trace headers.
- Declares request/subrequest allocation, read collection, write collection, retry, rolling buffer, proc, stats, and FS-Cache functions.
- Provides proc add/remove helpers for active netfs I/O requests.
- Defines stats increment/decrement helpers that compile away when disabled.
- Provides cache/cookie/volume state accessors with acquire/release ordering.
- Provides netfs group refcount helpers for dirty folio grouping.
- Provides request/subrequest in-progress checks with memory barriers.
- Defines debug macros and assertion macros used across these files.

Architectural role:
- This is the glue header connecting buffered read/write, FS-Cache, request lifetime, stats, and tracing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/iterator.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/iterator.c

Provides iterator extraction and sizing helpers for netfs I/O.

Key behavior:
- `netfs_extract_user_iter()` pins/extracts user pages from ubuf/iovec iterators into a bvec iterator.
- Handles cleanup only for safe error cases; warns on impossible overrun/corruption situations.
- `netfs_limit_iter()` dispatches to iterator-specific limiters for bvec, kvec, xarray, and folio_queue iterators.
- Limiters cap a contiguous operation by both byte count and segment count.
- Xarray limiting walks folios under RCU and rejects value entries/hugetlb folios.
- Folio_queue limiting walks queue slots and chained queues.

Use:
- Read and write retry paths use this to renegotiate request sizes when a transport has max segment constraints.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/iterator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/locking.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/locking.c

Provides inode-level exclusion between buffered and direct I/O for netfs users.

Key behavior:
- Buffered read/write start functions take `i_rwsem` shared but first clear/block outstanding direct I/O when needed.
- Direct I/O start sets `NETFS_ICTX_ODIRECT`, unmaps/waits cached pages, then downgrades to shared locking.
- Buffered writers take write lock first, then downgrade after direct I/O is blocked.
- End helpers release the shared lock.
- Interruptible/killable locking paths return `-ERESTARTSYS` or lower-level wait errors.

Design:
- Multiple buffered operations may run concurrently once direct I/O is excluded.
- Multiple direct I/O operations may run concurrently once buffered I/O is excluded.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/main.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/main.c

Initializes the netfs support library module.

Key behavior:
- Defines module metadata and `netfs_debug` module parameter.
- Creates request and subrequest slab caches plus mempools.
- Creates `/proc/fs/netfs` and active request listing when procfs is enabled.
- Creates `/proc/fs/netfs/stats` when FS-Cache stats are enabled.
- Calls `fscache_init()` after netfs core allocation/proc setup.
- Teardown reverses FS-Cache, proc, mempool, and slab setup.
- Proc request listing reports request id, origin, refs, flags, error, and coverage.

Important exported state:
- `netfs_io_requests`, `netfs_proc_lock`, `netfs_request_pool`, and `netfs_subrequest_pool`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/misc.c

Miscellaneous netfs helpers for folio queues, dirty/writeback pinning, invalidation, release, waiting, and collector wakeups.

Key behavior:
- Allocates/free folio_queue-backed buffers and marked folios.
- `netfs_reset_iter()` rewinds/truncates a subrequest iterator to remaining bytes.
- `netfs_dirty_folio()` marks a folio dirty and pins the FS-Cache cookie for later writeback.
- `netfs_unpin_writeback()` and `netfs_clear_inode_writeback()` release writeback cookie pins.
- `netfs_invalidate_folio()` updates zero-point tracking and trims/removes netfs private folio metadata.
- `netfs_release_folio()` refuses dirty/busy folios, waits for deprecated private_2 when safe, and notes cache page release.
- Collector wait helpers support either workqueue-offloaded collection or in-caller collection.
- Pause wait helpers are used during retry coordination.

Concurrency notes:
- Uses request waitqueue and `NETFS_RREQ_IN_PROGRESS`, `NETFS_RREQ_PAUSE`, and subrequest in-progress flags.
- Wakes collection only when front subrequests complete or retrying requires reassessment.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/objects.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/objects.c

Handles netfs I/O request and subrequest object lifetime.

Key behavior:
- Allocates requests from filesystem-specific pools or global mempools.
- Initializes request origin, mapping, inode, size snapshot, streams, waitqueue, work item, and tracing id.
- Read origins use `netfs_read_collection_worker`; write origins use `netfs_write_collection_worker`.
- Requests start with two refs, including the in-progress/work lifecycle ref.
- Calls filesystem `init_request()` and `free_request()` hooks when present.
- Request free path cancels collection work, removes proc entry, clears subrequests, ends cache operation, unpins direct bvec pages, clears rolling buffer, and decrements inode I/O count.
- Subrequests are also mempool-backed, refcounted, linked to parent request, and traced.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/objects.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_collect.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/read_collect.c

Collects read subrequest results, unlocks folios, handles EOF/short reads, and triggers retries.

Key behavior:
- Processes only the front of the read stream, preserving ordered completion semantics.
- Clears unread tails on EOF or explicit clear-tail cases.
- For buffered reads, marks folios uptodate, restores/removes private metadata, optionally marks copy-to-cache, and unlocks folios once fully covered.
- Cache read failures become retryable; server download failures become permanent request failures.
- Short reads without EOF/clear-tail/retry progress become `-ENODATA`.
- Completion handles DIO/unbuffered read dcache flushing, kiocb completion, inode dirtying for single-object cache population, task I/O accounting, abandoned page unlocks, and deprecated pgpriv2 cache-copy finalization.
- Exports progress and termination callbacks used by filesystems/cache backends.

Important flags:
- Uses request pause/in-progress flags and subrequest failed/retry/progress/copy-to-cache flags to coordinate retry and collection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_collect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_pgpriv2.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/read_pgpriv2.c

Deprecated support for copying read folios to cache using `PG_private_2`.

Key behavior:
- Starts a secondary write request with origin `NETFS_PGPRIV2_COPY_TO_CACHE`.
- Marks read folios private_2 and appends them to the copy request rolling buffer.
- Splits a folio into one or more cache write subrequests using `netfs_advance_write()`.
- Flushes outstanding cache writes when the read request finishes.
- Clears private_2 marks as copy-to-cache writeback collection advances.

Status:
- Code comments explicitly mark this path deprecated; newer private folio metadata is preferred.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_pgpriv2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_retry.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/read_retry.c

Retries failed or short read subrequests.

Key behavior:
- Reissues simple retryable subrequests directly when no renegotiation is needed.
- Converts failed cache reads to server downloads.
- When prepare/read sizing is involved, rebuilds contiguous pending spans and repartitions them according to renegotiated size/segment limits.
- Allocates additional subrequests if a retried span needs more pieces; discards superfluous ones if fewer are needed.
- Marks remaining retryable/failed subrequests failed with `-ENOMEM` when allocation or preparation fails.
- `netfs_retry_reads()` waits for in-progress stream I/O to quiesce before modifying the list.
- `netfs_unlock_abandoned_read_pages()` unlocks any buffered folios left behind by abandoned subrequests.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_retry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_single.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/read_single.c

Implements synchronous single-blob reads for monolithic netfs objects such as AFS directories.

Key behavior:
- `netfs_single_mark_inode_dirty()` marks the inode dirty after server download if cached contents should be stored locally.
- Begins a cache read operation when possible; otherwise falls back to server download.
- Allows exactly one subrequest for the object, though that subrequest may later be retried.
- Dispatches either backend cache read or filesystem `issue_read()`.
- `netfs_read_single()` allocates a request, assigns caller iterator as the buffer, dispatches, waits synchronously, and drops the request.

Special case:
- If object is cache-only and caching is unavailable, dirty marking is skipped.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/read_single.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/rolling_buffer.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/rolling_buffer.c

Implements folio_queue-based rolling buffers shared by read/write issuers and collectors.

Key behavior:
- Allocates and frees traced `folio_queue` objects.
- Initializes rolling buffers with separate head/tail pointers and an `ITER_SOURCE` or destination folio_queue iterator.
- Adds new queue nodes when the head fills while keeping iterator state valid for producer/consumer independence.
- Loads readahead folios into the buffer and records folio order.
- Appends individual folios, optionally setting mark bits.
- Deletes spent queue nodes but keeps the final placeholder queue to avoid collapsing producer/consumer pointers.
- Clears buffers and releases marked folios in batches.

Use:
- Read collection consumes folios from tail while read issue fills head.
- Write issue appends folios while write collection releases them after all streams cover them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/rolling_buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/stats.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/stats.c

Defines and renders netfs support statistics.

Key behavior:
- Tracks read origins, read/cache/download outcomes, write origins, upload/cache-write outcomes, retry counts, active objects, folio queues, and writeback lock behavior.
- `netfs_stats_show()` prints netfs counters and then appends FS-Cache stats through `fscache_stats_show()`.
- Exported so proc setup and other code can render stats.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/write_collect.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/write_collect.c

Collects write subrequest results across parallel write streams.

Key behavior:
- Supports multiple streams, primarily server upload and local cache write.
- Advances each stream independently but advances request `collected_to` only to the minimum collected position across active streams.
- Unlocks/writeback-completes folios once all required streams have covered them.
- Handles streaming-write metadata, dirty group references, and copy-to-cache markers.
- Cache write failure can invalidate the cache without failing server writeback unless the filesystem policy says otherwise.
- Server upload failure records mapping errors.
- Short writes set retry-needed; permanent failures cancel affected stream progress.
- Completion updates kiocb position/completion for async write origins and clears subrequests.
- Termination callback records transferred bytes or errors, sets retry/failure flags, pauses request generation, and wakes collector.

Debug support:
- `netfs_dump_request()` prints request, stream, and subrequest state when writeback unlock finds impossible buffer state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/write_collect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/write_issue.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/write_issue.c

Issues high-level netfs writeback, writethrough, cache-copy, and single-object writes.

Key behavior:
- Creates write requests with upload stream 0 and cache stream 1.
- Begins FS-Cache write operation when cacheable and cache is enabled.
- `netfs_write_folio()` handles writeback of dirty folios, partial streaming writes, EOF zeroing, dirty groups, copy-to-cache-only folios, and discontinuities.
- Builds subrequests incrementally with `netfs_advance_write()`, splitting by max write size, max segments, discontiguity, or EOF.
- `netfs_writepages()` serializes on `ictx->wb_lock`, iterates VFS writeback folios, starts upload when first non-copy-to-cache folio appears, and offloads collection.
- Writethrough path holds writeback lock across pagecache population, then writes folios as page ends are reached.
- Single-object writeback writes an `ITER_FOLIOQ` payload, used for monolithic objects.
- On unrecoverable startup failure, dirty pages are killed by starting/ending writeback and dropping netfs private metadata.

Important design:
- Upload and cache writes are overlaid over the same rolling folio buffer but can produce different subrequest boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/write_issue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/write_retry.c -->
# File Research: sources/os/linux/linux-stable/fs/netfs/write_retry.c

Retries short or retryable write subrequests.

Key behavior:
- Waits for all active streams to quiesce before retry list surgery.
- Calls filesystem `retry_request()` for upload streams when available.
- Reissues directly when no prepare hook is needed.
- Otherwise rebuilds contiguous retry spans, calls stream `prepare_write()` to renegotiate limits, repartitions iterators, and reissues.
- Allocates extra subrequests if a span expands into more pieces; discards excess subrequests if fewer pieces are needed.
- Handles upload and cache streams independently.
- Contains TODO placeholders for future content-encryption read-modify-write retry handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/netfs/write_retry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/nfs/Kconfig

Defines Linux NFS client configuration options.

Key options:
- `NFS_FS` enables core NFS client support and selects CRC32, LOCKD, SUNRPC, NFS_COMMON, and conditional ACL support.
- Version options cover NFSv2, NFSv3, NFSv3 ACLs, NFSv4, NFSv4.0, and NFSv4.2.
- pNFS layout modules include file, block, and flexfile layouts; `PNFS_BLOCK` depends on `NFS_V4 && BLK_DEV_DM`.
- `NFS_FSCACHE` selects `NETFS_SUPPORT` and `FSCACHE`, connecting NFS to the netfs/FS-Cache files in this group.
- Other options include swap over NFS, root over NFS, DNS resolver choice, debug, UDP disable default, migration, security labels, and READ_PLUS.

Research relevance:
- This file controls whether netfs caching and pNFS block layout code in this group is built.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nfs/Makefile

Build rules for the Linux NFS client.

Key behavior:
- Builds `nfs.o` from core client, directory, inode, superblock, I/O, read/write, mount, namespace, tracing, context, and export sources.
- Adds optional objects for root NFS, sysctl, FS-Cache integration, and local I/O.
- Builds version-specific modules: `nfsv2.o`, `nfsv3.o`, and `nfsv4.o`.
- Adds NFSv4 optional components for legacy DNS, sysctl, v4.0, and v4.2.
- Descends into pNFS layout directories based on config: filelayout, blocklayout, flexfilelayout.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/Makefile

Build rules for the pNFS block layout driver.

Key behavior:
- Builds `blocklayoutdriver.o` when `CONFIG_PNFS_BLOCK` is enabled.
- Driver objects are `blocklayout.o`, `dev.o`, `extent_tree.o`, and `rpc_pipefs.o`.
- The file in this group, `blocklayout.c`, depends on device resolution, extent tree, and pipefs support from the sibling objects.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.c

Implements the NFSv4.1 pNFS block and SCSI layout driver core.

Key behavior:
- Registers two layout drivers: `LAYOUT_BLOCK_VOLUME` and `LAYOUT_SCSI`.
- Translates NFS layout extents into block-device BIO reads/writes.
- `parallel_io` tracks multiple bios for one NFS page I/O header and calls the pNFS completion callback only after the final bio completes.
- Read path looks up extents, submits bios for data extents, zero-fills holes, updates EOF/count, and falls back through pNFS error handling on failures.
- Write path writes whole pages, marks extents written for layoutcommit, and reports `NFS_FILE_SYNC`.
- BIO errors mark layout segment failure and mark affected deviceids unavailable.
- Layout segment allocation decodes XDR extents, resolves/registers deviceids, verifies extent ordering/COW constraints, then inserts extents into the layout extent tree.
- Layout return removes affected extents from read/write trees.
- Pageio ops enforce sector/page alignment and reset to MDS I/O when block layout cannot handle a request.
- `set_layoutdriver()` rejects missing or page-larger server block sizes.
- Module init initializes pipefs support and registers block then SCSI drivers; exit unregisters both and cleans pipefs.

Important constraints:
- Reads require sector alignment for direct I/O.
- Writes require page alignment, except EOF direct writes can write full zero-padded pages per RFC behavior.
- Extent verification rejects invalid read/write/COW coverage combinations before extents become active.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.h

Defines pNFS block layout driver data structures and cross-file interfaces.

Key contents:
- Constants for page sectors, sector size, max UUIDs/devices, and UUID length cap.
- `pnfs_block_volume` describes simple, slice, concat, stripe, and SCSI volume forms.
- `pnfs_block_dev_map` maps logical offsets to block devices and disk offsets.
- `pnfs_block_dev` embeds an NFS deviceid node and describes composed block devices, children, chunking, opened bdev file, flags, SCSI reservation key, and map callback.
- `pnfs_block_extent` records file-sector to volume-sector mappings, state, device, length, and commit tag.
- `pnfs_block_layout` owns read/write extent rbtrees, extent lock, SCSI-layout flag, and last-written byte.
- Inline helpers convert layout headers/segments to `pnfs_block_layout`.
- Declares device management, extent tree, layoutcommit, and rpc_pipefs interfaces implemented by sibling files.

Research relevance:
- This header explains the structures consumed by `blocklayout.c` for BIO mapping, extent lookup, and layoutcommit tracking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.h -->