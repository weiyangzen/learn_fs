# Group Research: group_1133_lvm2_sources_block_storage_lvm2_lib_metadata_raid_manip_c_sources_b_b5b02e26be76

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/raid_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/raid_manip.c

This file implements LVM2’s RAID LV manipulation layer: RAID image/metadata sub-LV allocation, extraction, replacement, reshape, takeover between RAID layouts, split/merge of RAID images, failed-device cleanup, and degraded activation validation. It is the operational bridge between LVM metadata objects and dm-raid kernel target behavior.

Core responsibilities:
- Validates RAID conversion constraints: region size, stripe size, maximum image counts, sync state, kernel feature support, and segment-type compatibility.
- Manages hidden component LVs: `*_rimage_N`, `*_rmeta_N`, extracted component names, temporary rename suffixes, visibility flags, and `RAID_IMAGE` / `RAID_META` status.
- Coordinates metadata write/commit, suspend/resume, activation, backup, and cleanup sequences around operations that change active mappings.
- Implements reshape logic for striped RAID types, including out-of-place reshape space allocation, relocation, freeing, and kernel flag reset.
- Implements takeover logic between `linear`, `striped`, `mirror`, `raid0`, `raid0_meta`, `raid1`, `raid4`, `raid5*`, `raid6*`, and `raid10_near`.

Important entry points:
- `raid_ensure_min_region_size()` enforces dm-raid bitmap limits by growing region size until the RAID set fits within MD’s tracked-region limit.
- `lv_raid_in_sync()` wraps `_raid_in_sync()` and determines whether a RAID or mirror LV is fully synchronized.
- `lv_raid_image_count()` returns RAID area count, or `1` for non-RAID LVs.
- `lv_raid_has_visible_sublvs()` detects visible RAID component LVs, including split/tracking cases.
- `lv_raid_change_image_count()` adds or removes RAID images for mirror-style RAID changes.
- `lv_raid_split()`, `lv_raid_split_and_track()`, and `lv_raid_merge()` implement RAID1 image split, read-only tracking split, and merge-back flows.
- `lv_raid_convert()` is the main conversion dispatcher for reshape and takeover operations.
- `lv_raid_change_region_size()` changes RAID region size.
- `lv_raid_rebuild()` and `lv_raid_replace()` rebuild existing legs or replace selected PV-backed components.
- `lv_raid_remove_missing()` converts partial/missing RAID components to error segments.
- `lv_raid_clear_failed_devices()` and `lv_raid_count_failed_devices()` operate on dm-raid failed-device bits in metadata superblocks.
- `partial_raid_lv_supports_degraded_activation()` checks whether partial RAID can be activated without losing redundancy.

Key internal mechanisms:
- Kernel feature checks use segment-type handler `target_present()` attributes, especially `RAID_FEATURE_RESHAPE` and `RAID_FEATURE_NEW_DEVICES_ACCEPT_REBUILD`.
- `_lv_update_reload_fns_reset_eliminate_lvs()` is a central two-phase update/reload helper. It commits mapping changes, lets one-shot flags reach the kernel, clears flags such as `LV_REBUILD` and reshape delta bits, removes extracted LVs, and reloads again.
- `_alloc_image_components()` allocates data and metadata component LVs, using RAID-specific rimage extent math and optional PV constraints.
- `_extract_image_components()` and `_raid_extract_images()` detach RAID legs, clear RAID flags, make sub-LVs visible, rename them with `_extracted`, and leave holes or shift component arrays depending on caller needs.
- `_raid0_add_or_remove_metadata_lvs()` converts between `raid0` and `raid0_meta` by allocating or extracting metadata LVs.
- `_clear_meta_lvs()` temporarily detaches metadata LVs, reloads without them, clears them, and reattaches them. This is required for conversions that reorder device roles, such as `raid4 <-> raid5_n`.
- `_reorder_raid10_near_seg_areas()` reorders RAID0/RAID10 near layouts when taking over between striping and mirrored striping.

