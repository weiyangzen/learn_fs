# Group Research: group_1446_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_label_c_sources_c_25e6fa11a630

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_label.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_label.c

## Purpose
Implements OpenZFS vdev label management: physical label offsets, label config nvlist generation and reads, vdev label initialization, boot environment label storage, uberblock discovery/sync, and transactional config sync. The file defines the on-disk update choreography that keeps vdev labels and uberblocks consistent across crashes.

## Main Responsibilities
- Translate logical label numbers and offsets into physical disk offsets with `vdev_label_offset()` and reverse-map offsets with `vdev_label_number()`.
- Read and write label regions through physical ZIOs using label checksums.
- Generate vdev configuration nvlists, including topology, stats, allocation class, DTL/indirect-removal metadata, ZAP object ids, and action progress stats.
- Read the best usable label config at or below a target txg.
- Detect whether a candidate device is already in use by a pool, spare, or L2ARC device.
- Initialize labels for regular, spare, L2ARC, remove, replace, and split workflows.
- Read and write the label boot environment area in raw, nvlist, and FreeBSD bootonce-compatible forms.
- Scan all label uberblock rings to choose the best uberblock and associated config.
- Sync labels and uberblocks in a crash-consistent sequence.

## Key Entry Points
- `vdev_label_offset()`, `vdev_label_number()`: low-level label geometry helpers.
- `vdev_label_write()`: exported physical label writer; paired with local `vdev_label_read()`.
- `vdev_config_generate_stats()`: serializes vdev stats and extended queue/latency histograms.
- `vdev_config_generate()`: recursively emits a vdev subtree config nvlist.
- `vdev_top_config_generate()`: emits root top-level child count and hole array.
- `vdev_label_read_config()`: reads and selects a valid label config.
- `vdev_label_init()`: recursively initializes leaf labels and uberblock rings.
- `vdev_label_read_bootenv()`, `vdev_label_write_bootenv()`: manage label bootenv storage.
- `vdev_uberblock_compare()`, `vdev_uberblock_load()`: select import/load uberblock state.
- `vdev_uberblock_sync_list()`: writes uberblocks and flushes affected vdevs.
- `vdev_config_sync()`: top-level transactional sync for labels and uberblocks.

## Important Algorithms and Semantics
- Label placement keeps two labels at the start and two at the end of the device. `vdev_label_offset()` handles end-label relocation by subtracting total label size from physical size for labels in the second half.
- Label config selection favors the highest label txg not exceeding the requested txg. Auxiliary labels and partially initialized labels without usable txg are accepted as first-valid configs.
- Config sync is intentionally ordered:
  1. Flush data writes for the txg.
  2. Write and flush even labels.
  3. Write and flush uberblocks.
  4. Update MMP uberblock state if multihost is enabled.
  5. Write and flush odd labels.
  This preserves recovery paths if power fails before, during, or after the uberblock update.
- Uberblock comparison orders by txg, then timestamp, then valid MMP sequence. This handles duplicate txg writes from interrupted imports or multihost-aware writers.
- Uberblock load tracks both the best allowed uberblock and the latest observed uberblock. It rejects a rewind candidate if RAIDZ expansion reflow info differs from the latest uberblock.
- Expanded leaf vdevs may need end-label uberblock rings copied from label 0 because labels 2 and 3 moved.
- dRAID distributed spares are special-cased: label configs may be generated instead of read, and uberblocks/top-level configs are not written to them.

## Data and State
- Uses `vdev_phys_t` for packed config storage in `vp_nvlist`.
- Uses `vdev_label_t` regions: vdev phys area, bootenv padding area, and uberblock ring.
- Uses ABD buffers for all label I/O.
- Uses `spa_config_dirty_list` to decide which vdevs need label rewrites.
- Tracks successful writes with per-top-vdev `good_writes` counters so config sync can fail when no visible leaf accepted a label write.
- Auxiliary vdev state is handled through `spa_spares`, `spa_l2cache`, and `spa_aux_sync_uber`.

