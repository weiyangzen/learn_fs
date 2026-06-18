# Group Research: group_1445_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_draid_c_sources_c_c7184082e01f

Scope: `Docs/research_subset_a.md`; OpenZFS vdev implementation files under `sources/cow-pools/openzfs/module/zfs/`.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_draid.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_draid.c

## Purpose

Implements OpenZFS dRAID top-level vdev behavior plus the distributed spare pseudo-leaf vdev. dRAID spreads raidz-style redundancy groups across many children using fixed, deterministic permutation maps, reserves distributed spare capacity across those children, supports failure-domain layouts wider than a single child set, and exposes `vdev_draid_ops` / `vdev_draid_spare_ops` to the generic vdev layer.

## Main APIs And Entry Points

- Fixed layout generation: `vdev_draid_generate_perms()`, `vdev_draid_lookup_map()`, `vdev_draid_shuffle_perms()`, `vdev_draid_get_perm()`, and `vdev_draid_permute_id()` build and query the immutable child permutation table.
- Size and allocation geometry: `vdev_draid_psize_to_asize()`, `vdev_draid_asize_to_psize()`, `vdev_draid_get_astart()`, `vdev_draid_min_asize()`, `vdev_draid_min_alloc()`, `vdev_draid_rebuild_asize()`, and `vdev_draid_metaslab_init()` define full-stripe, group-aligned allocation behavior.
- dRAID I/O mapping: `vdev_draid_logical_to_physical()`, `vdev_draid_map_alloc_row()`, `vdev_draid_map_alloc()`, `vdev_draid_map_alloc_write()`, `vdev_draid_map_alloc_read()`, `vdev_draid_map_alloc_scrub()`, `vdev_draid_map_alloc_empty()`, and `vdev_draid_map_verify_empty()` turn a logical dRAID I/O into one or two raidz rows with parity, data, and empty skip-sector ABDs.
- Top-level vdev lifecycle and operations: `vdev_draid_init()`, `vdev_draid_fini()`, `vdev_draid_open()`, `vdev_draid_close()`, `vdev_draid_io_start()`, `vdev_draid_io_done()`, `vdev_draid_state_change()`, `vdev_draid_xlate()`, `vdev_draid_config_generate()`, `vdev_draid_nparity()`, and `vdev_draid_ndisks()`.
- Resilver and DTL helpers: `vdev_draid_missing()`, `vdev_draid_partial()`, `vdev_draid_readable()`, `vdev_draid_group_degraded()`, `vdev_draid_group_missing()`, `vdev_draid_need_resilver()`, and `vdev_draid_rebuilding()`.
- Distributed spare operations: `vdev_draid_spare_create()`, `vdev_draid_spare_get_parent()`, `vdev_draid_spare_get_child()`, `vdev_draid_fail_domain_allowed()`, `vdev_draid_spare_open()`, `vdev_draid_spare_io_start()`, `vdev_draid_read_config_spare()`, `vdev_draid_spare_lookup()`, `vdev_draid_spare_init()`, and config/fini helpers.

## Control Flow And Data Model

The top comment documents the on-disk layout contract: rows are 16 MiB-per-child chunks, groups are `ndata + nparity` columns, slices hold an LCM-based group count, and permutation rows spread groups across children and distributed spare slots. The hard-coded `draid_maps[]` table is part of the storage format; changing seeds, child counts, permutation counts, or checksums would change physical placement and make existing pools unreadable.

`vdev_draid_init()` validates the nvlist geometry, looks up the fixed map, generates the permutation array with the private PRNG, optionally shuffles slices for failure-domain layouts, and fills derived constants such as group width, usable disk count, group size, and per-device slice size. `vdev_draid_open()` opens normal children before distributed spares, checks parity/failure-domain tolerance, calculates allocatable size from the smallest non-spare child minus reflow reserve, and rounds capacity to row/group or big-slice boundaries.

Normal I/O starts in `vdev_draid_io_start()`. It creates a `raidz_map_t` that may contain two rows if a logical block crosses a dRAID group boundary. Writes always write full columns with zero-backed skip sectors included in parity. Normal reads read only needed data columns until error handling requires parity/empty-sector expansion. Scrub/resilver reads allocate backing ABDs for empty sectors so those bytes can be verified and repaired.

## Risks And Invariants

- The permutation table and PRNG output are on-disk compatibility data. Any behavioral change breaks existing dRAID pools.
- Group alignment is mandatory.
- Empty skip sectors are part of parity but not protected by the user data checksum.
- Distributed spare DTL behavior recurses through spare/replacing/dRAID-spare trees at the target physical offset.
- Repair during sequential rebuild is deliberately constrained because rebuild I/O may not have an end-to-end checksum.

## Summary

`vdev_draid.c` is the dRAID layout and dispatch engine. It deterministically maps logical dRAID space to raidz-style rows across permuted child devices, provides full-stripe write/read/scrub semantics, integrates dRAID-specific resilver decisions, and implements distributed spares as virtual leaves backed by parent dRAID child offsets.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_draid.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_draid_rand.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_draid_rand.c

## Purpose

