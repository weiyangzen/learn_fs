# File Research: sources/block-storage/lvm2/lib/metadata/pool_manip.c

## Purpose

`pool_manip.c` contains common pool manipulation logic for thin pools, cache pools/cachevols, and pool metadata spare volumes. It attaches and detaches pool data/metadata/origin relationships, creates pool LVs from allocated extents, maintains historical LV ancestry when thin volumes are removed, recalculates pool chunk sizes from device hints, allocates pool metadata LVs, and manages the VG-level pool metadata spare.

## Key Responsibilities

- Pool attachment: attaches pool metadata LVs, pool data LVs, cache/thin pool LVs to user LVs, origins, indirect historical origins, and merge LVs while setting status bits, hiding internal LVs, and maintaining reverse `segs_using_this_lv` links.
- Pool detachment: detaches cache pools/cachevols or thin pools, removes pending thin messages for removed LVs, queues thin delete messages, detaches external origins, updates origin/snapshot relationships, preserves or removes historical GLV chains, clears thin/cache status, and nulls segment pointers.
- Pool lookup and validation: finds the unique pool segment referencing a pool data/metadata LV and validates chunk sizes through cache/thin-specific validators.
- Pool creation: converts a newly allocated LV into a thin/cache pool by first creating and wiping metadata storage, moving that segment into an internal `_tmeta`/`_cmeta` LV, adding data extents, optionally converting data to VDO, inserting a `_tdata`/`_cdata` layer, changing the segment type, and attaching data/metadata LVs.
- Metadata allocation: creates temporary metadata LVs for pool conversion and attaches/renames them to the internal metadata naming scheme.
- Pool metadata spare management: creates, renames, hides, extends, removes, and re-exposes the VG-level `_pmspare` LV used for automated pool metadata recovery.
- Metadata sizing: clamps and rounds pool metadata sizes to required min/max limits and converts final sizes to extents.

## Main Data And APIs

- Public entry points include `attach_pool_metadata_lv()`, `detach_pool_metadata_lv()`, `attach_pool_data_lv()`, `attach_pool_lv()`, `detach_pool_lv()`, `find_pool_seg()`, `validate_pool_chunk_size()`, `recalculate_pool_chunk_size_with_dev_hints()`, `create_pool()`, `alloc_pool_metadata()`, `add_metadata_to_pool()`, `handle_pool_metadata_spare()`, `update_pool_metadata_min_max()`, and `vg_remove_pool_metadata_spare()`.
- Status bits set or cleared include `THIN_POOL_METADATA`, `CACHE_POOL_METADATA`, `THIN_POOL_DATA`, `CACHE_POOL_DATA`, `THIN_POOL`, `CACHE_POOL`, `CACHE`, `THIN_VOLUME`, `LV_CACHE_USES_CACHEVOL`, `LV_CACHE_VOL`, `POOL_METADATA_SPARE`, and `LV_ACTIVATION_SKIP`.
- Thin-history state uses `struct generic_logical_volume`, `struct historical_logical_volume`, and `struct glv_list` to preserve ancestry for removed LVs when historical LV recording is enabled.

## Control Flow Notes

- `attach_pool_lv()` handles both thin and cache users. Cache pool/cachevol use hides the pool LV and marks cachevol compatibility with `LV_CACHE_USES_CACHEVOL`; thin users can also attach live/historical indirect origins and merge LVs.
- `detach_pool_lv()` has separate cache and thin paths. The thin path removes pending create messages, refuses duplicate delete messages, creates historical GLV records if needed, schedules thin-device deletion by device ID, unlinks origin/pool references, and rewrites thin snapshots of a removed origin as regular thin volumes.
- `create_pool()` commits and wipes the initially visible pool LV metadata area before making it internal. On later failures after activation-time commits, it tries to remove the partially created pool LV and commit cleanup.
- `handle_pool_metadata_spare()` derives requested spare size from existing pool metadata LVs when extents are unspecified, caps it at the current 16 GiB usable metadata limit, allocates a spare if missing, or extends the existing spare while preserving its segment type and mirror count.

## Dependencies

This file depends on activation/wipe helpers, LV allocation and creation, segment movement/layer insertion, thin message helpers, external origin detach, VDO conversion, LV rename/update, mirror count logic, device topology hints, config defaults, and metadata graph reverse-link helpers.

## Risks And Edge Cases

- Pool creation commits metadata before the full transformation is complete, so failure paths need explicit cleanup and may still require manual intervention.
- `find_pool_seg()` treats more than one non-pending referencing segment as an internal error; callers depend on unique ownership.
- Historical LV handling is subtle: removed thin origins may need ancestry rewired from live GLVs to historical GLVs, while disabled history removes indirect links instead.
- Chunk-size recalculation only uses direct PV areas; stacked AREA_LV geometry is left as a FIXME.
- Metadata spare removal depends on the `_pmspare` suffix and must generate a fallback `lvol%d` name if the original base name is already used.
- Disabling `poolmetadataspare` can leave pools without automated metadata recovery and emits a warning when a spare would otherwise be useful.

## Summary

`pool_manip.c` is the common pool graph editor for LVM2. It transforms ordinary LVs into pool data/metadata layouts, attaches and detaches pool users safely, preserves thin-history relationships, and maintains the VG-level metadata spare needed for pool recovery workflows.
