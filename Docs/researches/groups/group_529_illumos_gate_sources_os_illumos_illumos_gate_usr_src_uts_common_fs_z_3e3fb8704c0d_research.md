# Group Research: group_529_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_3e3fb8704c0d

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all six requested ZFS vdev source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev.c

## Role

`vdev.c` is the central ZFS virtual-device management implementation. It owns generic vdev tree construction, open/close/reopen, validation, probing, metaslab setup, DTL management, state transitions, statistics, space accounting, dirty-list syncing, expansion, splitting, and helper predicates used by the ZIO and SPA layers.

It dispatches type-specific behavior through `vdev_ops_table`, covering root, raidz, mirror, replacing, spare, disk, file, missing, hole, and indirect vdevs.

## Core Responsibilities

Vdev allocation and topology:
- `vdev_alloc_common()` initializes `vdev_t`, locks, queues, DTL range trees, vdev cache, trim/initialize state, indirect mapping fields, and generated GUIDs.
- `vdev_alloc()` parses config nvlists for type, GUID, log status, RAID-Z parity, allocation class bias, paths, devids, ashift, metaslab metadata, indirect mapping objects, top/leaf ZAPs, DTL objects, offline/fault/degrade/remove flags, resilver txg, and deferred resilver state.
- `vdev_add_child()`, `vdev_remove_child()`, and `vdev_compact_children()` maintain child arrays, parent links, top-vdev pointers, GUID sums, and the SPA leaf list.
- `vdev_add_parent()` and `vdev_remove_parent()` wrap or unwrap devices in mirror/replacing/spare parents while preserving top-level identity where required.
- `vdev_top_transfer()` moves top-level allocation, metaslab, checkpoint, dirty-list, log, allocation-bias, indirect-removal, and scan-queue state between top-level vdevs.

Opening and probing:
- `vdev_open_children()` opens children in parallel unless any path uses zvols, where opens are serialized to avoid namespace-lock issues.
- `vdev_open()` handles persistent fault/offline state, invokes the type-specific open op, normalizes sizes and ashift, validates minimum allocatable size, handles expansion/shrink, probes leaves, updates min/max ashift, and asks scan code whether resilver is needed.
- `vdev_probe()` reads and optionally writes label pad regions to confirm access. It coalesces probe storms by keeping one active probe zio per vdev.
- `vdev_validate()` reads labels and checks pool GUID, vdev GUID/top GUID, split-pool markers, pool state, txg selection for rewind, and corrupted-label cases before `vdev_load()` can repair against the wrong device.
- `vdev_validate_aux()` performs a simpler label sanity check for spares and L2ARC devices.

Metaslabs and space maps:
- `vdev_metaslab_set_size()` chooses metaslab size/count from vdev size, targeting roughly 200 metaslabs while bounding small and huge devices.
- `vdev_metaslab_group_create()` assigns top-level vdevs to normal, log, special, or dedup metaslab classes.
- `vdev_metaslab_init()` loads or creates metaslabs and activates the metaslab group unless the vdev is being removed.
- `vdev_metaslab_fini()` passivates and destroys loaded metaslabs and checkpoint space maps.
- `vdev_destroy_spacemaps()` frees metaslab space-map objects and the metaslab-array object.
- `vdev_load()` recursively loads children, deflate ratios, allocation bias, metaslabs, checkpoint space maps, DTLs, and obsolete space maps.

DTL behavior:
- The file documents the DTL model for missing, partial, scrub, and outage ranges.
- Only leaf `DTL_MISSING` is persisted; parent DTLs and outage maps are derived.
- `vdev_dtl_dirty()`, `vdev_dtl_contains()`, and `vdev_dtl_empty()` manipulate in-core DTL range trees.
- `vdev_dtl_reassess()` recomputes DTLs after config changes or scrub completion, including scrub excision with a reference tree.
- `vdev_dtl_load()` loads persisted leaf DTL space maps.
- `vdev_dtl_sync()` rewrites leaf DTL space maps, destroys them for detached/removed leaves, and dirties config if the object changes.
- `vdev_dtl_required()` temporarily marks a device unreadable to determine whether offlining/detaching/removing it would lose access to data.
- `vdev_resilver_needed()` returns whether writable leaves still have DTL ranges and reports min/max txg.