## Dependencies
Heavy integration with `spa`, `vdev`, `zio`, `nvlist`, `uberblock`, `metaslab`, scan/removal/checkpoint/rebuild stats, dRAID, ABD, and bootenv definitions. Correctness depends on spa config locks and ZIO flags such as `ZIO_FLAG_CONFIG_WRITER`, `ZIO_FLAG_CANFAIL`, `ZIO_FLAG_TRYHARD`, `ZIO_FLAG_SPECULATIVE`, and `ZIO_FLAG_IO_RETRY`.

## Edge Cases and Failure Handling
- Retries label reads/writes with `ZIO_FLAG_IO_RETRY` before declaring failure.
- Avoids consuming labels with txg greater than the selected uberblock txg.
- Records create-info metadata when refusing an already-in-use device.
- Preserves shared spare/L2ARC GUIDs when adding or replacing known auxiliary devices.
- Treats log and auxiliary label sync errors as ignorable in the per-vdev label-sync callback path.
- `nvlist_pack()` overflow is converted to `ENAMETOOLONG` during initial label writes.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_label.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_mirror.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_mirror.c

## Purpose
Implements mirror-like vdev behavior for `mirror`, `replacing`, and `spare` vdev types. It handles child opening/closing, read replica selection, mirrored writes, scrub/resilver/rebuild behavior, repair I/O, state transitions, and mirror-specific kstats/tunables.

## Main Responsibilities
- Maintain mirror selection statistics through `vdev_mirror_stat_init()` and `vdev_mirror_stat_fini()`.
- Build per-I/O `mirror_map_t` state describing candidate children or root-level DVAs.
- Choose the least costly readable child for normal reads using queue load, last offset, rotational status, DTL state, and dRAID constraints.
- Issue reads to all children during scrub when not resilvering, so copies can be verified or compared.
- Issue writes to all children, with special protection for speculative rebuild repair writes.
- Retry alternate children after read failure and trigger repair writes when good data is available.
- Provide shared `vdev_ops_t` implementations for mirror, replacing, and spare vdevs.

## Key Entry Points
- `vdev_mirror_stat_init()`, `vdev_mirror_stat_fini()`: install/delete mirror kstats.
- `vdev_mirror_open()`: opens children and computes aggregate size and ashift.
- `vdev_mirror_close()`: closes all children.
- `vdev_mirror_io_start()`: maps and dispatches read/write child I/O.
- `vdev_mirror_io_done()`: evaluates child results, retries reads, selects scrub data, and issues repair writes.
- `vdev_mirror_state_change()`: maps child fault/degrade counts to parent state.
- `vdev_mirror_rebuild_asize()`: caps rebuild I/O size.
- `vdev_mirror_ops`, `vdev_replacing_ops`, `vdev_spare_ops`: exported operation vectors.

## Important Algorithms and Semantics
- `vdev_mirror_load()` scores candidates from active queue length plus a seek/linear penalty. Rotating devices distinguish exact continuation, nearby offset, and seek; non-rotating devices still get a seek penalty to preserve aggregation benefits.
- Root-level reads over multiple DVAs are treated as mirror reads across top vdevs. During sorted scrub, only the first DVA is considered until retry, because other sorted I/Os will check their own DVA copies.
- Read-only pool loads validate DVAs and skip invalid ones, allowing import attempts with incomplete or untrusted configs.
- `vdev_mirror_child_select()` skips unreadable children, marks DTL-missing children as speculative `ESTALE`, prefers dRAID distributed spares when present, and randomizes among equally preferred children.
- Scrub reads issue to every readable child and use separate ABDs for all but one child. Without a block pointer, scrub compares raw data copies and returns `ECKSUM` on mismatch.
- Direct I/O read checksum errors stop alternate-copy retries and report suspicious buffer mutation risk through direct-I/O checksum reporting.
- Repair writes are issued after unexpected read errors, resilver reads, or resilvering scrub reads when at least one good copy exists.
- Speculative sequential rebuild repair writes are restricted to rebuilding children when another child’s data is not confirmed.

