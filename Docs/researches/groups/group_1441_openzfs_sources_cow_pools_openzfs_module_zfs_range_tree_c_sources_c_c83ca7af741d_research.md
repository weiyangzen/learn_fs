# Group Research: group_1441_openzfs_sources_cow_pools_openzfs_module_zfs_range_tree_c_sources_c_c83ca7af741d

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/range_tree.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/range_tree.c

## Summary
Implements ZFS range trees: B-tree-backed interval sets used for free space and allocation-range tracking. It supports add/remove with automatic adjacent extent merging, extent splitting, traversal, clearing, swapping, and set-like XOR/remove-add operations.

## Main Responsibilities
- Creates and destroys range trees over `ZFS_RANGE_SEG32`, `ZFS_RANGE_SEG64`, and `ZFS_RANGE_SEG_GAP` segment encodings.
- Maintains total tracked space and a size histogram.
- Adds ranges by creating, extending, or merging segments.
- Removes ranges by deleting, shortening, or splitting segments.
- Supports gap-bridging trees with fill accounting for scan-style coalescing.
- Calls optional `zfs_range_tree_ops_t` hooks around create, destroy, add, remove, and vacate operations.

## Key APIs
- `zfs_range_tree_create()`, `zfs_range_tree_create_gap()`, `zfs_range_tree_create_flags()`, `zfs_range_tree_destroy()`.
- `zfs_range_tree_add()`, `zfs_range_tree_remove()`, `zfs_range_tree_remove_fill()`, `zfs_range_tree_resize_segment()`.
- `zfs_range_tree_find()`, `zfs_range_tree_contains()`, `zfs_range_tree_find_in()`, `zfs_range_tree_clear()`.
- `zfs_range_tree_walk()`, `zfs_range_tree_vacate()`, `zfs_range_tree_first()`.
- `zfs_range_tree_remove_xor_add_segment()`, `zfs_range_tree_remove_xor_add()`.
- `zfs_range_tree_space()`, `zfs_range_tree_numsegs()`, `zfs_range_tree_min()`, `zfs_range_tree_max()`, `zfs_range_tree_span()`.

## Important Behavior
Segments compare as non-overlapping intervals; overlap returns equality for B-tree lookup. Normal trees reject overlapping adds and missing removes with panic-recover diagnostics. Gap trees may merge nearby non-touching segments and track actual populated bytes through `fill`, but only support complete physical segment removal unless `zfs_range_tree_remove_fill()` can adjust fill.

`zfs_range_tree_vacate()` can either invoke a callback for every removed range while destroying B-tree nodes, or clear the tree directly. `zfs_range_tree_remove_xor_add_segment()` removes overlapping portions from one tree and adds uncovered portions to another.

## Risks
The implementation assumes callers provide external synchronization. Gap-tree semantics are stricter than normal interval trees; partial physical removes are illegal unless represented as fill changes. Callback users must tolerate remove/add callbacks around in-place segment resizing and fill adjustments.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/range_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/refcount.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/refcount.c

## Summary
Implements ZFS debug reference-count tracking. Under `ZFS_DEBUG`, a refcount can either be a fast untracked atomic count or a tracked AVL tree of holder records.

## Main Responsibilities
- Initializes and destroys the `reference_cache` slab.
- Creates tracked, untracked, or tunable-controlled `zfs_refcount_t` objects.
- Adds and removes references, including multi-reference holds.
- Preserves a short history of recently removed tracked references.
- Transfers counts between refcount objects and transfers ownership tags.
- Answers approximate or exact held/not-held queries depending on tracking mode.

## Key APIs
- `zfs_refcount_init()`, `zfs_refcount_fini()`.
- `zfs_refcount_create()`, `zfs_refcount_create_tracked()`, `zfs_refcount_create_untracked()`.
- `zfs_refcount_destroy()`, `zfs_refcount_destroy_many()`.
- `zfs_refcount_add()`, `zfs_refcount_add_many()`, `zfs_refcount_add_few()`.
- `zfs_refcount_remove()`, `zfs_refcount_remove_many()`, `zfs_refcount_remove_few()`.
- `zfs_refcount_transfer()`, `zfs_refcount_transfer_ownership()`.
- `zfs_refcount_count()`, `zfs_refcount_is_zero()`, `zfs_refcount_held()`, `zfs_refcount_not_held()`.

## Important Behavior
When tracking is disabled, add/remove are atomic count updates. When tracking is enabled, each hold records a holder pointer and reference number in an AVL tree; removal panics if the matching hold does not exist. Removed references can be kept in `rc_removed` for debugging history.

