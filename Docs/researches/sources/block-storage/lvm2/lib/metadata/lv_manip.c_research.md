# File Research: sources/block-storage/lvm2/lib/metadata/lv_manip.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8704, source bytes 262125, report `Docs/researches/chunks/chunk_sources_block_storage_lvm2_lib_metadata_lv_manip_c_1_1_8704_40ee88714cc3_research.md`
- chunk 2: lines 8705-10224, source bytes 47037, report `Docs/researches/chunks/chunk_sources_block_storage_lvm2_lib_metadata_lv_manip_c_2_8705_10224_419d11165acf_research.md`

## Chunk Research

### Chunk 1: lines 1-8704

# Chunk Research: sources/block-storage/lvm2/lib/metadata/lv_manip.c lines 1-8704

## Scope

This report covers chunk 1 of `sources/block-storage/lvm2/lib/metadata/lv_manip.c`, lines 1-8704, within `Docs/research_subset_a.md` block-storage/LVM2 scope. The chunk contains most LV metadata manipulation machinery: LV role/layout classification, PV discovery, segment creation/removal, allocation search, LV extend/reduce/resize, rename, historical LV ancestry, LV creation, dependency removal, activation reload, and layer insertion helpers. The file continues after this chunk with pvmove layer insertion tail, wiping, activation/wipe helpers, virtual-origin creation, activation-skip helpers, and full `lv_create_single()`.

## Primary APIs In This Chunk

- `lv_layout_and_role()` builds string lists describing an LV's layout and role. It delegates to type-specific classifiers for mirror, RAID, thin, cache/writecache, integrity, VDO, and thick snapshots, then falls back to segment inspection for linear/striped/error/zero/unknown layouts.
- `get_pv_list_for_lv()` walks a top LV and its sub-LVs to collect unique PVs used by AREA_PV segment areas.
- `get_default_region_size()` resolves mirror/raid region-size configuration, rounds down to a power of two, and enforces page-size alignment.
- `alloc_lv_segment()` is the single construction point for LV segments.
- `allocate_extents()` is the main allocator entry point returning an `alloc_handle`.
- `lv_extend()`, `lv_reduce()`, and `lv_resize()` implement the major size-changing paths.
- `lv_remove_single()` and `lv_remove_with_dependencies()` implement command-level removal and dependent LV removal.
- `insert_layer_for_lv()`, `remove_layer_from_lv()`, and related helpers implement stacked/layered LV graph changes.

## Core Data And State

Allocation state is split across `struct alloc_handle`, `struct alloc_parms`, and `struct alloc_state`. These hold request-wide allocation parameters, one-policy-attempt flags, selected PV areas, log/metadata needs, cling tags, parallel PV avoidance data, and output `allocated_area` lists.

LV topology state is maintained through `lv->segments`, `seg->areas`, optional RAID `seg->meta_areas`, reverse references in `lv->segs_using_this_lv`, and LV/segment status bits for visibility, mirror/RAID/cache/thin/VDO/integrity roles, activation skip, pending delete, image/log/meta roles, and historical ancestry.

Resize state is carried in `struct lvresize_params`, while filesystem resize planning uses `struct fs_info` flags for fsck, mount, unmount, crypt resize, fs reduce, and fs extend.

## Control Flow

`lv_layout_and_role()` creates layout/role lists, applies type-specific detectors, falls back to segment type inspection, then prepends `public` or `private`.

Segment mutation is reference-count aware. AREA_PV mappings are assigned and released through PV allocation helpers. AREA_LV mappings update `segs_using_this_lv`. RAID metadata sub-LVs are routed through `meta_areas`.

`lv_reduce()` rounds RAID reductions to stripe boundaries and delegates to `_lv_reduce()`, which walks segments from the tail, releases areas, removes child logs/metadata/pools/cache/integrity LVs as needed, updates stacked sizes, unlinks empty LVs, and handles pool metadata spare cleanup.

The allocator builds PV maps, tries allocation policies from contiguous through the requested policy, derives flags with `_init_alloc_parms()`, scans PV areas in `_find_some_parallel_space()`, handles cling/contiguous/tag constraints, sorts candidate areas, allocates log/metadata slots, and materializes selected extents into `ah->allocated_areas[]`.

`lv_extend()` handles virtual segments directly, pool segments through `create_pool()`, simple segments through `lv_add_segment()`, and mirror/RAID through sub-LV creation plus `_lv_extend_layered_lv()`. Initial RAID creation commits metadata before wiping rmeta sub-LVs.

`lv_resize()` resolves which LV in a stack should be resized, checks type and use constraints, calculates extents from size/percent/policy options, acquires lockd resize locks, optionally activates inactive thin pools, handles filesystem reduce/extend, resizes thin metadata before data, reloads the top LV, updates pool metadata/messages, and deactivates temporary activations.

Filesystem reduce may unlock the VG for long-running scripts, then reacquire it and check for metadata mismatch. Reduce supports ext*, btrfs, swap, and crypt cases; xfs cannot reduce. Extend supports ext*, xfs, btrfs, and swap with mount-state-specific behavior.

## Dependencies

This chunk depends on LVM2 metadata helpers, segment type predicates, PV map/allocation primitives, activation and device-mapper helpers, lvmlockd shared-lock operations, configuration lookups, filesystem/device scripts, target feature checks for RAID/thin/VDO, and pool/cache/thin/VDO/integrity manipulation code elsewhere in `lib/metadata`.

## Risks And Edge Cases