Sync and dirty state:
- `vdev_dirty()` puts top-level vdevs, metaslabs, DTL leaves, or indirect obsolete segments on txg dirty lists.
- `vdev_sync()` syncs obsolete segments, creates metaslab arrays, syncs dirty metaslabs and DTLs, removes empty log devices, and schedules clean callbacks.
- `vdev_sync_done()` completes metaslab sync and reassesses metaslab group state.
- `vdev_config_dirty()` and `vdev_state_dirty()` maintain SPA dirty lists for config and state changes.
- Aux vdev config dirtying updates the L2ARC/spare nvlist directly.

State transitions:
- `vdev_fault()`, `vdev_degrade()`, `vdev_online()`, `vdev_offline()`, and `vdev_clear()` implement administrative state changes.
- `vdev_fault()` backs off to degraded if faulting a required data device would lose data.
- `vdev_online()` clears offline state, can request expansion, restarts initialize/trim work, and supports unspare handling.
- `vdev_offline_locked()` prevents offlining required data devices, resets removable log devices, and reopens the top-level tree to verify survivability.
- `vdev_set_state()` handles removed/cant-open/fault/degrade/healthy transitions, leaf close-on-dead behavior, FMA ereports, not-present handling during import/recover, and parent propagation.
- `vdev_propagate_state()` aggregates child readability/writeability into parent state and treats top-level log device failures as root degradation.

Statistics and accounting:
- `vdev_get_stats_ex()` reports vdev state, size, expandable size, fragmentation, initialize progress, trim progress, deferred resilver, and queue/histogram stats.
- `vdev_stat_update()` records successful I/O ops, bytes, latency histograms, scan/self-heal counts, and failed read/write/checksum counts.
- Failed writes can dirty DTLs in the correct txg context, including scrub-thread repairs and ZIL claim repairs.
- `vdev_space_update()` updates top-level, class, and root alloc/space/dspace counters using the vdev deflate ratio.

Other helpers:
- `vdev_readable()`, `vdev_writeable()`, `vdev_allocatable()`, and `vdev_accessible()` gate I/O paths.
- `vdev_is_concrete()` excludes indirect, hole, missing, and root vdevs from allocation/write paths.
- `vdev_xlate()` recursively translates a child logical range into top-level physical range through vdev-specific xlate ops.
- `vdev_expand()` initializes new metaslabs after device growth.
- `vdev_split()` removes a child from a mirror-like topology during pool split.
- `vdev_deadman()` panics if active leaf I/O exceeds the pool deadman timeout.
- `vdev_replace_in_progress()` detects replacing/spare replacement activity.

## Integration Notes

This file sits between SPA config/state locking, ZIO I/O execution, metaslab allocation, DMU transactions, ZAP metadata, labels, FMA ereports, scan/resilver, initialize/trim, and indirect-vdev removal.

Edits here are high risk because small state, locking, txg, or dirty-list changes can affect import, resilver, device replacement, pool expansion, fault handling, and sync-time metadata persistence.

## Risk Notes

- Locking assumptions are strict: many functions assert `SCL_ALL`, `SCL_STATE_ALL`, `SCL_ALLOC`, or sync-context ownership.
- DTL updates must remain txg-correct or resilver/scrub behavior can silently lose repair coverage.
- `vdev_open()` and `vdev_validate()` intentionally separate accessibility from label identity; collapsing them risks I/O to the wrong device.
- Top-level transfer during attach/detach/replacement carries many metadata fields; omissions can orphan allocation or indirect-removal state.
- `vdev_stat_update()` intentionally suppresses speculative errors, retryable failfast EIO, and some root-level propagated errors; changing this affects user-visible pool health.
- Indirect, hole, missing, aux, log, and concrete vdev distinctions are woven through allocation, writeability, dirtying, sync, and state propagation.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_cache.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_cache.c

## Role

`vdev_cache.c` implements the historical per-vdev read-ahead cache, also called the software track buffer. It inflates small metadata reads into larger aligned reads, stores them in an LRU cache, and serves later nearby reads from memory.

