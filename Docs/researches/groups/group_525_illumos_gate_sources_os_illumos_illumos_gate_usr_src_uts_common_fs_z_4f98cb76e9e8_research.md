# Group Research: group_525_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_4f98cb76e9e8

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_checkpoint.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_checkpoint.c

This file implements ZFS storage pool checkpoints: creating a pool-wide rewind point, reporting checkpoint state, and discarding checkpointed space asynchronously.

Key behavior:
- A checkpoint is represented by `DMU_POOL_ZPOOL_CHECKPOINT` in the MOS, containing a checkpointed uberblock, plus active `SPA_FEATURE_POOL_CHECKPOINT` state.
- Checkpointed frees are preserved in top-level vdev checkpoint space maps rather than returned to metaslab allocatable space, preventing reuse of blocks needed for rewind.
- `spa_checkpoint_get_stats()` reports whether the checkpoint exists or is being discarded, plus checkpoint space and timestamp.
- `spa_checkpoint()` opens the pool, waits for the current TXG to sync, then uses `dsl_early_sync_task()` so `spa_checkpoint_sync()` runs before ordinary frees in the next TXG.
- `spa_checkpoint_check()` rejects unsupported pools, too-large vdev space map addressing, active vdev removal, an existing checkpoint, or an in-progress discard.
- `spa_checkpoint_sync()` stores `spa_ubsync` as the checkpoint uberblock, sets `spa_checkpoint_txg`, records timestamp, adds the MOS ZAP entry, increments the feature refcount, and logs history.
- `spa_checkpoint_discard()` starts discard with an early synctask that removes the MOS checkpoint entry, clears `spa_checkpoint_txg`, wakes the discard thread, and logs the start.
- `spa_checkpoint_discard_thread()` walks top-level vdev checkpoint space maps, prefetches bounded chunks, and schedules syncing work to transfer checkpointed frees into metaslab freeing trees.
- `spa_checkpoint_discard_thread_sync()` destroys checkpoint space-map entries incrementally, updates `sci_dspace` and per-vdev checkpoint accounting, and frees/removes empty checkpoint space maps.
- `spa_checkpoint_discard_complete_sync()` clears the timestamp, decrements the feature refcount, wakes waiters, and logs completion after all vdev checkpoint maps are gone.

Important invariants:
- Checkpoint create and discard both use early synctasks to avoid races with frees entering checkpoint data structures.
- Discard iteration works backward through space maps and is bounded by `zfs_spa_discard_memory_limit`.
- Checkpoint accounting is verified in debug builds by comparing per-vdev checkpoint space, checkpoint space maps, and `spa_checkpoint_info.sci_dspace`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_config.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_config.c

This file manages cached pool configuration nvlists: loading cache files into the SPA namespace, writing cache files atomically, exposing all configs to zones, generating config nvlists, and syncing config changes.

Key behavior:
- `spa_config_load()` reads `spa_config_path` (`ZPOOL_CACHE` by default), unpacks an nvlist, and calls `spa_add()` for pools not already present in the namespace.
- `spa_config_write()` packs an nvlist and writes it via temp file, fsync, and rename; if passed `NULL`, it removes the cachefile.
- `spa_write_cachefile()` requires `spa_namespace_lock`, walks each cachefile path associated with the target pool, builds an nvlist of writeable pools using that cachefile, writes it, handles write failures with ereports and async retry, prunes old cachefile list entries, bumps `spa_config_generation`, and can post config sysevents.
- Readonly pools are intentionally skipped from cachefile writes because they may not be importable on reboot.
- Temporary-name imports use the previous pool name stored in `ZPOOL_CONFIG_POOL_NAME` rather than `spa_name()`.
- `spa_all_configs()` supports local-zone visibility by returning configs only for pools visible in the zone and only when `spa_config_generation` changed.
- `spa_config_set()` replaces the in-core `spa_config` under `spa_props_lock`.
- `spa_config_generate()` builds a pool or top-vdev config nvlist from in-core state, including version, name, state, txg, GUIDs, host identity, comments, top GUIDs, spare/log flags, per-vdev ZAP support, split metadata, vdev tree, read-required features, and optional DDT stats.
- `spa_config_update()` dirties labels or expands pending top-level vdevs, waits for the MOS config to sync, updates the global cachefile unless this is a root pool, and cascades pool updates into vdev updates.