## Data and State
- `mirror_child_t` tracks child vdev, ABD, offset, error, load, tried/skipped/speculative flags, and rebuilding status.
- `mirror_map_t` tracks preferred child indexes, child count, resilvering/rebuilding/root flags, and an inline child array.
- The preferred index array is allocated immediately after the inline child array by `vdev_mirror_map_alloc()`.

## Dependencies
Uses `vdev_queue_length()` and `vdev_queue_last_offset()` from `vdev_queue.c` for load scoring, DTL routines for missing/partial data checks, dRAID helpers for readable/missing checks, ZIO child I/O APIs, ABD copy/compare APIs, scan state from `dsl_scan`, and vdev state helpers.

## Tunables and Kstats
- Tunables control rotational and non-rotational load penalties:
  `zfs_vdev_mirror_rotating_inc`,
  `zfs_vdev_mirror_rotating_seek_inc`,
  `zfs_vdev_mirror_rotating_seek_offset`,
  `zfs_vdev_mirror_non_rotating_inc`,
  `zfs_vdev_mirror_non_rotating_seek_inc`.
- Kstats count linear/offset/seek classifications and preferred-child selection outcomes.

## Edge Cases and Failure Handling
- A mirror with zero children fails open with `VDEV_AUX_BAD_LABEL`.
- If all children fail open, parent aux state distinguishes all-offline from no-replicas.
- Partial mirrored writes are treated as success when at least one child succeeds, except root-level ditto writes require all copies.
- If no good read copy exists and no child remains to try, the worst non-speculative error is propagated.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_mirror.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_missing.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_missing.c

## Purpose
Defines placeholder leaf vdev types used when a pool configuration refers to a device that is missing or a top-level hole. These are primarily import-time constructs that let the kernel parse and instantiate the rest of the vdev tree even though the pool should ultimately fail validation.

## Main Responsibilities
- Provide a minimal open routine for missing/hole vdevs.
- Reject all I/O with `ENOTSUP`.
- Export separate operation vectors for `missing` and `hole` vdev types.

## Key Entry Points
- `vdev_missing_open()`: pretends to open successfully with zero size and zero shifts.
- `vdev_missing_close()`: no-op close.
- `vdev_missing_io_start()`: sets `io_error` to `ENOTSUP` and executes the ZIO.
- `vdev_missing_io_done()`: no-op completion.
- `vdev_missing_ops`: leaf ops for `VDEV_TYPE_MISSING`.
- `vdev_hole_ops`: leaf ops for `VDEV_TYPE_HOLE`.

## Important Semantics
`vdev_missing_open()` deliberately returns success instead of failing. The comment explains this preserves the desired later failure mode: a GUID sum mismatch with `VDEV_AUX_BAD_GUID_SUM`, rather than prematurely faulting the root vdev as having no replicas.

## Data and State
The implementation stores no private state. All size and shift outputs from open are set to zero.

## Dependencies
Depends only on generic vdev ops, ZIO execution, and default size conversion helpers.

## Edge Cases and Failure Handling
All I/O is unsupported. These vdevs exist to keep config parsing and import diagnostics coherent, not to serve data.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_missing.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_queue.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_queue.c

## Purpose
Implements the per-leaf-vdev ZFS I/O scheduler. It queues, prioritizes, throttles, aggregates, dispatches, completes, and reprioritizes physical ZIOs across sync read/write, async read/write, scrub, removal, initializing, trim, and rebuild classes.

## Main Responsibilities
- Maintain per-priority FIFO or AVL queues and active counts.
- Enforce global per-vdev active I/O limits and per-class min/max active limits.
- Dynamically adjust async write concurrency based on dirty data and pending sync tasks.
- Throttle non-interactive I/O while interactive I/O is active using NIA credit/delay rules.
- Aggregate adjacent read/write I/Os into a delegated parent I/O using gang ABDs.
- Optionally bypass queueing for selected scheduler modes and non-rotating block devices.
- Provide queue length, last offset, class length, and pool-busy helpers used elsewhere.