The implementation remains present but is disabled by default: `zfs_vdev_cache_size = 0`.

## Main Behavior

Cache structure:
- Each vdev has a `vdev_cache_t` with a lock, an AVL tree by offset, and an AVL tree by last-used tick.
- Cache blocks are `1 << zfs_vdev_cache_bshift`, defaulting to 64 KiB.
- Reads larger than `zfs_vdev_cache_max`, reads crossing cache-block boundaries, and reads with `ZIO_FLAG_DONT_CACHE` bypass the cache.
- Kstats track delegations, hits, and misses.

Operations:
- `vdev_cache_allocate()` reserves a placeholder entry before the fill I/O completes, preventing multiple threads from issuing the same read.
- `vdev_cache_read()` handles hits, in-flight fill delegation, and misses. On a miss, it creates a delegated read zio for the whole cache block and adds the original zio as a child.
- `vdev_cache_fill()` copies data to all waiting parent zios when the fill completes, then evicts the line if the fill failed or a write raced with the fill.
- `vdev_cache_write()` updates cached lines after writes, or marks in-flight lines with `ve_missed_update`.
- `vdev_cache_purge()`, `vdev_cache_init()`, and `vdev_cache_fini()` manage lifecycle.

## Integration Notes

The cache is below DMU semantics and above physical vdev I/O. It uses ABD buffers, delegated zios, AVL ordering, and per-vdev locking. Its hits use `zio_vdev_io_bypass()` so the original physical I/O does not proceed.

## Risk Notes

- Because the cache is disabled by default, changes may be rarely exercised in normal deployments.
- In-flight fill plus concurrent write handling depends on `ve_missed_update`; incorrect behavior can return stale data.
- LRU eviction refuses to evict entries with active fill I/O.
- Cache sizing uses global tunables, so enabling it can increase read amplification and memory consumption.
- ABD copy offsets must match cache phase and I/O offsets exactly.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_disk.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_disk.c

## Role

`vdev_disk.c` implements the kernel disk-backed leaf vdev operations using illumos LDI. It opens block devices, tracks devid/minor/path identity, registers LDI offline/degrade callbacks, issues physical reads/writes, cache flushes, TRIM, dump I/O, and pre-root device discovery for root-pool import.

## Main Behavior

Disk state:
- `vdev_disk_t` stores the decoded devid, minor name, LDI handle, registered LDI callback IDs, and an offline flag.
- `vdev_disk_bypass_devid` can deliberately ignore stored devids for recovery.
- `zfs_no_trim` disables TRIM globally.
- `zfs_nocacheflush` skips volatile write-cache flushes for debugging/performance analysis but is explicitly unsafe on power loss.

Open and identity:
- `vdev_disk_open()` requires an absolute path.
- It tries to open by user path first, with legacy whole-disk `s0` path repair if needed.
- It validates the opened device against the stored devid, then falls back to opening by devid, physical path, logical path, or pre-root alternate path.
- It can force a specific pre-root root-disk path through `vdev_disk_preroot_force_path()`.
- After opening, it may update or remove stored devid/minor values and refresh `vdev_physpath`.
- It registers LDI callbacks for offline and degrade events.
- It obtains physical size, media logical/physical block size, ashift, whole-disk maximum expansion size, write-cache enablement, TRIM support, and non-rotational property.

Close and callbacks:
- `vdev_disk_close()` frees devid/minor state, closes the LDI handle, removes callback registrations, and frees `vdev_tsd`.
- Offline notify marks `vd_ldi_offline`, posts removal, sets `vdev_remove_wanted`, and requests `SPA_ASYNC_REMOVE`.
- Offline finalize requests a probe if offline failed.
- Degrade finalize marks the vdev degraded.

I/O:
- `vdev_disk_io_start()` handles:
  - `DKIOCFLUSHWRITECACHE` using async `struct dk_callback`, unless disabled or known unsupported.
  - `ZIO_TYPE_TRIM` through `DKIOCFREE`, disabling future TRIM if unsupported.
  - normal reads/writes through `ldi_strategy()` with ABD-borrowed buffers.
