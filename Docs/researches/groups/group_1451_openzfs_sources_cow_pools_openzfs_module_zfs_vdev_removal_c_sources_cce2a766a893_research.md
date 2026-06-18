# Group Research: group_1451_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_removal_c_sources_cce2a766a893

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/openzfs`.  
Files read completely: `vdev_removal.c` 2616 lines, `vdev_root.c` 169 lines, `vdev_trim.c` 1802 lines, `zap.c` 1307 lines, `zap_fat.c` 1458 lines, `zap_impl.c` 558 lines, `zap_leaf.c` 858 lines.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_removal.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_removal.c

## Purpose
Implements OpenZFS vdev removal: auxiliary vdev removal, log vdev evacuation/removal, primary top-level singleton/mirror removal by copying allocated ranges elsewhere, recording indirect mappings, handling concurrent frees, canceling removals, and reporting removal progress.

## Main Responsibilities
- Disables/re-enables allocation for concrete top-level vdevs via `spa_vdev_noalloc()` and `spa_vdev_alloc()`.
- Removes hot spares and L2ARC devices from SPA auxiliary config nvlists.
- Evacuates log vdevs by passivating allocation, resetting logs, cleaning metadata, labeling removal, and replacing the slot with a hole vdev.
- Starts primary top-level removal by allocating indirect mapping/birth objects, recording `spa_removing_phys`, counting bytes to copy, dirtying MOS config state, and spawning `spa_vdev_remove_thread()`.
- Copies allocated segments from the removing vdev to replacement allocations, then syncs partial mappings through `vdev_mapping_sync()`.
- Handles frees during removal in `free_from_removing_vdev()`, including already-synced, in-flight, and not-yet-visited ranges.
- Completes successful removals by replacing the concrete vdev with an indirect vdev and destroying old space maps/ZAPs.
- Cancels removals by freeing mapped destinations, destroying mapping/birth objects, restoring allocation when allowed, and clearing removal state.

## Key Data And State
- `vdev_copy_arg_t`: per-copy-thread accounting for outstanding copy bytes and read/write error bytes.
- `spa_vdev_removal_t`: SPA removal state with range trees for not-yet-copied allocated segments, per-TXG deferred frees, new indirect mapping entries, bytes-done counters, max offsets to sync, a thread pointer, and synchronization primitives.
- Tunables:
  - `zfs_remove_max_copy_bytes`: memory budget for outstanding removal I/O.
  - `zfs_remove_max_segment`: largest requested destination allocation.
  - `zfs_removal_ignore_errors`: test/debug override allowing removal to continue after hard I/O errors.
  - `vdev_removal_max_span`: maximum free gap a remap segment may span.
  - `zfs_removal_suspend_progress`: test hook to pause removal progress.
- `DMU_POOL_REMOVING`: MOS ZAP entry persisted by `spa_sync_removing_state()`.

## Important Functions
- `vdev_passivate()` / `vdev_activate()`: toggle allocation state for a vdev and its log metaslab group while preserving pool progress guarantees.
- `vdev_remove_initiate_sync()`: sync-task initializer for primary device removal; creates indirect mapping state, initializes `spa_removing_phys`, counts bytes, dirties config blocks, and starts the copy thread.
- `spa_remove_init()`: pool-open recovery path that reloads active removal state and all indirect vdev mappings in newest-to-oldest order.
- `free_from_removing_vdev()`: synchronizing-context handler that updates original space maps, tracks in-flight frees, frees synced destination mappings, and adjusts progress accounting.
- `vdev_mapping_sync()`: sync task that persists new indirect mapping entries, records birth offsets, drains per-TXG deferred frees, and writes updated removal progress.
- `spa_vdev_copy_segment()` / `spa_vdev_copy_impl()`: allocate destination DVAs, create mapping entries, issue physical read/write zio trees, handle mirrors child-by-child, and shrink allocation size on `ENOSPC`.
- `spa_vdev_remove_thread()`: open-context background worker that walks metaslabs, loads allocated space maps, copies segments TXG by TXG, detects copy errors, and either completes or cancels removal.
- `vdev_remove_complete()` / `vdev_remove_complete_sync()`: convert the removed vdev to an indirect vdev and finish on-disk state cleanup.
- `spa_vdev_remove_cancel_sync()`: undo partial removal by freeing mapped destinations, dropping obsolete state, destroying indirect mapping objects, and reactivating allocation if the property permits.
- `spa_vdev_remove_top_check()`: enforces removal constraints: top-level concrete vdev, feature enabled, no active removal, sufficient free space, healthy DTLs, same ashift, no raidz/draid destinations, and simple mirror topology.
- `spa_vdev_remove()`: public dispatcher for spares, L2ARC, log vdevs, and primary top-level vdevs.

## Control Flow Notes
- Primary device removal begins under config locks but data evacuation happens in a background open-context thread; every copied range is committed through sync tasks.
- Mapping entries are append-only by increasing source offset. This ordering lets frees compare their offset against synced and in-flight max offsets.
- Removal requires same ashift across normal-class vdevs because copied ranges must not gain allocator padding that would desynchronize mapping sizes.
- Normal-class raidz/draid destination vdevs are rejected because segment copies are not block-boundary aware and cannot synthesize parity columns.
- Removal and pool checkpoint/discard are mutually exclusive.
- Successful completion waits for deferred frees, stops initialize/TRIM/autotrim/rebuild activity, tears down metaslabs, then relabels the removed physical vdev.

## Error Handling And Invariants
- The copy thread cancels removal on read/write errors unless `zfs_removal_ignore_errors` is set.
- `vdev_passivate()` refuses to disable allocation on the last usable normal-class allocating vdev.
- Cancel paths assert no new segment lists are pending, free all already-mapped destinations, and remove feature references.
- Sync-time assertions require `svr_bytes_done[]`, `svr_max_offset_to_sync[]`, and per-TXG lists to be drained before destruction.
- L2ARC and log removal stop TRIM/initialize activity before vdev teardown.

## Dependencies
Strongly coupled to SPA config locking, DMU transactions, DSL sync tasks, metaslab space maps, range trees, zio physical I/O, indirect vdev mapping/birth objects, ZAP metadata, vdev initialize/TRIM/rebuild code, and pool feature accounting.

## Research Notes
This is one of the highest-risk vdev state-machine files: correctness depends on TXG ordering, config-lock choreography, precise space accounting, and crash-resumable indirect mapping persistence. Any change should be tested across removal start, import/resume, concurrent frees, cancellation, error injection, log vdev removal, and aux vdev removal.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_removal.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_root.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_root.c

## Purpose
Defines the OpenZFS root vdev operations. The root vdev is a synthetic container for top-level vdevs and is responsible for opening/closing children and computing pool-level health from child open/state errors.

## Main Responsibilities
- Counts concrete, non-log, non-hole, non-indirect top-level vdevs as core data-bearing devices.
- Opens every child vdev during root open.
- Determines whether child open failures exceed the pool's allowed missing top-level-vdev budget.
- Reports root vdev state as healthy, degraded, or cannot-open based on faulted/degraded child counts.
- Exposes `vdev_root_ops` for the root vdev type.

## Key Data And State
- No private persistent state is introduced by this file.
- `vdev_root_core_tvds()` excludes holes, log vdevs, and indirect vdevs from the root failure budget.
- `too_many_errors()` compares current errors with `spa_missing_tvds_allowed()`, while always failing when every core top-level vdev is missing.

## Important Functions
- `vdev_root_core_tvds()`: returns the number of core top-level vdevs relevant to missing-device tolerance.
- `too_many_errors()`: central policy helper for deciding whether the root vdev must fail.
- `vdev_root_open()`: opens children, records missing top-level count during load, initializes reported sizes/shifts to zero, and returns failure if too many core devices failed.
- `vdev_root_close()`: closes all child vdevs.
- `vdev_root_state_change()`: maps child fault/degrade counts to root vdev state.
- `vdev_root_ops`: operation vector with root-specific open/close/state handlers and no I/O start/done handlers.

## Control Flow Notes
- The root vdev itself does not issue I/O and does not contribute allocation geometry.
- During pool load, root open records missing top-level vdev count in the SPA so import policies can account for it.
- Indirect vdevs are ignored for root missing-device tolerance because they no longer contain directly allocated pool data.

## Error Handling And Invariants
- A root vdev with no children fails with `VDEV_AUX_BAD_LABEL` and `EINVAL`.
- If too many core top-level children fail to open, root state is `VDEV_AUX_NO_REPLICAS`.
- Assertions ensure the counted error total does not exceed the core top-level vdev count.

## Dependencies
Depends on the vdev operation framework, SPA load state and missing-vdev policy, child vdev open/close helpers, and indirect vdev operation identity.

## Research Notes
This file is small but policy-significant: its exclusions for log, hole, and indirect vdevs affect import behavior and pool health classification after device removal or missing-device imports.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_root.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_trim.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_trim.c

## Purpose
Implements OpenZFS TRIM/discard support for vdevs, including manual `zpool trim`, automatic background trimming of recently freed ranges, simple one-shot leaf trimming, and whole-device L2ARC trim.

## Main Responsibilities
- Persists manual TRIM state, progress, and options in leaf vdev ZAP entries.
- Issues physical `zio_trim()` requests with max/min extent sizing, optional secure trim, per-leaf queue limiting, and manual rate limiting.
- Walks metaslab free/trim range trees and translates logical top-level ranges into physical leaf-vdev ranges.
- Runs manual TRIM threads per leaf vdev.
- Runs autotrim threads per top-level vdev, using `ms_trim` recently-freed ranges and a TXG-batched metaslab stride.
- Stops/restarts manual trim and autotrim safely during export, removal, detach, offline, expansion, and property changes.
- Trims full L2ARC cache devices when needed and clears the L2ARC device header afterward.

## Key Data And State
- Tunables:
  - `zfs_trim_extent_bytes_max`: max command size, default 128 MiB.
  - `zfs_trim_extent_bytes_min`: min useful command size, default 32 KiB.
  - `zfs_trim_metaslab_skip`: manual partial-trim behavior for uninitialized metaslabs.
  - `zfs_trim_queue_limit`: max queued TRIM I/Os per leaf.
  - `zfs_trim_txg_batch`: minimum TXG spacing between autotrim visits to a metaslab.
- `trim_args_t`: per-range walker context containing target leaf vdev, disabled metaslab, range tree, trim type, extent limits, flags, start time, and bytes done.
- Per-vdev fields managed here include `vdev_trim_state`, `vdev_trim_thread`, `vdev_trim_last_offset`, `vdev_trim_rate`, `vdev_trim_partial`, `vdev_trim_secure`, `vdev_trim_inflight[]`, and autotrim thread/cv fields.

## Important Functions
- `vdev_trim_change_state()`: transitions manual TRIM state, schedules ZAP persistence, records options, emits sysevents/history, and wakes waiters on non-active transitions.
- `vdev_trim_zap_update_sync()`: sync task that writes manual TRIM offset, action time, rate, partial/secure flags, and state to the leaf ZAP.
- `vdev_trim_range()` / `vdev_trim_ranges()`: issue sized physical trim I/O, enforce rate/queue limits, update stats, wait for completion before re-enabling metaslabs, and select callback by trim type.
- `vdev_trim_calculate_progress()` / `vdev_trim_load()`: reconstruct manual TRIM progress from persisted offset and current metaslab free state.
- `vdev_trim_thread()`: manual trim worker that sequentially disables metaslabs, loads allocatable space, translates ranges for one leaf, issues trims, and completes/cancels state.
- `vdev_trim()` / `vdev_trim_stop()` / `vdev_trim_stop_all()` / `vdev_trim_restart()`: public lifecycle operations for manual trim.
- `vdev_autotrim_thread()`: top-level background worker that periodically swaps `ms_trim`, builds per-leaf trim trees, issues best-effort automatic trims, and re-enables metaslabs after safe TXG waits.
- `vdev_autotrim()`, `vdev_autotrim_kick()`, `vdev_autotrim_stop_all()`, `vdev_autotrim_restart()`: autotrim lifecycle operations.
- `vdev_trim_l2arc_thread()` / `vdev_trim_l2arc()`: trim full cache devices and update L2ARC headers.
- `vdev_trim_simple()`: helper for direct leaf vdev trim over a supplied physical range.

## Control Flow Notes
- Manual TRIM disables one metaslab at a time so no allocation can race ahead of outstanding lower-priority trim I/O for the same ranges.
- Manual TRIM progress is offset-based and persistent; autotrim has no on-disk progress and is best effort.
- Autotrim processes non-consecutive metaslab groups to distribute trim load and enforce a minimum revisit interval.
- Manual trim yields over autotrim: autotrim skips leaves already running a manual trim and manual trim vacates `ms_trim` for the processed metaslab.
- TRIM is suppressed for detached/unwritable vdevs, vdevs being removed, and vdevs undergoing raidz expansion.

## Error Handling And Invariants
- Manual trim rolls back the last persisted offset when a trim fails due to vdev unavailability.
- Trim callbacks update per-vdev trim error counters and SPA I/O stats, then decrement in-flight counters and release config locks.
- `vdev_trim_ranges()` waits for all manual trim I/O before returning so re-enabled metaslabs cannot receive writes before overlapping trim completes.
- Autotrim abandons unprocessed `ms_trim` ranges when autotrim is disabled, reclaiming memory.
- Assertions protect against trimming non-leaf/non-concrete/detached/removing/expanding vdevs.

## Dependencies
Depends on SPA config locks, DMU transactions, DSL sync tasks, ZAP leaf metadata, metaslab range trees, vdev translation, zio trim I/O, ARC/L2ARC state, pool autotrim properties, and vdev removal/raidz-expansion state.

## Research Notes
TRIM safety hinges on metaslab disable/enable ordering, in-flight trim accounting, and config-lock release by callbacks. Tests should cover manual resume, cancellation, L2ARC removal, autotrim property toggles, unavailable devices, secure trim, and interaction with vdev removal/expansion.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_trim.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zap.c

## Purpose
Provides the public ZAP object API: create/destroy, lookup, add/update/remove, count, increment, value search, integer-key helpers, cursor iteration, prefetch, and stats. It dispatches between microzap and fatzap implementations.

## Main Responsibilities
- Allocates or claims DMU objects with ZAP-compatible byteswap type and initializes them as microzaps.
- Creates linked child ZAP objects by adding the new object ID into a parent ZAP.
- Looks up string and uint64-array keys, including normalization-aware matching and real-name return.
- Adds, updates, removes, counts, and increments entries.
- Upgrades microzaps to fatzaps when entry names/values or object size exceed microzap limits.
- Initializes and advances cursors for full or serialized iteration.
- Provides stats and object prefetch helpers.
- Exports the ZAP API symbols used by the wider OpenZFS kernel module.

## Key Data And State
- The file does not introduce global mutable state beyond exported functions.
- `zap_attribute_t` objects are allocated through helpers from `zap_impl.c`.
- Cursor state is carried in `zap_cursor_t`: held `zap_t`, optional held leaf, hash, collision differentiator, object set/object number, and prefetch preference.
- Microzap entries are managed through `mzap_*`; fatzap entries through `fzap_*`.

## Important Functions
- `zap_create_impl()` and wrappers: allocate/claim ZAP DMU objects with optional normalization, flags, block shifts, bonus type/length, and dnode size.
- `zap_lookup_norm_by_dnode()`: locks the ZAP, builds a normalized name, dispatches to `fzap_lookup()` or microzap btree lookup, and reports normalization conflicts.
- `zap_add_by_dnode()` / `zap_update_by_dnode()`: write string-keyed entries, upgrading to fatzap when microzap constraints are exceeded.
- `zap_add_uint64_by_dnode()` / `zap_update_uint64_by_dnode()`: uint64-keyed write paths that use fatzap semantics.
- `zap_remove_norm_by_dnode()` / `zap_remove_uint64_by_dnode()`: delete entries from microzap or fatzap.
- `zap_length_by_dnode()` and uint64 variant: report value integer size and count.
- `zap_count_by_dnode()`: returns microzap in-memory count or fatzap physical count.
- `zap_increment_by_dnode()`: lookup-add/remove helper for counters, removing zero-valued entries.
- `zap_value_search_impl()`: cursor-based scan for first entry whose first integer matches a masked value.
- `zap_cursor_init*()`, `zap_cursor_retrieve()`, `zap_cursor_advance()`, `zap_cursor_serialize()`, `zap_cursor_fini()`: iteration API.
- `zap_get_stats_by_dnode()`: fills microzap or fatzap stats.

## Control Flow Notes
- Most public object-number APIs hold the dnode, call the `_by_dnode` variant, then release the dnode.
- Microzap supports only one 8-byte integer value per short string key; larger or incompatible entries trigger fatzap upgrade.
- Cursor initialization takes and then drops the ZAP read lock while preserving underlying holds, letting retrieval reacquire locks per step.
- Serialized cursors pack hash bits and collision differentiator; corrupt serialized collision differentiators are reset to zero.

## Error Handling And Invariants
- Object creation asserts the DMU object type uses `DMU_BSWAP_ZAP`.
- Unsupported match types without normalization return `ENOTSUP`.
- Value reads return `EOVERFLOW` when caller buffers are too small and `EINVAL` for incompatible integer sizes.
- Add returns `EEXIST` when a key already exists; remove returns `ENOENT` when absent.
- Cursor retrieval returns `EIO` if initialized from a failed cursor and `ENOENT` at end.

## Dependencies
Depends on DMU object allocation/holding/freeing, dnode holds, microzap implementation, fatzap implementation, ZAP name normalization/hash helpers, btree cursor support, and module symbol export infrastructure.

## Research Notes
This file is the stable facade for ZAP consumers. Behavioral changes here affect directories, pool metadata ZAPs, feature state, vdev metadata, quotas, and any code storing structured key/value metadata in DMU objects.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_fat.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zap_fat.c

## Purpose
Implements the top half of fatzap: header and pointer-table management, microzap-to-fatzap upgrade, fatzap leaf lookup/split/growth/shrink coordination, attribute add/update/remove/lookup, cursor iteration, prefetch, and stats.

## Main Responsibilities
- Converts a microzap into a fatzap header, embedded pointer table, and first leaf block.
- Manages embedded and external pointer tables, including incremental growth through `zt_nextblk` and `zt_blks_copied`.
- Maps hash prefixes to leaf block IDs.
- Opens, creates, locks, and releases `zap_leaf_t` dbuf users.
- Splits full leaves and grows pointer tables as needed.
- Shrinks empty sibling leaves and truncates the object tail when possible.
- Implements fatzap CRUD operations by delegating entry storage to `zap_leaf.c`.
- Implements fatzap cursor iteration and stats collection.

## Key Data And State
- Tunables:
  - `zap_iterate_prefetch`: prefetch whole fatzap object when iterating from the beginning.
  - `zap_shrink_enabled`: enable collapsing empty sibling leaf blocks.
- `fzap_default_block_shift`: default 16 KiB fatzap block size.
- Fatzap physical state in `zap_phys_t`: block type, magic, salt, norm flags, flags, pointer table, free block cursor, leaf count, and entry count.
- `zap_table_phys_t`: external pointer table metadata, including current table, in-progress next table, copied block count, and shift.

## Important Functions
- `fzap_upgrade()`: rewrites a microzap header as fatzap, initializes embedded pointer table to leaf block 1, and initializes the first leaf.
- `zap_table_grow()` / `zap_grow_ptrtbl()`: allocate and incrementally copy larger pointer tables, first from embedded to external and then by doubling.
- `zap_table_store()` / `zap_table_load()`: read/write external pointer table entries, mirroring updates into an in-progress next table when growth is active.
- `zap_create_leaf()` / `zap_get_leaf_byblk()` / `zap_open_leaf()` / `zap_put_leaf()`: leaf dbuf lifecycle and locking.
- `zap_deref_leaf()`: validates the fatzap header and resolves a hash to the target leaf.
- `zap_expand_leaf()`: upgrades locks if needed, grows the pointer table if leaf prefix length equals table shift, creates a sibling leaf, splits entries, and updates pointer-table ranges.
- `fzap_lookup()`, `fzap_add_cd()`, `fzap_add()`, `fzap_update()`, `fzap_length()`, `fzap_remove()`: fatzap attribute operations.
- `fzap_cursor_retrieve()`: returns the next entry at or after cursor hash/cd, advances across leaf prefix ranges, and supports whole-object prefetch.
- `fzap_get_stats()`: collects header, pointer-table, and leaf histograms.
- `zap_shrink()`: recursively collapses empty sibling leaves, redirects pointer table entries, frees leaf blocks, and updates prefix lengths/freeblk.

## Control Flow Notes
- Fatzap pointer table entries reference fixed-size leaf blocks; leaves contain variable-length entry/name/value chunk chains.
- Splitting a leaf increases prefix length and moves entries with the next significant hash bit set into the new sibling.
- Pointer-table growth may span multiple transactions; `zt_nextblk` records the destination table while blocks are copied incrementally.
- Removing the last entry from a leaf may trigger recursive shrink only when the sibling exists and is also empty.
- Iteration uses hash/collision-differentiator ordering, not lexical name ordering.

## Error Handling And Invariants
- `fzap_checkname()` enforces name length limits, allowing new longer names only for directory ZAPs.
- `fzap_checksize()` accepts only 1, 2, 4, or 8-byte integers and caps value byte length.
- Corrupt fatzap headers return `EIO` from `zap_deref_leaf()`.
- Pointer-table I/O errors are checked before destructive split/shrink updates.
- `zap_expand_leaf()` handles concurrent split/growth by re-dereferencing after lock upgrade.

## Dependencies
Depends on DMU buffers, dnode prefetch and free-range operations, ZAP physical layout definitions, `zap_leaf.c` entry/chunk operations, ZAP locks from `zap_impl.c`, btree/cursor support, and object byteswap helpers.

## Research Notes
This file owns fatzap structural mutation. High-risk areas are pointer-table growth persistence, concurrent lock upgrades, leaf split/shrink races, cursor correctness across changing leaves, and long-name compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_fat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_impl.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zap_impl.c

## Purpose
Provides shared ZAP infrastructure: slab caches for names/attributes, string and uint64 key initialization, Unicode normalization and matching, hash computation, ZAP locking/unlocking and lock upgrades, byteswap dispatch, and attribute allocation helpers.

## Main Responsibilities
- Creates and destroys kmem caches for `zap_name_t` and `zap_attribute_t`, including long-name variants.
- Normalizes string keys according to ZAP normalization flags and match type.
- Initializes string and uint64-array `zap_name_t` objects.
- Computes salted CRC64-based ZAP hashes or accepts pre-hashed uint64 keys.
- Opens/locks ZAP objects from dnodes/dbufs and handles microzap growth or fatzap upgrade.
- Provides reader/writer lock upgrade helpers used by fatzap split/shrink.
- Tears down `zap_t` dbuf users on eviction.
- Dispatches byteswap between microzap and fatzap formats.

## Key Data And State
- Static caches:
  - `zap_name_cache`, `zap_attr_cache` for normal names/attributes.
  - `zap_name_long_cache`, `zap_attr_long_cache` for longer directory names.
- `zap_name_t` captures original key, normalized key, integer width, integer count, match flags, norm flags, computed hash, owning `zap_t`, and normalization buffer size.
- `zap_t` lock state and micro/fat identity are maintained as dbuf user data.

## Important Functions
- `zap_init()` / `zap_fini()`: lifecycle for ZAP object caches.
- `zap_name_alloc_str()` / `zap_name_alloc_uint64()` / `zap_name_init_str()` / `zap_name_free()`: key wrapper allocation and initialization.
- `zap_normalize()` / `zap_match()`: Unicode textprep normalization and match-type-aware comparison.
- `zap_hash()`: CRC64 hash over normalized string or uint64 key material, masked to either 28 or 48 significant bits depending on flags.
- `zap_lock_impl()`: validates object type, opens microzap if needed, chooses lock mode, dirties dbuf for writers, grows microzap block size, activates large-microzap feature when needed, and upgrades to fatzap if microzap max size is exceeded.
- `zap_lock_by_dnode()` / `zap_lock()` / `zap_unlock()`: public lock/hold wrappers.
- `zap_lock_try_upgrade()` / `zap_lock_upgrade()`: convert a read lock to writer lock while dirtying the header dbuf.
- `zap_evict_sync()`: destroys locks and micro/fat auxiliary state on dbuf eviction.
- `zap_getflags()`, `zap_hashbits()`, `zap_maxcd()`: format/flag helpers.
- `zap_byteswap()`: DMU byteswap callback for microzap/fatzap blocks.
- `zap_attribute_alloc()`, `zap_attribute_long_alloc()`, `zap_attribute_free()`: cursor attribute allocation.

## Control Flow Notes
- Match-type `MT_MATCH_CASE` removes case-folding for that lookup while preserving the original hash normalization rules.
- Hashing omits the terminating NUL for string keys for historical on-disk compatibility.
- Microzap growth can increase block size until the pool/dataset feature limits require conversion to fatzap.
- `zap_lock_impl()` may initially take a writer lock for a microzap operation, then downgrade if another thread already upgraded the object to fatzap.

## Error Handling And Invariants
- Non-ZAP DMU object types are rejected with `EINVAL`.
- Invalid microzap/fatzap on-disk state returns `EIO`.
- Unsupported normalization or match requests return `ENOTSUP`.
- Long key allocation must use the long-name cache when the key exceeds old ZAP maximum name length.
- `zap_maxcd()` reserves collision differentiator bits according to hash-width mode.

## Dependencies
Depends on DMU/dbuf/dnode lifecycle, DSL dataset feature activation, Unicode textprep, CRC64 tables, microzap/fatzap open and byteswap functions, and ZAP physical format flags.

## Research Notes
This file is the shared correctness boundary between public ZAP APIs and the micro/fat implementations. Normalization, hash masking, and lock-upgrade behavior must remain consistent with on-disk compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_impl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_leaf.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zap_leaf.c

## Purpose
Implements fatzap leaf blocks: byteswapping, initialization, chunk allocation/free, name/value array storage, hash-chain lookup, entry create/read/update/remove, normalization conflict detection, leaf split transfer, and leaf statistics.

## Main Responsibilities
- Defines the internal leaf chunk model: entry chunks, array chunks, free chunks, and hash chains.
- Converts leaf physical blocks between byte orders.
- Initializes a leaf header, hash table, and freelist.
- Stores variable-length names and values in chains of array chunks.
- Searches exact or closest entries by hash and collision differentiator.
- Reads entry names/values with integer-size conversion.
- Creates, updates, and removes entries while maintaining chunk/free counts and hash chains.
- Transfers entries between leaves during fatzap split.
- Generates per-leaf histograms for ZAP stats.

## Key Data And State
- `CHAIN_END` marks the end of chunk chains.
- `LEAF_HASH()` and `LEAF_HASH_ENTPTR()` derive the per-leaf hash bucket from global hash bits and leaf prefix length.
- Leaf physical state includes header fields `lh_prefix`, `lh_prefix_len`, `lh_nfree`, `lh_nentries`, `lh_freelist`, flags, hash table, and chunk array.
- `zap_entry_handle_t` points at a leaf entry and the hash-chain link that references it, enabling efficient removal/update.

## Important Functions
- `zap_leaf_byteswap()`: byteswaps leaf header, hash table, entry chunks, free chunks, and array metadata.
- `zap_leaf_init()`: clears and initializes a new leaf block and optionally marks collision-differentiator-sorted chains.
- `zap_leaf_chunk_alloc()` / `zap_leaf_chunk_free()`: freelist operations for individual chunks.
- `zap_leaf_array_create()` / `zap_leaf_array_copy()` / `zap_leaf_array_free()` / `zap_leaf_array_read()`: variable-length array chain management for names and values.
- `zap_leaf_array_match()`: compares stored keys against a `zap_name_t`, supporting uint64 keys, normalized matching, and fast exact string matching.
- `zap_leaf_lookup()`: finds an entry by key/hash in the appropriate hash chain.
- `zap_leaf_lookup_closest()`: finds the next entry at or after a `(hash, cd)` cursor position.
- `zap_entry_read()` / `zap_entry_read_name()`: copy value/name data out of an entry.
- `zap_entry_update()`: replace an entry value if enough free chunks exist.
- `zap_entry_remove()`: unlink an entry and free value/name/entry chunks.
- `zap_entry_create()`: allocate chunks, choose the lowest unused collision differentiator, populate an entry, and link it into the hash chain.
- `zap_entry_normalization_conflict()`: detects another same-hash entry with equivalent normalized form.
- `zap_leaf_split()`: updates prefixes, rebuilds hash chains, and moves entries whose next hash bit belongs in the new leaf.
- `zap_leaf_stats()`: fills histograms for pointer fanout, entries per leaf, fullness, chunks per entry, and bucket depth.

## Control Flow Notes
- Names and values are stored as big-endian byte streams inside array chunks; `ldv()` and `stv()` convert supported integer widths.
- Hash chains are sorted by collision differentiator for normalized ZAPs so normalized lookup finds the lowest-cd match.
- Entry creation may return `EAGAIN` when the leaf lacks enough free chunks, signalling `zap_fat.c` to split the leaf.
- `zap_leaf_split()` scans chunks sequentially, moving entries based on the next prefix bit and rehashing remaining entries.

## Error Handling And Invariants
- Integer widths are limited to 1, 2, 4, and 8 bytes; invalid paths panic in low-level conversion helpers.
- `zap_entry_read()` returns `EINVAL` when the stored integer size exceeds caller size and `EOVERFLOW` when the caller buffer is too small.
- `zap_entry_create()` returns `E2BIG` when a single entry cannot fit in any leaf and `EAGAIN` when this leaf needs splitting.
- Assertions validate leaf magic, chunk bounds, chunk types, freelist counts, and sorted-chain assumptions.

## Dependencies
Depends on ZAP physical layout macros from `zap_leaf.h`, key normalization/matching from `zap_impl.c`, fatzap split/growth orchestration from `zap_fat.c`, DMU buffer sizing, ARC headers, and SPA/ZIO definitions.

## Research Notes
This file is the low-level packed storage engine for fatzap entries. Bugs here can corrupt directories and metadata ZAPs, so changes need focused tests for long names, uint64 keys, collision chains, value resizing, split behavior, byteswap, and cursor iteration.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_leaf.c -->