Important invariants:
- Cachefile writes happen after MOS config sync, leaving a crash window where explicit import may be needed.
- `spa_config_generate()` takes `SCL_CONFIG | SCL_STATE` when it must lock itself.
- Config cache generation is a coarse change detector for consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_errlog.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_errlog.c

This file implements the persistent logical data error log for a pool. It combines on-disk ZAP logs with in-core AVL lists of pending errors.

Key behavior:
- Error keys are stringified `zbookmark_phys_t` tuples using `bookmark_to_name()` as `objset:object:level:blkid` in lowercase hex.
- Kernel builds also parse bookmark strings back with `name_to_bookmark()`.
- `spa_log_error()` ignores try-import loads, chooses the scrub or last pending AVL list based on scrub state, deduplicates by bookmark, and records new pending errors.
- `spa_get_errlog_size()` sums on-disk scrub and last logs plus in-core pending lists; the last log is skipped after scrub completion because it is about to rotate.
- Kernel-only `spa_get_errlog()` copies bookmarks to userland from on-disk logs and pending lists, using separate error-log and error-list locks to avoid recursion when reads themselves produce errors.
- `spa_errlog_rotate()` marks scrub completion so future errors go to the next list and `spa_errlog_sync()` performs actual log rotation.
- `spa_errlog_drain()` frees pending AVL entries, used when unloading a faulted pool whose errors cannot be synced.
- `sync_error_list()` creates a ZAP if needed, writes each bookmark as a key with an optional stored name string, then destroys the in-core list entries.
- `spa_errlog_sync()` copies pending lists under lock, clears `spa_scrub_finished`, then under `spa_errlog_lock` writes current errors, rotates logs after scrub completion, writes scrub errors, updates MOS directory entries, and commits an assigned TXG transaction.

Important invariants:
- The persistent view is the union of last log, scrub/current log, and pending lists.
- Pending list lock is dropped before writing ZAPs so I/O errors during errlog syncing can still be logged.
- On-disk logs are ZAP objects referenced by `DMU_POOL_ERRLOG_LAST` and `DMU_POOL_ERRLOG_SCRUB`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_errlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_history.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_history.c

This file manages the pool history log, stored as a DMU object containing repeated little-endian record length plus packed nvlist records. The log behaves as a ring buffer while preserving the original pool creation command.

Key behavior:
- The history object bonus buffer is `spa_history_phys_t`, tracking physical max offset, logical BOF/EOF, preserved create-record length, and lost-record count.
- `spa_history_create_obj()` allocates the history object, adds it to `DMU_POOL_HISTORY`, and sizes the log to 0.1% of normal-class dspace, capped at 1 GiB and floored at 128 KiB.
- `spa_history_log_to_phys()` maps logical offsets to ring-buffer physical offsets after the preserved create region.
- `spa_history_advance_bof()` reads the next record length at BOF, advances BOF past that record, and increments `sh_records_lost`.
- `spa_history_write()` makes room by advancing BOF as needed, writes with wraparound, and advances EOF.
- `spa_history_log_notify()` converts selected history nvlist fields into normalized sysevent fields and posts `ESC_ZFS_HISTORY_EVENT`.
- `spa_history_log_sync()` creates the object lazily for older pools, adds timestamp and host, emits debug messages, posts internal history sysevents, packs the nvlist, writes length and record, and records the first command as the permanent create record.
- `spa_history_log()` wraps a command string; `spa_history_log_nvl()` sanitizes hidden args from input nvlist, adds zone and uid, and schedules async sync work.
- `spa_history_get()` reads command history chunks, waits for sync on first read when writeable, handles preserved-create reads, clamps overwritten offsets to BOF, and handles ring wraparound.
- `spa_history_log_internal()`, `_ds()`, and `_dd()` log internal TXG events, optionally tied to datasets or directories.
- `spa_history_log_version()` records pool/software/ZPL/UTS version information.

Important invariants:
- `spa_history_lock` protects ring offsets and writes.
- The first `ZPOOL_HIST_CMD` record is never overwritten.
- Internal events in syncing context write immediately; otherwise they schedule a sync task.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_history.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_log_spacemap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_log_spacemap.c

This file implements log space maps, an optimization for random-write/random-free workloads that batches metaslab space-map changes into pool-wide per-TXG log space maps and later flushes selected metaslabs.