## Key Entry Points
- `vdev_queue_init()`, `vdev_queue_fini()`: create/destroy per-class lists/trees, offset trees, active list, and lock.
- `vdev_queue_io()`: normalize priority, enqueue or bypass an I/O, and return the next dispatchable I/O.
- `vdev_queue_io_done()`: remove a completed active I/O and dispatch more queued work.
- `vdev_queue_change_io_priority()`: reprioritize queued or not-yet-queued I/O.
- `vdev_queue_pool_busy()`: reports whether dirty data has crossed the async write minimum threshold.
- `vdev_queue_length()`, `vdev_queue_last_offset()`, `vdev_queue_class_length()`: queue introspection helpers.

## Important Algorithms and Semantics
- FIFO classes are sync read, sync write, and trim. Other queueable classes use AVL ordering by coarse timestamp bucket and offset, preserving fairness while encouraging locality.
- `vdev_queue_class_to_issue()` first tries classes below their minimum active count using round-robin from the last priority, then tries classes below their maximum active count in priority order.
- `vdev_queue_max_async_writes()` linearly interpolates async write active limits between configured dirty-data percentages, and immediately uses the maximum when dirty data is high or sync tasks are pending.
- Scrub, removal, initializing, and rebuild are non-interactive. Their max concurrency is reduced while interactive I/O is active, and gradually expands only after enough non-interactive completions when the vdev is idle.
- `vdev_queue_aggregate()` merges sufficiently adjacent reads or writes with matching aggregation-inherited flags. Reads may bridge configured gaps; writes may include optional gap-closing I/Os. The aggregate uses a gang ABD to avoid data copies.
- Aggregated parent I/Os are marked `ZIO_FLAG_DONT_QUEUE`; child parent links are bypassed/executed so completion is coordinated through ZIO graph mechanics.
- `ZIO_FLAG_NODATA` I/Os are still queued because bypass code cannot handle some gang ABD and RAIDZ aggregation cases; if selected directly, they are bypassed and completed immediately.

## Data and State
- `vdev_queue_t` owns per-class queues, read/write offset AVL trees, an active list, active counts, last issued offset, NIA counters, and a mutex.
- `vq_cqueued` is a bitmask of non-empty classes.
- `vq_cactive[]` and `vq_active` track active I/Os.
- `vq_ia_active` tracks active interactive I/O.
- `vq_nia_credit` controls how many non-interactive I/Os may proceed around interactive load.
- `vq_last_offset` is used by both scheduler locality and mirror load scoring.

## Tunables
The file exposes module parameters for aggregation limits, read/write gap limits, total max active, dirty-data async-write thresholds, per-class min/max active counts, and NIA credit/delay. Defaults favor high sync read/write concurrency, bounded async writes, and conservative scrub/removal/initializing/rebuild concurrency.

## Dependencies
Uses ZIO, vdev internals, AVL/list primitives, DSL pool dirty data, metaslab/spa state, ABD gang buffers, and dRAID assertions. It provides load information consumed by `vdev_mirror.c`.

## Edge Cases and Failure Handling
- Queueing can be bypassed with `ZIO_FLAG_DONT_QUEUE`, explicit scheduler-off mode, or auto mode for non-rotating block devices.
- Priority normalization prevents read/write child I/Os from inheriting incompatible parent priorities.
- Aggregation refuses TRIM, disabled aggregation, zero aggregation limit, oversize spans, and dRAID distributed-spare queues.
- Locking is carefully managed around aggregate dispatch to avoid `vq_lock` and ZIO lock order inversions.
- Queue length and last offset accessors intentionally avoid locking for performance, accepting possible transient inaccuracy on 32-bit platforms.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_queue.c -->