`zfs_refcount_held()` is exact only for tracked counters. For untracked counters it returns true if any reference exists, regardless of holder.

## Risks
This file is compiled only for `ZFS_DEBUG`, so production behavior depends on non-debug definitions elsewhere. Tracked mode has meaningful CPU and memory cost, which is why `reference_tracking_enable` defaults off. Holder identity is pointer/tag based and must be used consistently by callers.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/rrwlock.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/rrwlock.c

## Summary
Implements re-entrant read reader/writer locks (`rrwlock_t`) plus reader-mostly striped locks (`rrmlock_t`). Readers may reacquire read locks while a writer is waiting, avoiding self-deadlock while still preventing general writer starvation.

## Main Responsibilities
- Provides read/write enter, exit, held, init, and destroy operations.
- Tracks reader ownership through thread-specific data when needed.
- Gives waiting writers priority once anonymous readers drain.
- Rejects recursive writers and read-to-write recursion.
- Implements `rrmlock_t` as an array of `rrwlock_t` locks for lower read contention.

## Key APIs
- `rrw_init()`, `rrw_destroy()`.
- `rrw_enter_read()`, `rrw_enter_read_prio()`, `rrw_enter_write()`, `rrw_enter()`, `rrw_exit()`, `rrw_held()`.
- `rrw_tsd_destroy()`.
- `rrm_init()`, `rrm_destroy()`, `rrm_enter()`, `rrm_enter_read()`, `rrm_enter_write()`, `rrm_exit()`, `rrm_held()`.

## Important Behavior
Fast read acquisition can increment anonymous reader count without TSD when there is no writer pressure and full tracking is disabled. Once a writer is wanted, new readers are linked into per-thread TSD so re-entrant readers can be distinguished from unrelated readers.

`rrm_enter_read()` hashes the current thread to one shard. `rrm_enter_write()` acquires every shard for writing, making writes slower but reducing read-side lock contention.

## Risks
Read locks must be released by the same thread that acquired them, especially for `rrmlock_t` shard selection. `rrw_held(RW_READER)` is exact only when `track_all` is enabled; otherwise anonymous readers can make it report a reader hold without proving the current thread owns one.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/rrwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/sa.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/sa.c

## Summary
Implements ZFS System Attributes, a compact per-object attribute storage format using dnode bonus buffers and optional spill blocks. SA stores registered attributes according to persistent layout tables so common attribute sets can be represented compactly.

## Main Responsibilities
- Maintains per-objset SA state, attribute registries, and layout tables.
- Supports legacy ZPL znode layouts and modern `DMU_OT_SA` layouts.
- Builds and caches index tables mapping attribute IDs to offsets.
- Handles bonus/spill sizing, spill allocation/removal, and whole-layout rewrites.
- Performs SA byteswapping using registered per-attribute byteswap functions.
- Provides handle lifecycle and lookup/update/remove APIs.
- Converts older ZPL objects when adding project ID support in kernel builds.

## Key APIs
- `sa_cache_init()`, `sa_cache_fini()`.
- `sa_setup()`, `sa_tear_down()`, `sa_set_sa_object()`.
- `sa_handle_get()`, `sa_handle_get_from_db()`, `sa_handle_destroy()`, `sa_spill_rele()`.
- `sa_lookup()`, `sa_bulk_lookup()`, `sa_lookup_uio()`, `sa_size()`.
- `sa_update()`, `sa_bulk_update()`, `sa_remove()`.
- `sa_replace_all_by_template()`, `sa_replace_all_by_template_locked()`.
- `sa_object_info()`, `sa_object_size()`, `sa_get_db()`, `sa_get_userdata()`, `sa_set_userp()`.
- `sa_register_update_callback()`, `sa_handle_lock()`, `sa_handle_unlock()`.

## Important Behavior
SA layouts are arrays of attribute IDs persisted in ZAP objects. Each unique layout receives a layout number and can have cached `sa_idx_tab_t` offset tables keyed by layout and variable-length sizes. Adding/removing an attribute, or changing a variable-length attribute size, rebuilds the complete attribute set and may create a new layout.

`sa_find_sizes()` computes header size, aligned attribute payload size, and whether attributes must spill from the bonus buffer. Spill blocks are resized up to `SPA_OLD_MAXBLOCKSIZE`; unneeded spills are removed. Normal fixed-size same-length updates write in place.

## Risks
Correctness depends on registry/layout ZAP consistency, per-objset locks, handle locks, and dbuf lifetime management. Byteswapping requires SA metadata to be available, unlike simpler self-describing ZFS blocks. Whole-layout rewrites are sensitive to preserving old data, variable-length header slots, spill transitions, and legacy znode compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/sa.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/sha2_zfs.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/sha2_zfs.c