- `vdev_disk_io_intr()` normalizes completion errors to `EIO`, treats residuals as errors, returns ABD buffers, frees the wrapper, and delays zio interrupt.
- `vdev_disk_io_done()` probes device state on EIO and schedules async removal or delayed close.
- `vdev_disk_dumpio()` supports crash-dump paths with `ldi_dump()` and normal dump I/O via synchronous physio.

Root-label and pre-root discovery:
- `vdev_disk_read_rootlabel()` opens a device by devid or path, reads labels, unpacks a valid config nvlist, and rejects destroyed or txg-zero labels.
- Pre-root scanning walks available block devices, records pool GUID/vdev GUID to devpath mappings, and allows lookup during early boot.
- `vdev_disk_preroot_init()` and `vdev_disk_preroot_fini()` manage the pre-root cache.

## Integration Notes

This file is the illumos-specific physical disk adapter for the generic vdev layer. It depends on LDI, DKIO ioctls, device identifiers, FMA removal/degrade paths, ABD buffer borrowing, ZIO completion, root-label config reading, and pre-root block-device walking.

## Risk Notes

- Device identity ordering is deliberate: path preserves administrator intent, devid survives recabling, and label validation happens at higher layers.
- Devid bypass permanently stops storing devid information for imported pools.
- `zfs_nocacheflush` can corrupt pools on power loss with volatile out-of-order write caches.
- TRIM support is mutable; failed `DKIOCFREE` can disable it for the vdev.
- Residual I/O counts are treated as hard errors.
- LDI offline can race with ordinary I/O; `vd_ldi_offline` prevents new work after notification.
- Pre-root scanning is best effort and intentionally ignores many invalid-label devices.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_file.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_file.c

## Role

`vdev_file.c` implements file-backed leaf vdev operations. It lets ZFS use regular files as vdevs, primarily for testing or non-production configurations, and provides a userland fallback where disk vdevs are accessed like files.

## Main Behavior

Open and close:
- `vdev_file_open()` requires an absolute path.
- File vdevs are marked non-rotational.
- TRIM is allowed as an attempted file-space punch operation, while secure TRIM is disabled.
- Files are opened from the global-zone root using `vn_openat()`.
- In kernel builds, the vnode must be a regular file.
- Physical size is taken from `VOP_GETATTR(AT_SIZE)`.
- `ashift` is set to `SPA_MINBLOCKSHIFT`.
- `vdev_file_close()` invalidates pages with `VOP_PUTPAGE(B_INVAL)`, closes the vnode, releases it, frees `vdev_file_t`, and clears delayed close.

I/O:
- `vdev_file_io_start()` handles:
  - `DKIOCFLUSHWRITECACHE` by calling `VOP_FSYNC(FSYNC | FDSYNC)`.
  - `ZIO_TYPE_TRIM` by issuing `VOP_SPACE(F_FREESP)` over the zio range.
  - reads/writes by creating a `buf_t`, borrowing an ABD buffer, and dispatching `vdev_file_io_strategy()` to `system_taskq`.
- `vdev_file_io_strategy()` performs `vn_rdwr()` at the logical block offset and completes the buf.
- `vdev_file_io_intr()` maps buf errors to `EIO`, maps successful residuals to `ENOSPC`, returns ABD buffers, frees the wrapper, and delays zio interrupt.
- `vdev_file_io_done()` is empty.

Ops:
- `vdev_file_ops` is a leaf vdev type with default asize and xlate behavior.
- In non-kernel builds, `vdev_disk_ops` aliases the same file-backed implementation.

## Integration Notes

This file bridges ZIO to vnode operations rather than LDI strategy calls. It uses ABD borrowing/copying, vnode read/write/fsync/space calls, taskq dispatch, and standard vdev open/close/asize hooks.

## Risk Notes

- File vdev paths must be absolute.
- Kernel file vdevs reject non-regular vnode types.
- Residual writes are reported as `ENOSPC`, unlike disk vdev residuals which become `EIO`.
- TRIM depends entirely on underlying filesystem support for `F_FREESP`.
- File-backed vdev semantics differ from disks for caching, allocation, flush, and failure behavior.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect.c