Key behavior:
- On disk, `DMU_POOL_LOG_SPACEMAP_ZAP` maps TXG keys to log space-map object IDs.
- Each top-level vdev can persist per-metaslab unflushed TXGs in `VDEV_TOP_ZAP_MS_UNFLUSHED_PHYS_TXGS`.
- In memory, `spa_sm_logs_by_txg` tracks log maps by TXG with metaslab and block counts, `spa_metaslabs_by_flushed` orders metaslabs by `ms_unflushed_txg`, and `spa_log_summary` aggregates counts for fast flush estimation.
- Tunables control log space-map block size, unflushed memory limits, log block limits, summary length, minimum metaslabs to flush, historical TXGs used for incoming-rate estimation, and test behavior at export.
- `spa_log_sm_set_blocklimit()` derives a capped block limit from total metaslab count and tunables.
- `spa_log_summary_verify_counts()` cross-checks summary counters against AVL state and aggregate SPA counters when debug log-spacemap checks are enabled.
- `spa_log_summary_decrement_mscount()` and `spa_log_summary_decrement_blkcount()` maintain summary state when metaslabs flush or old logs are destroyed, including device-removal and flush-all corner cases.
- `spa_estimate_incoming_log_blocks()` averages recent log-map block counts, excluding the current syncing TXG.
- `spa_estimate_metaslabs_to_flush()` projects incoming blocks into future TXGs and uses the summary to choose a per-TXG flush count that keeps log blocks below the limit.
- `spa_flush_metaslabs()` runs only in sync pass 1, ensures a syncing log map exists, then flushes oldest metaslabs until block and memory heuristics are satisfied or all logs are requested for export.
- `spa_sync_close_syncing_log_sm()` records the current log map’s block count, updates aggregate block counts and summary, closes the map, and clears flush-all state after export flushing.
- `spa_cleanup_old_sm_logs()` destroys obsolete log maps whose TXG is older than the oldest unflushed metaslab TXG and removes their ZAP entries.
- `spa_generate_syncing_log_sm()` creates the ZAP on first use, activates `SPA_FEATURE_LOG_SPACEMAP`, allocates a new space map for the current TXG, adds in-memory tracking, and opens it with broad address range support.
- Import path: `spa_ld_unflushed_txgs()` loads per-metaslab unflushed TXGs, `spa_ld_log_sm_metadata()` loads and validates log metadata, `spa_ld_log_sm_data()` replays log entries into metaslab unflushed alloc/free trees, and `spa_ld_log_spacemaps()` orchestrates the full load.

Important invariants:
- Flush heuristics operate in sync pass 1 and depend on ordered metaslab and log-map trees.
- Log replay skips entries for removed vdevs and ignores entries older than a metaslab’s persisted unflushed TXG.
- Import failure paths still recompute metaslab accounting enough for clean teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_log_spacemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_misc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_misc.c

This broad infrastructure file implements SPA global state, locking, namespace lifecycle, vdev operation locking, auxiliary device tracking, tunables, accessors, import progress, scan stats, and initialization/finalization.