## Summary
Provides ABD-backed SHA-2 checksum implementations for ZFS checksums.

## Main Responsibilities
- Computes SHA-256 checksums over ABD buffers.
- Computes SHA-512/256 checksums in native and byteswapped forms.
- Uses QAT acceleration for SHA-256 when available and falls back to software.

## Key APIs
- `abd_checksum_sha256()`.
- `abd_checksum_sha512_native()`.
- `abd_checksum_sha512_byteswap()`.

## Important Behavior
`abd_iterate_func()` feeds ABD chunks into `SHA2Update()`. SHA-256 output is forced to big-endian word order to preserve compatibility with an older private implementation. SHA-512/256 native output is byteswapped word-by-word for the byteswap variant.

## Risks
The SHA-256 endian conversion is on-disk compatibility behavior and must not be “simplified.” QAT fallback must preserve identical digest output when hardware acceleration fails.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/sha2_zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/skein_zfs.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/skein_zfs.c

## Summary
Provides ABD-backed Skein MAC checksum support for ZFS.

## Main Responsibilities
- Computes native 256-bit Skein MAC checksums over ABD buffers.
- Provides a byteswapped checksum wrapper.
- Allocates and frees salted Skein context templates.

## Key APIs
- `abd_checksum_skein_native()`.
- `abd_checksum_skein_byteswap()`.
- `abd_checksum_skein_tmpl_init()`.
- `abd_checksum_skein_tmpl_free()`.

## Important Behavior
The native checksum requires a non-NULL context template. Each checksum copies the template, iterates ABD chunks through `Skein_512_Update()`, finalizes into `zio_cksum_t`, and clears the working context. Template initialization uses `Skein_512_InitExt()` with the checksum salt as key material.

## Risks
Callers must provide the template created by `abd_checksum_skein_tmpl_init()`. Contexts are explicitly zeroed before free or after use; that cleanup is part of the security-sensitive MAC handling.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/skein_zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_checkpoint.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_checkpoint.c

## Summary
Implements storage pool checkpoint creation, discard, statistics, and asynchronous discard processing. A checkpoint preserves a pool-wide rewind target by preventing checkpoint-referenced blocks from being reused.

## Main Responsibilities
- Creates a checkpoint from the most recently synced uberblock.
- Stores checkpoint state in the MOS and activates `SPA_FEATURE_POOL_CHECKPOINT`.
- Tracks freed checkpoint blocks in per-vdev checkpoint space maps.
- Discards checkpoint space maps incrementally over multiple TXGs.
- Reports checkpoint state, space, and start time.
- Completes discard by decrementing the feature refcount.

## Key APIs
- `spa_checkpoint_get_stats()`.
- `spa_checkpoint()`.
- `spa_checkpoint_discard()`.
- `spa_checkpoint_discard_thread_check()`.
- `spa_checkpoint_discard_thread()`.

## Important Behavior
Checkpoint create and discard use early sync tasks so state transitions happen before ordinary dirty data can free or reuse checkpoint-relevant blocks in the same TXG. Creation records `spa_ubsync` in `DMU_POOL_ZPOOL_CHECKPOINT` and sets `spa_checkpoint_txg`.

Discard first removes the checkpoint uberblock entry and clears `spa_checkpoint_txg`, then a zthr walks each top-level vdev checkpoint space map. Entries are prefetched in open context, then a sync task moves freed ranges into metaslab freeing trees and updates checkpoint space accounting. When all checkpoint space maps are gone, the feature is deactivated.

## Risks
Checkpoint semantics constrain pool operations that change topology or identity. Discard accounting spans vdev stats, pool checkpoint info, space maps, and metaslab trees; interruption and batching are intentional. The memory limit tunable controls prefetch/discard batch size.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_config.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_config.c

## Summary
Manages SPA pool configuration generation and cachefile synchronization. It writes imported writable pool configs to cache files and generates nvlists used in MOS configs and vdev labels.

## Main Responsibilities
- Writes or removes pool cache files.
- Synchronizes cachefile contents for all imported pools sharing a cache path.
- Tracks a global config generation for zone-visible config queries.
- Stores and replaces `spa->spa_config`.
- Generates pool and vdev configuration nvlists.
- Updates labels, expands newly added vdevs, waits for config sync, and refreshes cachefiles.

## Key APIs
- `spa_write_cachefile()`.
- `spa_all_configs()`.
- `spa_config_set()`.
- `spa_config_generate()`.
- `spa_config_update()`.