- Allocation is complex and stateful; correctness depends on positional slot accounting, PV-area `unreserved` reset/reinsert behavior, and `allocated_areas[]` layout.
- `_init_alloc_parms()` contains a suspicious policy/flag-looking check involving `A_POSITIONAL_FILL`.
- `_for_each_pv()` notes that some callers may expect broader traversal than it actually performs; RAID metadata traversal is commented out.
- RAID/mirror sizing crosses logical extents, area extents, data copies, parity devices, metadata extents, and stripe counts.
- Filesystem reduce unlocks the VG and must detect concurrent metadata changes.
- Layer insertion/removal assumes strict one-to-one segment boundaries and has several internal consistency checks.
- `lv_remove_single()` can postpone VG write/commit, so callers must ensure a later commit path.

## Cross-Chunk References

- Lines after 8704 continue `_split_large_segments_for_pvmove()` and define `insert_layer_for_segments_on_pv()`.
- `wipe_lv()`, `activate_and_wipe_lvlist()`, and `activate_and_wipe_lv()` are used in this chunk but implemented after line 8704.
- `_create_virtual_origin()`, activation-skip helpers, `_should_wipe_lv()`, `_vg_check_features()`, `_lv_create_an_lv()`, and `lv_create_single()` are also after this chunk.
- `lv_resize()` is called from `tools/lvresize.c` and `lvmlockd.c`; `lv_extend()` and `allocate_extents()` are used by mirror, RAID, pool, VDO, integrity, and create code outside this file.

## Summary

Lines 1-8704 define the main metadata engine for reshaping LVM logical volumes. The chunk turns classify, create-empty, allocate, extend, reduce, resize, rename, remove, reload, and layer operations into concrete mutations of LV segment graphs and PV mappings across linear/striped, mirror, RAID, thin, cache/writecache, VDO, integrity, snapshot, pvmove, and historical LV cases.

### Chunk 2: lines 8705-10224

# Chunk Research: sources/block-storage/lvm2/lib/metadata/lv_manip.c lines 8705-10224

## Scope

This chunk covers the tail of pvmove/layer insertion helpers, LV wiping helpers, activation-skip policy, feature validation, and the main single-LV creation path.

## APIs and Entry Points

- `insert_layer_for_segments_on_pv()` inserts a mapping layer under selected `lv_where` segments after pvmove size splitting and PE-range boundary alignment.
- `wipe_lv()` wipes signatures and/or initializes an active LV, using `BLKZEROOUT` when possible and `dev_set_bytes()` as fallback.
- `activate_and_wipe_lvlist()` validates, activates, wipes, and deactivates a list of visible writable LVs.
- `activate_and_wipe_lv()` wraps the list path for one LV.
- `lv_set_activation_skip()` sets/clears `LV_ACTIVATION_SKIP`, defaulting thin snapshots to skip when configured.
- `lv_activation_skip()` decides whether activation should be skipped; deactivation is never skipped.
- `lv_create_single()` handles implicit pool creation, then delegates final LV creation to `_lv_create_an_lv()`.

## Key Control Flow

Pvmove/layer insertion:
1. Split oversized pvmove segments using `allocation_pvmove_max_segment_size_mb_CFG`.
2. Align segment boundaries to selected PE ranges.
3. Record affected lock-holder LVs in `lvs_changed`.
4. Move matching segment areas into `layer_lv` via `_extend_layer_lv_for_segment()`.

Wiping:
1. Require active local LV.
2. Resolve `/dev/<vg>/<lv>`, open read-write via label scan.
3. Optionally wipe known signatures.
4. Zero metadata fully or only initial sectors depending on config.
5. Invalidate label scan and clear `LV_NOSCAN` on success.

LV creation:
1. Validate duplicate names, VG feature support, activation support, stripe size, extents, pool size, and PV count.
2. Resolve pools/origins and classify thin/cache/VDO/snapshot behavior.
3. Create and extend the LV, then apply type-specific setup.
4. Write/commit VG metadata before activation.
5. Activate, wipe, and finalize VDO/cache/snapshot conversions.
6. Revert through centralized deactivate/unlock/remove paths where possible.

## State and Dependencies

Mutated state includes segment lists, LV sizes, `lvcreate_params`, thin pool transaction/device IDs, pool messages, and flags such as `LV_NOSCAN`, `LV_TEMPORARY`, `LV_ACTIVATION_SKIP`, `LV_NOAUTOACTIVATE`, `LV_NOTSYNCED`, `LVM_WRITE`, and `FIXED_MINOR`.

Major dependencies include dev-cache/label-scan wiping APIs, `lv_create_empty()`, `lv_extend()`, `vg_write()/vg_commit()`, activation/deactivation helpers, thin/cache/VDO conversion helpers, and lockd operations.

## Risks and Edge Cases

- Pvmove max segment size conversion can truncate from `uint64_t` to `uint32_t`.
- Stripe alignment can exceed the configured max segment size to preserve stripe boundaries.
- Segment splitting mutates lists while iteration still uses the original `seg`.
- Some `wipe_lv()` failure paths do not visibly call `label_scan_invalidate()`.
- Full metadata zeroing passes a shifted size through `size_t`, risking truncation on narrow platforms.
- `activate_and_wipe_lvlist()` deactivates all listed LVs, including ones already active before entry.
- `_lv_create_an_lv()` has many partial-state exits; not all go through full revert.
- Thin snapshot failure handling manually restores transaction IDs with acknowledged uncertainty.
- Cache/snapshot/VDO finalization paths include manual-intervention cases on failure.
- Revert skips `lv_remove()` for `lvconvert`, intentionally leaving possible abandoned LVs.

## Cross-Chunk References

- `_match_seg_area_to_pe_range()` begins before this chunk and is completed at the start of it.
- `_extend_layer_lv_for_segment()` is defined immediately before this chunk and performs the actual layer remapping.
- `_round_to_stripe_boundary()` is called here but defined earlier.
- Higher-level `lv_create_single()` callers and later orchestration are outside this chunk.