Key behavior:
- The opening block documents SPA lock ordering: `spa_namespace_lock`, per-SPA refcount, and ordered `spa_config_lock[]` levels from `SCL_CONFIG` through `SCL_VDEV`.
- Global tunables include debug flags, recovery behavior, deadman timing, free-on-EIO behavior, allocation inflation, slop-space policy, allocator count, special-class policy, and FPU enablement.
- `spa_load_failed()` and `spa_load_note()` emit structured debug messages for import/load diagnostics.
- `spa_config_lock_init()`, `spa_config_tryenter()`, `spa_config_enter()`, `spa_config_exit()`, and `spa_config_held()` implement multi-lock reader/writer config locking with writer ownership and waiters.
- Namespace functions include `spa_lookup()`, `spa_add()`, `spa_remove()`, and `spa_next()`, all coordinated by `spa_namespace_lock`.
- `spa_add()` allocates and initializes a `spa_t`, including mutexes, CVs, bplists, deadman cyclic, refcount, config locks, allocation trees, log-spacemap AVL/list structures, cachefile list, load info, label features, kstats, feature refcount cache, and leaf list.
- `spa_remove()` tears all of that down after the pool is uninitialized and refcount is zero.
- Refcount helpers are `spa_open_ref()`, `spa_close()`, `spa_async_close()`, and `spa_refcount_zero()`.
- Shared auxiliary AVL logic supports spares and L2ARC devices through `spa_aux_*`, with wrappers `spa_spare_*` and `spa_l2cache_*`.
- `spa_spare_poll()` probes inactive spares by scheduling async probe work.
- Vdev locking helpers `spa_vdev_enter()`, `spa_vdev_config_enter()`, `spa_vdev_config_exit()`, `spa_vdev_exit()`, `spa_vdev_state_enter()`, and `spa_vdev_state_exit()` coordinate namespace/config locks, autotrim, config sync, DTL reassessment, vdev free, state sync, and cachefile update.
- Miscellaneous helpers handle MOS feature activation, lookup by pool/device GUID, string allocation, random GUID generation, block-pointer formatting, pool freeze, recoverable panic behavior, hex parsing, and allocation-class feature activation.
- Accessors expose core SPA state, TXGs, root block pointer, dspace/checkpoint space, failmode, suspension, version, metaslab classes, log state, writeability, bootfs, delegation, MOS object set, dedup checksum, autotrim, multihost, and checkpoint predicates.
- `spa_preferred_class()` selects normal, log, special, or dedup allocation classes based on object type, level, size, and special-class reserve.
- Evicting objset helpers let unload wait for pending objset eviction and DMU buffer-user eviction.
- Size helpers compute DVA/BP disk size with deflation under `SCL_VDEV`.
- illumos import progress is exposed via kstats, with setters for load state, max TXG, and MMP seconds remaining.
- `spa_init()` initializes global AVL trees and subsystem dependencies; `spa_fini()` stops L2ARC, evicts pools, finalizes subsystems, and destroys globals.
- Scan helpers initialize and report pool scan stats, combining on-disk scan state with per-pass volatile counters.
- Checkpoint helpers include `spa_top_vdevs_spacemap_addressable()`, `spa_has_checkpoint()`, `spa_importing_readonly_checkpoint()`, `spa_min_claim_txg()`, and `spa_suspend_async_destroy()`.
- `zfs_post_dle_sysevent()` emits device LUN expansion sysevents in kernel builds.

Important invariants:
- Namespace mutation requires `spa_namespace_lock`.
- Vdev config changes are synchronized so administrator-visible operations wait for relevant TXGs.
- `spa_writeable()` requires both `FWRITE` mode and trusted config.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_map.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_map.c

This file implements ZFS space map object encoding, iteration, loading into range trees, append writing, histogram maintenance, truncation, allocation/freeing, incremental destruction, and size estimation.

Key behavior:
- Space map entries can be debug entries, single-word entries, or v2 double-word entries.
- `sm_entry_is_debug()`, `sm_entry_is_single_word()`, and `sm_entry_is_double_word()` classify encoded words.
- `space_map_iterate()` prefetches the requested byte range, walks DMU blocks, decodes non-debug entries, handles double-word entries with vdev IDs, validates alignment and bounds, and invokes a callback.
- `space_map_reversed_last_block_entries()` reads the final block and reverses entries while preserving double-word ordering, supporting safe backward destruction.
- `space_map_incremental_destroy()` destructively processes entries from the tail, invokes a callback, updates allocation accounting inversely as entries are removed, shrinks `smp_length`, and can stop early on callback error such as `EINTR`.
- `space_map_load_length()` and `space_map_load()` reconstruct a range tree by applying alloc/free entries; loading free maps starts with the full space range.
- Histogram functions clear, verify, and add range-tree histograms into the space-map histogram stored in `space_map_phys_t` when the bonus buffer supports it.
- `space_map_write_intro_debug()` appends a debug entry containing action, sync pass, and TXG.
- `space_map_write_seg()` appends one or more encoded entries for a segment, handles block boundaries, pads if a double-word entry would straddle a block, and splits runs by encoding limits.
- `space_map_write_impl()` writes all range-tree segments, choosing double-word entries when spacemap v2 is active and offset/run/vdev ID require it, or optionally for testing.
- `space_map_write()` dirties the header, updates `smp_object` for compatibility, adjusts `smp_alloc`, writes entries, and verifies the source range tree did not change during writing.
- `space_map_open()` allocates an in-core `space_map_t`, holds the bonus buffer, records block size and physical header pointer; `space_map_close()` releases it.
- `space_map_truncate()` either reallocates the object for changed bonus/block/indirect block sizing or frees all ranges in-place, then resets length, allocation, and histogram.
- `space_map_alloc()` allocates a DMU space-map object and increments the histogram feature refcount when enabled.
- `space_map_free_obj()` decrements the histogram feature refcount when appropriate and frees the DMU object.
- `space_map_estimate_optimal_size()` uses range-tree histograms to compute a worst-case encoded size, accounting for single-word versus double-word limits and padding.
- Accessors return object ID, allocated bytes, length, and number of blocks.