Provides the deterministic pseudo-random generator used by dRAID permutation generation. It implements xoroshiro128++ 1.0 directly in-tree so dRAID layout generation does not depend on platform RNG behavior or external libraries.

## APIs And Behavior

- `rotl()` performs a 64-bit rotate-left primitive.
- `vdev_draid_rand(uint64_t *s)` takes a two-word mutable state, returns the next 64-bit value, and advances the state with xoroshiro128++ constants.

## Risks And Invariants

The exact arithmetic, rotations, and state update order are layout-critical. Even small changes would alter generated permutation maps and make dRAID physical placement incompatible with existing pools.

## Summary

This is a tiny but format-sensitive PRNG implementation that underpins stable dRAID child permutation maps.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_draid_rand.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_file.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_file.c

## Purpose

Implements file-backed leaf vdevs for OpenZFS and, in userland builds, maps disk vdev operations to the same file-backed implementation.

## Main APIs And Entry Points

- `vdev_file_init()` / `vdev_file_fini()` manage the global taskq.
- `vdev_file_open()` validates an absolute regular-file path, opens it, reports size, and supplies tunable ashift values.
- `vdev_file_io_start()` routes flush, TRIM, read, and write ZIOs to taskq workers.
- `vdev_file_io_strategy()`, `vdev_file_io_fsync()`, and `vdev_file_io_deallocate()` perform host file operations.

## Control Flow

Reads borrow an ABD buffer, call `zfs_file_pread()`, and copy data back. Writes borrow a copied ABD buffer and call `zfs_file_pwrite()`. Flush honors `zfs_nocacheflush`; TRIM delegates to `zfs_file_deallocate()`.

## Risks And Invariants

- File paths must be absolute and regular files in kernel builds.
- TRIM is optimistic because support depends on the host filesystem.
- Ashift tunables affect vdev geometry and are meaningful at creation time.

## Summary

`vdev_file.c` adapts ZIO/ABD operations to host file operations for file vdevs and userland disk access.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_file.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_indirect.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_indirect.c

## Purpose

Implements indirect vdevs, which represent removed top-level vdevs whose old block-pointer locations must be remapped to new locations elsewhere in the pool. It also implements obsolete-space accounting, mapping condensing, and split-block reconstruction.

## Main APIs And Entry Points

- Obsolete marking and syncing: `vdev_indirect_mark_obsolete()`, `spa_vdev_indirect_mark_obsolete()`, `vdev_indirect_sync_obsolete()`, `vdev_obsolete_sm_object()`.
- Condense lifecycle: `vdev_indirect_should_condense()`, `spa_condense_indirect_start_sync()`, `spa_condense_indirect_thread()`, `spa_condense_indirect_complete_sync()`, `spa_condense_init()`, `spa_condense_fini()`.
- Remapping/I/O: `vdev_indirect_remap()`, `vdev_indirect_io_start()`, `vdev_indirect_io_done()`, `vdev_indirect_read_all()`, `vdev_indirect_reconstruct_io_done()`, and `vdev_indirect_ops`.

## Control Flow

Obsolete tracking appends ranges to an in-memory range tree and syncs them to an obsolete spacemap. Condensing starts in sync context, creates a new mapping object, moves the old obsolete spacemap aside, then a zthr folds obsolete counts into the mapping and writes only still-referenced entries. Completion swaps the mapping under `vdev_indirect_rwlock`, frees the old mapping and spacemap, and clears persistent condense state.

`vdev_indirect_remap()` walks mapping entries and nested indirect vdevs using a stack. It copies relevant mapping entries while holding the mapping rwlock, then drops the lock before invoking callbacks, allowing condense to proceed safely.

For I/O, non-split remaps pass the original BP to the child vdev so normal checksum behavior applies. Split blocks issue per-segment I/O and validate the whole-block checksum at completion. On checksum failure or scrub/resilver, all mirror copies of all splits may be read, de-duplicated, and searched for a valid whole-block combination.

## Risks And Invariants

- Mapping entries must be copied under `vdev_indirect_rwlock` because condense may swap mapping objects.
- Split-block reconstruction is combinatorial and bounded by `zfs_reconstruct_indirect_combinations_max`.
- Condense restart depends on persistent MOS state and max-offset resume.
- Obsolete counts must not exceed mapped entry sizes.

## Summary

`vdev_indirect.c` is the removed-vdev remap engine: it translates old DVAs, tracks obsolete mapping space, condenses mappings, and reconstructs rare split blocks.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_indirect.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_indirect_births.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_indirect_births.c

## Purpose

Manages the vdev-indirect births object, an on-disk array describing the physical birth TXG for contiguous ranges copied during vdev removal.

## Main APIs And Entry Points

- Accessors: `vdev_indirect_births_count()`, `vdev_indirect_births_object()`, `vdev_indirect_births_last_entry_txg()`.
- Lifecycle: `vdev_indirect_births_alloc()`, `vdev_indirect_births_open()`, `vdev_indirect_births_close()`, `vdev_indirect_births_free()`.
- Mutation/query: `vdev_indirect_births_add_entry()` and `vdev_indirect_births_physbirth()`.

## Control Flow And Data Model