## Role

`vdev_indirect.c` implements indirect vdevs, which represent removed vdevs. Because old block pointers in snapshots cannot all be rewritten, ZFS keeps a mapping from old offsets on the removed vdev to new locations elsewhere in the pool. This file handles that mapping at runtime, obsolete-space accounting, mapping condensation, and reconstruction of split blocks.

## Obsolete-Space Model

The file documents the full obsolete-block pipeline:
- Each indirect mapping entry can have an obsolete byte count.
- Each indirect/removing vdev can have an obsolete space map containing obsolete DVAs since the last condense.
- Each dataset can have a remap deadlist for remapped blocks still referenced by snapshots.
- The pool can have an obsolete bpobj used when snapshots are destroyed.
- Sync-time processing moves obsolete entries to per-vdev obsolete space maps.

`vdev_indirect_mark_obsolete()` adds obsolete ranges to `vdev_obsolete_segments` and dirties the vdev when the obsolete-counts feature is enabled.

`vdev_indirect_sync_obsolete()` creates the obsolete space-map object if needed, writes accumulated obsolete segments, updates feature accounting, and clears the in-core range tree.

## Condensing

Condensing reduces indirect mapping size by integrating obsolete counts and space maps, then writing a new mapping that omits fully obsolete entries.

Major flow:
- `vdev_indirect_should_condense()` decides based on obsolete percentage, obsolete space-map size, mapping size, whether another condense is active, shutdown state, and whether the vdev is fully indirect rather than still removing.
- `spa_condense_indirect_start_sync()` creates the next mapping object, records the previous obsolete space-map object, detaches the old obsolete space map from the vdev ZAP, persists `DMU_POOL_CONDENSING_INDIRECT`, creates in-core condense state, and wakes the condense thread.
- `spa_condense_indirect_thread()` reconstructs precise obsolete counts, loads the previous obsolete space map, finds resume position from the new mapping’s max offset, generates new entries, and completes via sync task unless canceled.
- `spa_condense_indirect_generate_new_mapping()` iterates old mapping entries and commits only entries not fully obsolete.
- `spa_condense_indirect_commit_entry()` queues entries per txg and schedules `spa_condense_indirect_commit_sync()`.
- `spa_condense_indirect_complete_sync()` swaps the vdev to the new mapping, frees the old mapping and previous obsolete space map, clears condense state, removes the pool-directory marker, and dirties the config.
- `spa_condense_init()`, `spa_condense_fini()`, and `spa_start_indirect_condensing_thread()` handle import/restart and thread lifecycle.

## Remapping

`vdev_indirect_remap()` is the central mapping walker:
- Starts with an old indirect range and follows mapping entries until concrete vdevs are reached.
- Handles nested indirect vdevs with an explicit stack.
- Copies adjacent mapping entries while holding `vdev_indirect_rwlock`, then drops the lock before iterating to allow condensing to proceed.
- Calls a callback for each contiguous concrete segment.
- Also calls callbacks for indirect vdevs encountered, allowing callback-specific behavior.
- Supports debug-only split reversal to exercise split-block handling.

`vdev_indirect_mapping_duplicate_adjacent_entries()` copies the mapping entries covering a requested range while the rwlock is held.

The indirect vdev ops expose this as `vdev_op_remap`.

## I/O Path

`vdev_indirect_io_start()`:
- Creates an `indirect_vsd_t` with a list of split segments.
- Uses `vdev_indirect_remap()` and `vdev_indirect_gather_splits()` to build `indirect_split_t` entries.
- For non-split blocks, issues one child zio with the original block pointer so the normal child path can verify checksums and select mirror copies.
- For split reads/writes, issues child zios per segment without per-segment block-pointer checksums.
- For scrub/resilver split reads, reads all copies from mirror children.
- Split reads that initially checksum fail are retried through full reconstruction.

`vdev_indirect_child_io_done()` aggregates child errors into the parent and releases ABD references.

## Split-Block Reconstruction

Split indirect blocks can map different byte ranges to different top-level vdevs and mirror children. Because the checksum covers the full logical block, the code may need to try combinations of segment copies.

