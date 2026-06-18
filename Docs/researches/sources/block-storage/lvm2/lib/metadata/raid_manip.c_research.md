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