Important invariants:
- Space map writes occur in syncing context and caller-provided synchronization is required.
- The append format permits valid zero words, so incremental deletion cannot mark entries as zeroed; it shrinks from the end instead.
- Double-word entries are never split across DMU blocks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_reftree.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_reftree.c

This file implements space reference trees, an AVL-based sweep-line representation that converts ranges into offset deltas so unions and intersections can be computed by reference-count threshold.

Key behavior:
- A reference tree stores `space_ref_t` nodes sorted by offset, with pointer comparison as a tie-breaker so multiple deltas at the same offset can coexist.
- `space_reftree_create()` initializes the AVL tree.
- `space_reftree_destroy()` frees all `space_ref_t` nodes and destroys the AVL.
- `space_reftree_add_node()` allocates a delta node for a specific offset.
- `space_reftree_add_seg()` adds `+refcnt` at segment start and `-refcnt` at segment end.
- `space_reftree_add_map()` converts every range-tree segment into reference-tree deltas with the supplied refcount.
- `space_reftree_generate_map()` sweeps sorted deltas, tracks cumulative refcount, and emits ranges where `refcnt >= minref`.

Important uses:
- The file comment describes use in DTL reassessment: mirrors, RAID-Z, and interior vdevs can derive missing/outage regions by thresholding accumulated child DTL maps.
- Union is represented by `minref >= 1`; intersection by `minref >= N`.

Important invariants:
- Generated output range tree is vacated before filling.
- Final cumulative refcount must return to zero and no open range may remain at the end.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_reftree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/abd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/abd.h

This header declares the ABD abstraction, which represents ZFS buffers as either linear memory or scattered chunks and provides common allocation, ownership, copy, compare, zero, and RAID-Z iteration interfaces.

Key definitions:
- `abd_flags_t` includes `ABD_FLAG_LINEAR`, `ABD_FLAG_OWNER`, and `ABD_FLAG_META`.
- `abd_t` stores flags, logical size, optional parent pointer, child refcount, and either scatter metadata (`abd_offset`, `abd_chunk_size`, flexible `abd_chunks[]`) or a linear buffer pointer.
- `abd_iter_func_t` and `abd_iter_func2_t` define callback signatures for iterating over one or two ABDs.
- `zfs_abd_scatter_enabled` controls scatter allocation behavior externally.
- `abd_is_linear()` tests the linear flag.

Declared operations:
- Allocation/free: `abd_alloc()`, `abd_alloc_linear()`, `abd_alloc_for_io()`, `abd_alloc_sametype()`, `abd_free()`.
- Views/wrappers: `abd_get_offset()`, `abd_get_offset_size()`, `abd_get_from_buf()`, `abd_put()`.
- Buffer conversion/borrowing: `abd_to_buf()`, `abd_borrow_buf()`, `abd_borrow_buf_copy()`, return-copy variants, and ownership transfer/release.
- Data operations: `abd_iterate_func()`, `abd_iterate_func2()`, `abd_copy_off()`, copy to/from raw buffers, compare, and zero.
- RAID-Z support: `abd_raidz_gen_iterate()` and `abd_raidz_rec_iterate()` pass chunk arrays to parity generation/reconstruction callbacks.
- Inline zero-offset wrappers provide `abd_copy()`, `abd_copy_from_buf()`, `abd_copy_to_buf()`, `abd_cmp_buf()`, and `abd_zero()`.
- Lifecycle functions are `abd_init()` and `abd_fini()`.

Important invariants:
- `abd_size` excludes scatter offset.
- Ownership and parent/child refcounts allow sub-ABD views without losing lifetime tracking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/abd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/aggsum.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/aggsum.h

This header declares an aggregate counter structure designed to reduce contention by spreading deltas across per-bucket counters while maintaining global lower and upper bounds.