Reshape behavior:
- `_reshape_requested()` classifies whether a request is a reshape, invalid reshape, or not a reshape.
- `_raid_reshape()` handles same-level RAID changes: adding/removing devices, changing layout algorithm, changing stripe size, or freeing reshape space.
- `_lv_alloc_reshape_space()` allocates or relocates out-of-place reshape space at the beginning or end of each data image, using kernel-reported data offset to decide where existing reshape space lives.
- `_raid_reshape_add_images()` grows an active RAID set and marks new images with `LV_RESHAPE_DELTA_DISKS_PLUS`.
- `_raid_reshape_remove_images()` performs two-step shrink behavior: first mark disks with `LV_RESHAPE_DELTA_DISKS_MINUS`, then later remove completed/freed component pairs.
- `_raid_reshape_keep_images()` handles layout and stripe-size reshapes without changing image count.

Takeover behavior:
- `_possible_takeover_reshape_types[]` declares legal conversion families and which options are allowed (`--stripes`, `--stripesize`, `--regionsize`).
- `takeover_matrix.h` supplies the dispatch matrix used by `_get_takeover_fn()`.
- `_conversion_options_allowed()` validates user options and may replace a requested target with an intermediate “convenient” RAID type for staged conversions.
- `_takeover_upconvert_wrapper()` handles conversions from striped/raid0/raid1/raid4/raid5 to higher-redundancy layouts, including metadata allocation and rebuild setup.
- `_takeover_downconvert_wrapper()` handles conversions that remove redundancy or parity devices, including RAID10 area reorder and parity-device shifting.
- Many `_takeover_from_*` wrappers encode exact supported and unsupported conversion paths.

Safety and failure handling:
- Most destructive or resilience-reducing operations require active LVs, in-sync arrays, archive creation, and user confirmation unless `yes`/force paths apply.
- RAID0 device replacement is explicitly rejected.
- Integrity-enabled RAID blocks split, rebuild, degraded activation, and some linear conversions until integrity is removed or special replacement handling is used.
- Degraded replacement limits are enforced: cannot replace all legs, cannot exceed parity-device tolerance, and RAID10 cannot lose all devices in a mirror group.
- Partial RAID repair may try progressively smaller replacement sets and can replace partial multi-segment images with error targets to free allocatable space.
- Degraded activation checks ensure enough redundancy remains before allowing activation.

Dependencies and coupling:
- Heavily depends on `metadata.h`, `lv_alloc.h`, activation APIs, locking APIs, `segtype.h`, display/logging helpers, dm-raid status helpers, and `takeover_matrix.h`.
- Assumes first-segment RAID layout for top-level RAID LVs in most operations.
- Relies on LVM status flags and segment flags being consistent across top-level LVs, image LVs, metadata LVs, and temporary/extracted LVs.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/raid_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/segtype.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/segtype.c

This file provides lookup helpers for LVM segment types registered in `cmd_context->segtypes`.

Functions:
- `get_segtype_from_string(cmd, str)` searches registered segment types by name. If no match exists, it creates an unknown segment type with `init_unknown_segtype()`, appends it to the command context list, warns about the unrecognized type, and returns it.
- `get_segtype_from_flag(cmd, flag)` iterates registered segment types backwards and returns the first type whose flags match the supplied bit. Backward iteration supports aliases, for example returning `raid5` instead of `raid5_ls` where registration order makes that preferable.

Behavioral notes:
- Unknown on-disk segment type names can still be represented rather than immediately rejected.
- Flag lookup logs an internal error and returns `NULL` if no registered type matches.
- The file is small but central: conversion and metadata code use these helpers to map user-visible names and internal flags to `struct segment_type` objects.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/segtype.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/segtype.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/segtype.h

This header defines LVM segment-type flags, canonical segment-type names, predicate macros, the `struct segment_type` object, the `struct segtype_handler` vtable, initialization prototypes, and target feature bits.