The object stores a bonus count plus a payload array of `vdev_indirect_birth_entry_phys_t`. Open reads the whole array into memory. Appending writes a new entry, increments the count, and rebuilds the in-memory table. Lookup binary-searches offsets, treating each entry as covering from the previous entry offset up to its own `vibe_offset`.

## Risks And Invariants

- Queries assume the range is contiguously mapped and below the last recorded offset.
- Entry ordering is semantic; binary search depends on monotonic offsets.
- Append reallocates the full in-memory table.

## Summary

This file is a compact DMU-backed table abstraction for mapping indirect-vdev source offsets to physical birth TXGs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_indirect_births.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_indirect_mapping.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_indirect_mapping.c

## Purpose

Provides the DMU-backed mapping table used by indirect vdevs. Each entry maps a source offset on a removed vdev to a destination DVA, optionally with an obsolete-byte count used by condense logic.

## Main APIs And Entry Points

- Accessors: `vdev_indirect_mapping_num_entries()`, `vdev_indirect_mapping_max_offset()`, `vdev_indirect_mapping_object()`, `vdev_indirect_mapping_bytes_mapped()`, `vdev_indirect_mapping_size()`.
- Lookup: `vdev_indirect_mapping_entry_for_offset()` and `vdev_indirect_mapping_entry_for_offset_or_next()`.
- Lifecycle: `vdev_indirect_mapping_alloc()`, `vdev_indirect_mapping_open()`, `vdev_indirect_mapping_close()`, `vdev_indirect_mapping_free()`.
- Obsolete accounting: `vdev_indirect_mapping_add_entries()`, `vdev_indirect_mapping_increment_obsolete_count()`, `vdev_indirect_mapping_load_obsolete_spacemap()`, `vdev_indirect_mapping_load_obsolete_counts()`.

## Control Flow And Data Model

The mapping object's bonus buffer stores entry count, max source offset, bytes mapped, and optionally a separate counts object. Open detects old-format objects by bonus size and reads all mapping entries into memory.

Lookup uses custom binary search because a source offset matches an entry when it lies in `[src_offset, src_offset + asize)`. The `or_next` variant returns the next greater entry when the offset is in a gap.

`vdev_indirect_mapping_add_entries()` appends pending entries in batches, writes optional obsolete counts, updates metadata, frees list nodes, and rebuilds the in-memory array.

## Risks And Invariants

- Entries are assumed sorted by source offset and non-overlapping.
- Range ends are exclusive.
- Obsolete counts are bounded by mapped entry size.
- In-memory arrays scale with mapping entry count.

## Summary

`vdev_indirect_mapping.c` stores, searches, appends, and obsolete-counts source-to-DVA mappings used after vdev removal.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_indirect_mapping.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_initialize.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_initialize.c

## Purpose

Implements `zpool initialize` support for leaf vdevs. Initialization writes a known filler pattern over currently free physical regions while persisting progress and state in leaf-vdev ZAP entries.

## Main APIs And Entry Points

- Public control: `vdev_initialize()`, `vdev_uninitialize()`, `vdev_initialize_stop()`, `vdev_initialize_stop_wait()`, `vdev_initialize_stop_all()`, `vdev_initialize_restart()`.
- Persistence: `vdev_initialize_change_state()`, `vdev_initialize_zap_update_sync()`, `vdev_initialize_zap_remove_sync()`, `vdev_initialize_load()`.
- Worker/I/O: `vdev_initialize_thread()`, `vdev_initialize_ranges()`, `vdev_initialize_write()`, `vdev_initialize_cb()`.
- Progress/range translation: `vdev_initialize_calculate_progress()`, `vdev_initialize_range_add()`, `vdev_initialize_xlate_range_add()`.

## Control Flow

`vdev_initialize()` records `VDEV_INITIALIZE_ACTIVE` and starts a worker thread. The worker loads persisted progress, allocates a reusable ABD filled with `zfs_initialize_value`, walks top-level metaslabs, disables each metaslab while inspecting free ranges, translates logical free space through `vdev_xlate_walk()` to leaf physical ranges, skips already initialized offsets, and writes remaining ranges in chunks.

`vdev_initialize_write()` limits concurrent writes, creates a DMU transaction for progress persistence, records the txg-local next offset, protects vdev lifetime with state config locks, checks stop conditions, and issues `zio_write_phys()`. The callback updates bytes done or error stats, rolls back the last offset for unavailable-device `ENXIO`, decrements inflight I/O, and wakes waiters.

Stop/restart paths coordinate state changes, cancellation, condition variables, txg sync waits, and import-time resume of active writable leaves.

## Risks And Invariants

- Initialization writes only free space observed while metaslabs are disabled.
- Last-offset persistence relies on txg-root ZIO ordering before sync tasks.
- Stop paths must avoid holding config/state writer locks while waiting.
- `vdev_xlate_walk()` is required for composite top-level layouts.
- Initialization is best-effort; I/O errors increment stats rather than necessarily failing the device.

## Summary

`vdev_initialize.c` coordinates persisted state, metaslab free-space traversal, translated physical writes, progress estimation, cancellation, and import-time restart for leaf vdev initialization.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_initialize.c -->