Key definitions:
- `aggsum_bucket_t` is cacheline-aligned and contains a mutex, signed delta, borrowed count, and padding.
- `aggsum_t` contains a global lock, lower and upper bounds, bucket count, and cacheline-aligned bucket array.
- The comment states the counter fans out over a selected number of CPUs.

Declared operations:
- `aggsum_init()` initializes an aggregate counter with a starting value.
- `aggsum_fini()` releases resources.
- `aggsum_lower_bound()` and `aggsum_upper_bound()` expose approximate bounds.
- `aggsum_compare()` compares aggregate state against a value, presumably using bounds before exact aggregation.
- `aggsum_value()` returns the aggregate value.
- `aggsum_add()` applies a signed delta.

Important role:
- This is a synchronization/data-structure interface for high-frequency counters where exact global updates would be too expensive on every modification.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/aggsum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc.h

This header declares the ARC and L2ARC public interfaces, ARC buffer structures, flags, sizing macros, callbacks, memory accounting, read/write entry points, and lifecycle functions.

Key definitions:
- `ARC_EVICT_ALL` is used by `arc_flush()` to request eviction of all available buffers from a state.
- `HDR_SET_LSIZE()`, `HDR_SET_PSIZE()`, `HDR_GET_LSIZE()`, and `HDR_GET_PSIZE()` store/recover logical and physical sizes in units of `SPA_MINBLOCKSHIFT`.
- `arc_read_done_func_t` and `arc_write_done_func_t` define completion callbacks.
- Generic read callbacks `arc_bcopy_func` and `arc_getbuf_func` are declared.
- `arc_flags_t` includes public request flags (`WAIT`, `NOWAIT`, `PREFETCH`, `CACHED`, `L2CACHE`, predictive/prescient prefetch) and private header flags for hash membership, I/O state, errors, indirect blocks, async priority, L2ARC write/evict state, encryption/authentication, metadata, L1/L2 header presence, compressed ARC, shared data, and compression encoding bits.
- `arc_buf_flags_t` tracks shared, compressed, and encrypted arc buffers.
- `arc_buf_t` links to its header, next buffer, eviction lock, data pointer, and flags.
- `arc_buf_contents_t` distinguishes data and metadata buffers.
- `arc_space_type_t` classifies ARC memory accounting for data, metadata, headers, L2 headers, other, and bonus.
- `arc_state_type_t` names ARC states: anon, MRU, MRU ghost, MFU, MFU ghost, and L2-only.

Declared ARC operations:
- Memory accounting and metadata queries: `arc_space_consume()`, `arc_space_return()`, `arc_is_metadata()`, `arc_is_encrypted()`, `arc_is_unauthenticated()`, `arc_get_compression()`.
- Raw/encryption transforms: `arc_get_raw_params()`, `arc_untransform()`, `arc_convert_to_raw()`.
- Buffer allocation and loaning: normal, compressed, and raw variants for `arc_alloc_*` and `arc_loan_*`.
- Buffer lifetime/access: `arc_return_buf()`, `arc_loan_inuse_buf()`, `arc_buf_destroy()`, size queries, access marking, release/released checks, freeze/thaw, and debug reference query.
- I/O: `arc_read()` and `arc_write()` are the main cache read/write interfaces, with zio, spa, block pointer, callbacks, priority, flags, and bookmark context.
- Free notification: `arc_freed()`.
- Cache pressure and reservation: `arc_flush()`, `arc_tempreserve_clear()`, `arc_tempreserve_space()`.
- Memory status and lifecycle: `arc_memory_is_low()`, `arc_all_memory()`, `arc_max_bytes()`, `arc_init()`, `arc_fini()`.

Declared L2ARC operations:
- Device add/remove/presence/rebuild: `l2arc_add_vdev()`, `l2arc_remove_vdev()`, `l2arc_vdev_present()`, `l2arc_rebuild_vdev()`.
- Range overlap checking: `l2arc_range_check_overlap()`.
- Lifecycle and worker control: `l2arc_init()`, `l2arc_fini()`, `l2arc_start()`, `l2arc_stop()`, `l2arc_spa_rebuild_start()`.

Important notes:
- ARC callbacks explicitly allow transform/authentication errors independent of zio errors, especially for encrypted data.
- Userland builds expose `arc_watch` and `arc_procfd` for watchpoint support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc.h -->