Major definitions:
- Generic segment flags include split support, striped/mirrored areas, snapshot, virtual, monitored, raid, thin, cache, mirror, writecache, integrity, VDO, and unknown types.
- RAID flags cover `raid0`, `raid0_meta`, `raid1`, `raid10_near`, `raid4`, all RAID5 layout variants, and all RAID6 layout variants.
- Name constants define stable strings such as `linear`, `striped`, `mirror`, `snapshot`, `thin-pool`, `cache`, `raid5_ls`, `raid6_zr`, `vdo-pool`, and others.
- Predicate macros classify segment types and segments, for example `segtype_is_raid()`, `segtype_is_any_raid5()`, `seg_is_raid_with_meta()`, `seg_is_reshapable_raid()`, `seg_is_thin_pool()`, and `segtype_supports_stripe_size()`.

Key structures:
- `struct segment_type` stores list linkage, flags, parity-device count, handler operations, name, DSO name, loaded library pointer, and private handler data.
- `struct segtype_handler` defines operations for naming, target naming, display, text import/export, segment merge, dm target line construction, status/percent parsing, target presence checks, module requirements, monitoring, and cleanup.

Feature flags:
- RAID feature flags describe dm-raid target capabilities such as RAID10, RAID0, reshaping, RAID4, shrink, reshape, and accepting rebuild args with empty metadata.
- Thin, VDO, cache, snapshot, and mirror feature flags describe target-specific capabilities used by their segment handlers.

Design role:
- This header is the central classification contract for metadata code. Files such as `raid_manip.c` depend on these macros to choose conversion paths, validate supported operations, and decide whether a segment has metadata, parity, striping, mirroring, or reshape support.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/segtype.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/snapshot_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/snapshot_manip.c

This file implements classic LVM snapshot metadata manipulation: identifying origins and COW volumes, sizing COW storage, creating/removing snapshot metadata segments, managing merge state, visibility rules, and validating snapshot origins.

Core functions:
- `lv_is_origin()` returns whether an LV has snapshots.
- `lv_is_cow()` identifies classic COW snapshot volumes while avoiding confusion with thin merging origins.
- `find_cow()`, `find_snapshot()`, and `origin_from_cow()` navigate snapshot relationships.
- `cow_max_extents()` and `cow_has_min_chunks()` enforce COW size limits and minimum snapshot size.
- `lv_is_cow_covering_origin()` checks whether a COW LV is large enough to cover its origin.
- `lv_is_visible()` applies LVM snapshot visibility rules, hiding snapshot wrapper LVs and merging COWs while exposing virtual origins where appropriate.
- `init_snapshot_seg()` links origin, COW, and snapshot segment metadata, hides the COW, increments origin count, marks virtual origin status where needed, and optionally initializes merge state.
- `init_snapshot_merge()` and `clear_snapshot_merge()` manage snapshot-merge metadata flags and visibility changes.
- `vg_add_snapshot()` creates the internal snapshot LV and attaches the COW/origin relationship.
- `vg_remove_snapshot()` removes snapshot metadata, deactivates virtual origins when needed, updates/commits VG metadata, suspends/resumes active origins, and reactivates the COW.
- `validate_snapshot_origin()` rejects unsupported origins such as COWs, locked/pvmove/hidden volumes, merging origins, cache/thin pool internals, mirror subvolumes, RAID subvolumes, and RAID-with-integrity under cache/writecache wrappers.

Sizing behavior:
- `_cow_max_size()` models classic snapshot disk layout: header chunk, metadata chunks, and data chunks for origin chunks.
- `_cow_extra_chunks()` adds extra space for kernels without `SNAPSHOT_FEATURE_FIXED_LEAK`; kernels with the fixed leak feature do not need the extra allowance.
- Minimum COW size is `SNAPSHOT_MIN_CHUNKS` chunks.

Operational notes:
- Snapshot wrapper LVs are virtual and generally invisible; COW LVs are hidden while attached and made visible after removal.
- Snapshot merge uses both segment status and origin status `MERGING`; thin snapshot merge has special handling through `merge_lv`.
- Snapshot removal is careful around active origins: it writes metadata, suspends active origins, commits, activates the COW if necessary, and resumes the origin.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/snapshot_manip.c -->