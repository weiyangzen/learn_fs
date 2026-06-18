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