## Important Behavior
Cachefile writes pack an nvlist and overwrite the target path in place; if writing fails, the file is removed and an async config update is requested for retry. Read-only pools are excluded from cachefiles because they may not be importable on reboot.

`spa_config_generate()` includes pool identity, txg, host info, errata, allocation limits, comments, compatibility, top-level config, vdev tree, read-required features, and optional DDT stats. Temporary import names preserve the previous pool name in generated config.

## Risks
The cachefile can lag behind MOS config if a crash occurs between MOS sync and cachefile write, requiring explicit import. Config generation assumes SPA config/state locks are held. Cachefile path changes leave old dirents on `spa_config_list` until the next successful write removes stale entries.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_config.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_errlog.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_errlog.c

## Summary
Implements ZFS persistent logical data error logs. It supports both the legacy flat bookmark log and the newer `head_errlog` format that groups errors by head dataset and stores block birth TXGs.

## Main Responsibilities
- Logs pending uncorrectable data errors into in-memory AVL trees.
- Syncs current and scrub error lists into on-disk ZAP logs.
- Rotates logs when scrubs complete.
- Reports known errors to userland as bookmark arrays.
- Removes healed errors from pending and on-disk logs.
- Upgrades legacy error logs to the head-dataset format.
- Deletes or swaps dataset-specific errlogs for destroy/promote operations.

## Key APIs
- `spa_log_error()`.
- `spa_get_errlog()`, `spa_approx_errlog_size()`, `spa_get_last_errlog_size()`.
- `spa_errlog_rotate()`, `spa_errlog_drain()`, `spa_errlog_sync()`.
- `spa_remove_error()`.
- `spa_upgrade_errlog()`.
- `spa_delete_dataset_errlog()`, `spa_swap_errlog()`.
- `find_birth_txg()`, `find_top_affected_fs()`, `zep_to_zb()`, `name_to_errphys()`.
- `sync_error_list()`.

## Important Behavior
Errors are first inserted into `spa_errlist_last` or `spa_errlist_scrub` depending on scrub state. In sync context, lists are copied, locks are reordered safely, healed entries are removed, and errors are written to `DMU_POOL_ERRLOG_LAST` or `DMU_POOL_ERRLOG_SCRUB`.

Legacy logs key entries by full `zbookmark_phys_t`. `head_errlog` logs use a top-level ZAP keyed by head dataset object, with per-head ZAPs keyed by object/level/blkid/birth. Userland enumeration checks heads, snapshots, and clones to report affected datasets and can mark no-longer-present errors as healed.

## Risks
Lock ordering is explicit: dataset config locks precede errlog locks, and in-core lists are copied before disk updates because errlog writes can themselves encounter I/O errors. `head_errlog` processing depends on dataset holds, decryption availability, block-pointer birth lookup, and snapshot/clone ancestry. Upgrade intentionally skips entries it cannot validate to avoid permanent spurious errors.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_errlog.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_history.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_history.c

## Summary
Manages the on-disk SPA history log. The log stores packed nvlist records with little-endian length prefixes in a ring buffer while preserving the original pool creation record.

## Main Responsibilities
- Creates the history object and bonus-buffer offset metadata.
- Writes packed history records into a bounded ring buffer.
- Advances BOF when old records must be overwritten.
- Posts sysevents for internal history records.
- Logs command, ioctl, internal, dataset, dsl-dir, and version events.
- Reads history chunks for userland consumers.

## Key APIs
- `spa_history_create_obj()`.
- `spa_history_log()`, `spa_history_log_nvl()`.
- `spa_history_get()`.
- `spa_history_log_internal()`, `spa_history_log_internal_ds()`, `spa_history_log_internal_dd()`.
- `spa_history_log_version()`.
- `spa_history_zone()` outside kernel builds.

## Important Behavior
The physical log size is set to 0.1 percent of normal-class space, capped at 1 GiB and floored at 128 KiB. Logical offsets monotonically advance; `spa_history_log_to_phys()` maps logical offsets into the ring region after the preserved create record.

`spa_history_log_sync()` creates the history object for older pools, adds host info, emits debug messages, packs the nvlist, writes length and record bytes, and sets `sh_pool_create_len` after the first command record. `spa_history_get()` syncs pending async history on first read for writable pools.

## Risks
History writes are asynchronous for most callers, so record time can precede durable pool changes. Consumers must handle ring wrap and overwritten logical offsets. Hidden input nvlist arguments are stripped before logging, but callers still control what history metadata is submitted.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_history.c -->