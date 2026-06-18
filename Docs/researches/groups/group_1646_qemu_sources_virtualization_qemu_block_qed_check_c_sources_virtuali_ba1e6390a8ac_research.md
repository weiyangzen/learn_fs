# Group Research: group_1646_qemu_sources_virtualization_qemu_block_qed_check_c_sources_virtuali_ba1e6390a8ac

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/qemu`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qed-check.c -->
# File Research: sources/virtualization/qemu/block/qed-check.c

Implements QED image consistency checking and optional repair. It builds a bitmap of referenced clusters, walks the L1 table and every reachable L2 table, validates table/data cluster offsets, detects duplicate references as corruptions, and records allocation/fragmentation statistics in `BdrvCheckResult`.

`qed_check_l1_table()` marks the L1 table clusters, validates L2 table offsets, reads each L2 table, delegates data-cluster validation to `qed_check_l2_table()`, and writes repaired L1/L2 entries when `fix` is true. Invalid offsets are cleared to unallocated entries during repair. `qed_check_for_leaks()` scans file clusters after the header for unreferenced clusters, but only after a complete successful metadata walk.

`qed_check_mark_clean()` clears `QED_F_NEED_CHECK` only if there are no remaining corruptions or check errors, flushing first so repaired metadata reaches storage before the image is marked clean. Public `qed_check()` must run with `table_lock` held and coordinates bitmap allocation, accounting, L1 traversal, leak detection, repair cleanup, and freeing temporary state.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qed-check.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qed-cluster.c -->
# File Research: sources/virtualization/qemu/block/qed-cluster.c

Implements logical-to-file cluster lookup for QED. `qed_count_contiguous_clusters()` scans an L2 table from a given index and counts a contiguous run of entries, treating allocated clusters, unallocated markers, and zero-cluster markers as distinct run types.

`qed_find_cluster()` limits a request to a single L2-table boundary, looks up the L1 entry, validates the L2 table offset, reads or reuses the L2 table through the cache, then determines whether the requested range maps to allocated data, zero clusters, missing L2 entries, or missing L1 entries. It returns `QED_CLUSTER_FOUND`, `QED_CLUSTER_ZERO`, `QED_CLUSTER_L2`, `QED_CLUSTER_L1`, or a negative error.

The function also shortens `*len` to the contiguous run and stores the raw table offset/marker in `*img_offset`. It transfers an L2 cache reference into `request->l2_table`, replacing any previous reference, so callers can reuse the table for subsequent write allocation/update work.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qed-cluster.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qed-l2-cache.c -->
# File Research: sources/virtualization/qemu/block/qed-l2-cache.c

Implements QED's in-memory L2 table cache. The cache is a QTAILQ of `CachedL2Table` entries with reference counts, intended to avoid repeated image reads for recently used L2 tables while allowing in-flight requests to keep evicted tables alive.

`qed_alloc_l2_cache_entry()` creates an uninitialized refcounted entry. `qed_unref_l2_cache_entry()` drops a reference and frees the table with `qemu_vfree()` when the count reaches zero. `qed_find_l2_cache_entry()` searches by table file offset and increments the refcount on hits.

`qed_commit_l2_cache_entry()` inserts a freshly loaded or allocated L2 table after it is valid on disk and referenced by L1. If another request already committed the same offset, the new entry is discarded. The cache target is 50 entries; unused entries are evicted when possible, but the cache may temporarily grow if all entries are still referenced by active requests.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qed-l2-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qed-table.c -->
# File Research: sources/virtualization/qemu/block/qed-table.c

Provides QED L1/L2 table I/O. `qed_read_table()` reads a table from the image file, temporarily releases `table_lock` around block I/O, and converts little-endian disk offsets to CPU endianness. `qed_write_table()` writes a sector-aligned slice of a table, byte-swapping entries into an aligned temporary buffer and optionally flushing after the write.

The L1 wrappers read and write the fixed table at `header.l1_table_offset`. The L2 read path first drops any existing request cache reference, checks the L2 cache, allocates and reads a table on miss, commits it into the cache, and reacquires the canonical cached entry. On read failure, the untrusted loaded table is discarded.

The L2 write wrapper writes through to the image at the cached table's offset, either for a partial updated slice or a whole newly allocated L2 table. The `_sync` variants are thin wrappers around the coroutine implementations.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qed-table.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qed.c -->
# File Research: sources/virtualization/qemu/block/qed.c

Implements the QED block format driver. It handles probing, header endian conversion, header updates, option validation, open, create, close, reopen, length/info queries, block status, read/write I/O, write-zeroes, grow-only truncate, backing-file changes, cache invalidation, consistency checking, AioContext timer management, and final `BlockDriver` registration.

Open reads and validates the QED header, feature bits, cluster/table sizes, logical image size, L1 offset, file size, and optional backing filename/format flag. It initializes table geometry (`table_nelems`, `l1_shift`, `l2_shift`, `l2_mask`), loads the L1 table, initializes the L2 cache, repairs unclean images when writable and not opened for check, and starts the delayed `QED_F_NEED_CHECK` cleanup timer when needed.

The write path is built around `QEDAIOCB`. `qed_aio_next_io()` iterates cluster runs from `qed_find_cluster()`. Reads return zero clusters, backing data, or file data. In-place writes update existing clusters directly. Allocating writes are serialized through `allocating_acb` and `allocating_write_reqs`, allocate data clusters or zero markers, set `QED_F_NEED_CHECK` when required, perform copy-on-write prefill from backing for untouched cluster regions, write data, then update L2 and possibly L1 metadata.

Crash-consistency logic centers on `QED_F_NEED_CHECK`. Allocating writes without a backing file mark the image dirty before metadata updates; a virtual-clock timer later plugs new allocating writes, flushes data, clears the bit, writes the header, and flushes again. With a backing file, subcluster COW writes flush data clusters before L2 updates to avoid losing inherited backing data after a crash.

Creation supports QAPI and legacy create options, validates cluster/table/image sizes, creates a file child, writes the header and optional backing filename, and initializes the L1 table. Runtime metadata helpers expose block status from QED allocation maps, report dirty status through `BlockDriverInfo`, grow image size by rewriting the header, rewrite backing-file fields within existing header space, and route `.bdrv_co_check` to `qed_check()` under `table_lock`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qed.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qed.h -->
# File Research: sources/virtualization/qemu/block/qed.h

Defines the QED on-disk format constants, feature bits, header layout, metadata table structures, L2 cache structures, request state, AIO request state, and private driver state. The comments describe QED as a two-level cluster allocation table: a fixed L1 table points to on-demand L2 tables, which point to data clusters.

Key format constants include default/min/max cluster size, min/max/default table size, `QED_F_BACKING_FILE`, `QED_F_NEED_CHECK`, `QED_F_BACKING_FORMAT_NO_PROBE`, and supported feature masks. `QEDHeader` is packed and stored little-endian on disk. QED table entries use `0` for unallocated clusters and `1` for zero clusters.

`BDRVQEDState` owns the block node, CPU-endian header, `table_lock`, L1 table, L2 cache, table geometry, tracked file size, serialized allocating-write state, and delayed need-check timer. Inline helpers compute cluster starts, cluster offsets, table indexes, table/data offset validity, alignment, and special cluster markers. The header also declares all shared QED routines implemented across `qed.c`, `qed-table.c`, `qed-cluster.c`, `qed-l2-cache.c`, and `qed-check.c`.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qed.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/quorum.c -->
# File Research: sources/virtualization/qemu/block/quorum.c

Implements the `quorum` block filter, which presents multiple children as one device and requires a configured vote threshold for reads/writes. It supports normal quorum reads, FIFO reads, blkverify-like two-child comparison mode, optional rewrite of corrupted replicas after a successful read vote, dynamic child add/remove, and QAPI event reporting for bad children or quorum failure.

Reads in quorum mode allocate per-child aligned buffers, launch child read coroutines, collect successes/errors, compare successful data, and either copy the unanimous buffer or compute SHA-256 vote groups to select the winning version. Failed children and losing data versions are reported with `QUORUM_REPORT_BAD`; inability to reach the threshold emits `QUORUM_FAILURE`. If `rewrite-corrupted` is enabled, losing replicas are asynchronously rewritten with the winning data.

Writes and write-zeroes are mirrored to all children. The operation succeeds only if at least `threshold` children complete successfully; otherwise the most common error code is returned. Flush similarly votes over child flush results. `quorum_co_getlength()` requires all children to report the same length.

Open parses `children[]`, `vote-threshold`, `blkverify`, `rewrite-corrupted`, and `read-pattern`. It validates threshold bounds, restricts blkverify to exactly two children with threshold two, opens children as data children, and computes supported zero flags as the intersection of child capabilities. Child permissions request writes only when corrupted-rewrite is enabled and avoid sharing write/resize in ways that could let children diverge. Block status reports zero only when all children report zero for the region.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/quorum.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/raw-format.c -->
# File Research: sources/virtualization/qemu/block/raw-format.c

Implements QEMU's `raw` format driver as a thin pass-through layer over a file child, with optional `offset` and fixed `size` bounds. Without offset/size it behaves like a filter; with either option it is a bounded data node whose logical offsets are translated into the containing file.

`raw_apply_options()` validates that the offset lies within the child size, that optional size fits and is sector-aligned, and records the effective virtual size. `raw_adjust_offset()` enforces bounds for reads/writes and adds the configured base offset. Read, write, write-zeroes, discard, block status, copy-range, truncate, getlength, get-info, ioctl, eject, lock-medium, zoned operations, zero-init, and cancel-in-flight mostly forward to the child after this translation.

A key safety feature handles probed raw images. If QEMU guessed raw format, writes to block 0 are restricted: the first 512 bytes are copied to an aligned buffer, reprobed, and rejected with `-EPERM` if they would make another format driver match. This prevents a guest from creating a format header that later changes interpretation of the image. Probed raw images also get 512-byte request alignment.

The driver supports mutable `offset` and `size` reopen options, raw image creation by creating the underlying file, measuring raw size, passing through block size/geometry probing where safe, and permission adjustment that avoids requesting child WRITE/RESIZE unless the parent actually needs them.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/raw-format.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/rbd.c -->
# File Research: sources/virtualization/qemu/block/rbd.c

Implements the Ceph RADOS Block Device protocol driver. It parses legacy `rbd:pool/image[@snap][:key=value...]` filenames and modern QAPI options, connects to a RADOS cluster, opens an RBD image or snapshot, performs asynchronous I/O through librbd, supports image creation/truncation/discard/flush/write-zeroes where available, exposes snapshots, reports allocation status through fast-diff when possible, and registers as protocol `rbd`.

Connection setup handles monitor hosts, pool, namespace, image, snapshot, user, conf file, auth modes, key secrets, and legacy key/value pairs. Snapshot opens are forced read-only. The driver tracks image name, snapshot name, namespace, image size, object size, and probed/loaded encryption format in `BDRVRBDState`.

Optional librbd encryption support converts QAPI LUKS/LUKS2 options into librbd encryption format/load structures, including layered encryption through `rbd_encryption_load2` when available. If encryption is not requested, the driver probes the first bytes of the image for RBD/LUKS header markers so image-specific info can report likely encryption format.

`qemu_rbd_start_co()` bridges librbd async completions into QEMU coroutines: it creates a completion object, issues the selected read/write/discard/flush/write-zeroes operation, yields, and is woken by a bottom half scheduled from the librbd callback thread. Writes that extend beyond the tracked image size resize first. Short reads are zero-padded.

Block status defaults to allocated data but, when fast-diff is supported and valid, uses `rbd_diff_iterate2()` to distinguish allocated data from holes/zero regions. Older librbd versions get workarounds for non-object-aligned offsets, striping, and cloned images. Snapshot APIs create, delete, roll back, and list RBD snapshots, using the snapshot name as QEMU's snapshot ID.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/rbd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/replication.c -->
# File Research: sources/virtualization/qemu/block/replication.c

Implements the `replication` block filter used by block replication/failover flows. It has primary and secondary modes and tracks stages: none, running, failover, failover failed, and done. The filter registers `ReplicationOps` callbacks for start, checkpoint, get-error, and stop.

Primary mode is minimal: it is used to forward write requests and records errors while returning success to the caller. Secondary mode expects a three-layer chain: active disk, hidden disk, and secondary disk. On start it validates backing topology and equal lengths, ensures active/hidden disks can be emptied, temporarily reopens hidden/secondary writable, attaches them as children, blocks operations on a configured top node, and starts an internal backup job from secondary to hidden.

Checkpoints on the secondary call `backup_do_checkpoint()`, then empty both active and hidden disks. Reads are only allowed on secondary; writes either go to the active disk during normal running or, after failed failover, split writes between already allocated active/hidden regions and the secondary base to preserve consistency.

Stopping secondary replication cancels the backup job, optionally checkpoints for non-failover stop, or starts an active commit from the active disk into the secondary disk during failover. `replication_done()` marks success, detaches hidden/secondary children, and clears error state; failure moves to `BLOCK_REPLICATION_FAILOVER_FAILED`. Close cancels active jobs and unregisters replication state.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/replication.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/reqlist.c -->
# File Research: sources/virtualization/qemu/block/reqlist.c

Implements a small coroutine request-overlap list helper. `reqlist_init_req()` initializes a `BlockReq` with offset/byte range, creates its wait queue, and inserts it into a `BlockReqList`.

`reqlist_find_conflict()` scans the list for the first request whose byte range overlaps a requested range using `ranges_overlap()`. `reqlist_wait_one()` waits on the conflicting request's queue while holding a provided `CoMutex`; `reqlist_wait_all()` repeats until no overlapping request remains.

`reqlist_shrink_req()` reduces an active request's byte range and wakes all waiters so conflicts can be re-evaluated. `reqlist_remove_req()` removes the request and wakes all waiters. The helper is intended for block filters that need simple in-flight range exclusion.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/reqlist.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/snapshot-access.c -->
# File Research: sources/virtualization/qemu/block/snapshot-access.c

Implements the `snapshot-access` block driver, a read-oriented wrapper exposing a child's snapshot-access APIs. It opens a primary data child named `file`, mirrors its total sectors, refreshes its filename from the child, and registers as format `snapshot-access`.

Reads call `bdrv_co_preadv_snapshot()` and reject nonzero request flags with `-ENOTSUP`. Block status delegates to `bdrv_co_snapshot_block_status()`, and discard delegates to `bdrv_co_pdiscard_snapshot()`. Writes and write-zeroes are unsupported.

The child permission function requests no permissions and shares all permissions, relying on the child providing snapshot-access operations rather than normal write/read ownership. This makes the node a narrow adapter for accessing snapshot state rather than a general-purpose block filter.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/snapshot-access.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/snapshot.c -->
# File Research: sources/virtualization/qemu/block/snapshot.c

Provides block-layer internal snapshot management helpers. It defines snapshot option descriptors, lookup helpers by name or by ID/name, and generic wrappers for create, goto, delete, list, temporary load, and grouped all-device snapshot operations.

For drivers without native snapshot callbacks, the code can fall back to a primary child only when it is safe: the node must have a primary child and no other data/metadata/filtered children that would also need snapshotting. Fallback snapshot goto is more involved: it references the fallback child, closes the parent, detaches the child, applies the snapshot to the child, clears parent opaque state, reopens the parent with options forcing the same child node, and then unreferences the child.

`bdrv_can_snapshot()`, `bdrv_snapshot_create()`, `bdrv_snapshot_delete()`, `bdrv_snapshot_list()`, and `bdrv_snapshot_goto()` all prefer driver callbacks and otherwise use the safe fallback path. Snapshot goto rejects active dirty bitmaps. Temporary snapshot load requires a read-only device and a driver-provided `bdrv_snapshot_load_tmp`.

The all-device helpers collect either explicit node names or all BDS nodes, include writable inserted nodes that are in use by a `BlockBackend` or monitor-owned root nodes, and then check/create/delete/goto snapshots across that set. Delete drains all devices while operating. VM state snapshot selection finds either a named node or the first snapshot-capable included node.

<!-- END FILE RESEARCH: sources/virtualization/qemu/block/snapshot.c -->