Main pieces:
- `vdev_indirect_read_all()` reads all readable copies of all split segments, including mirror children.
- `vdev_indirect_reconstruct_io_done()` deduplicates identical child data per split, computes the number of unique combinations, and either enumerates all combinations or tries random combinations.
- `vdev_indirect_splits_checksum_validate()` assembles selected split data into the parent ABD and validates the original checksum.
- `vdev_indirect_splits_enumerate_all()` deterministically tries every unique combination when feasible.
- `vdev_indirect_splits_enumerate_randomly()` tries bounded random combinations when the search space is too large.
- `vdev_indirect_splits_damage()` is a ztest/debug helper that intentionally damages copies to validate reconstruction.
- `vdev_indirect_repair()` writes the validated good split copy back over incorrect copies and posts checksum errors.
- `vdev_indirect_all_checksum_errors()` reports checksum errors for all read children when no valid reconstruction is found.

Tunable `zfs_reconstruct_indirect_combinations_max` limits exhaustive reconstruction, and `zfs_reconstruct_indirect_damage_fraction` injects test damage.

## Ops

`vdev_indirect_open()` synthesizes size from `vdev_asize` plus label areas and preserves `vdev_ashift`.
`vdev_indirect_close()` is empty.
`vdev_indirect_ops` is a non-leaf, non-concrete vdev type with remap support and no dump I/O or xlate op.

## Risk Notes

- Indirect mapping changes are protected by `vdev_indirect_rwlock`; remap copies entries before dropping the lock to avoid holding it across recursive or callback work.
- Condensing must be restartable after import and must not include newly obsolete ranges added after the condense starts.
- Split-block reconstruction can be computationally expensive; the random bounded fallback trades completeness for bounded work.
- Repair ignores DTL guesses and writes only copies shown to differ from the reconstructed good data.
- Obsolete-space accounting is feature-gated and sync-context-sensitive.
- Mapping entry order and offset contiguity assumptions are central to remap correctness.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_births.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_births.c

## Role

`vdev_indirect_births.c` manages the side table that records physical birth txgs for ranges in an indirect vdev mapping. This lets ZFS determine when a remapped range was copied during vdev removal.

## Main Behavior

Lifecycle:
- `vdev_indirect_births_alloc()` allocates a DMU metadata object with a bonus buffer containing `vdev_indirect_birth_phys_t`.
- `vdev_indirect_births_open()` holds the bonus buffer, points at the physical header, and reads all birth entries into memory when count is nonzero.
- `vdev_indirect_births_close()` frees the in-memory entry array, releases the bonus buffer, clears pointers, and frees the handle.
- `vdev_indirect_births_free()` frees the DMU object.

Accessors:
- `vdev_indirect_births_count()` returns entry count.
- `vdev_indirect_births_object()` returns the backing object number.
- `vdev_indirect_births_last_entry_txg()` returns the last entry’s physical birth txg.

Mutation:
- `vdev_indirect_births_add_entry()` appends `{max_offset, txg}` to the DMU object, increments the bonus-buffer count, and rebuilds the in-memory array with the appended entry.
- It requires syncing context and a syncing DMU transaction.

Lookup:
- `vdev_indirect_births_physbirth()` binary-searches entries to return the physical birth txg for a contiguously mapped range.
- Each entry implicitly describes the range from the previous entry’s offset to its own offset.
- The lookup asserts the requested `offset + asize` fits within the selected entry boundary.

## Integration Notes

This file is used by indirect-vdev removal/remap code alongside `vdev_indirect_mapping`. It depends on DMU object allocation, bonus buffers, sync-context transactions, and in-memory copies of fixed-size physical entries.

## Risk Notes

- Entries must remain sorted by increasing offset and physical birth txg.
- The binary search relies on implicit previous-entry boundaries, so a simple independent-entry search would be wrong.
- Lookups require the requested range to be contiguously mapped and within the last recorded offset.
- `add_entry()` rewrites the in-memory array on every append; this is simple but assumes append frequency and size remain manageable.
- Verification asserts object, objset, dbuf, physical header, and entry-array consistency.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_births.c -->