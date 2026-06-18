# File Research: sources/block-storage/lvm2/lib/metadata/mirror.c

## Purpose

`mirror.c` implements classic LVM mirror metadata manipulation and pvmove mirror cleanup. It can create mirror images and mirror logs, convert linear LVs to mirrors, add/remove mirror legs or logs, split mirror images into a new LV, collapse temporary resync layers, fix imported mirror reverse references, and locate pvmove/mirror-related LVs.

## Key Responsibilities

- Mirror topology inspection: detects temporary mirror layers, counts effective mirror copies, finds the parent mirror segment for an image/log LV, finds pvmove LVs inside an LV tree, and lists LVs using a given LV.
- Mirror log management: creates disk or mirrored logs, writes the on-disk mirror log header, initializes log content by activating/wiping/deactivating the log LV, attaches/detaches log LVs, converts disk/core/mirrored log types, and maps user log names to counts.
- Mirror image creation: allocates destination extents, creates `_mimage_%d` internal LVs, inserts mirror layers, builds mirror segments, and supports segment-preserving mirror additions.
- Mirror image removal: moves removable images to the end without changing primary-order semantics, removes selected mirror images, handles partial or failed mirrored logs, converts orphaned sub-LVs to error targets, reloads affected active LVs, and then deactivates/removes temporary internal LVs.
- Mirror split/collapse: splits in-sync mirror legs into a new LV, optionally forming a new mirror from multiple split images; collapses temporary mirror layers once they are fully synced.
- Pvmove cleanup: redirects parent LVs away from pvmove layers, clears `PVMOVE`/`LOCKED` status, merges error segments, activates pvmoved parents after metadata updates, and supports pvmove-specific lookup by source device.

## Main Data And APIs

- Public entry points include `is_temporary_mirror_layer()`, `find_temporary_mirror()`, `lv_mirror_count()`, `find_mirror_seg()`, `adjusted_mirror_region_size()`, `find_active_pvmoved_lv()`, `activate_pvmoved_lvs()`, `detach_mirror_log()`, `is_mirror_image_removable()`, `collapse_mirrored_lv()`, `get_pvmove_pvname_from_lv_mirr()`, `find_pvmove_lv_in_lv()`, `find_pvmove_lv()`, `lvs_using_lv()`, `fixup_imported_mirrors()`, `remove_mirror_log()`, `prepare_mirror_log()`, `add_mirror_log()`, `attach_mirror_log()`, `lv_add_mirrors()`, `lv_split_mirror_images()`, `lv_remove_mirrors()`, `set_mirror_log_count()`, and `get_mirror_log_name()`.
- Internal helpers manipulate `struct lv_segment` area arrays, reverse dependency lists (`segs_using_this_lv`), LV status bits (`MIRROR`, `MIRRORED`, `MIRROR_IMAGE`, `MIRROR_LOG`, `PVMOVE`, `LOCKED`, `LV_NOTSYNCED`), and activation state.
- Mirror log headers use `MIRROR_MAGIC` and `MIRROR_DISK_VERSION` with little-endian fields written at byte offset zero of the activated log LV.

## Control Flow Notes

- `_shift_mirror_images()` preserves relative order of remaining images when moving a removable leg to the tail. This protects the primary mirror image semantics during failure recovery.
- `_init_mirror_log()` may commit VG metadata before activating the log LV. It temporarily inherits tags for activation, wipes the log to either in-sync or out-of-sync content, writes the mirror log header, deactivates the log, removes temporary tags, and removes the log LV on configured failure paths.
- `_remove_mirror_images()` is the core destructive conversion path. It selects removable images, releases segment areas, detaches logs when requested or required, replaces detached internal LVs with error segments, handles pvmove layer removal, reloads origins, activates changed pvmove parents, then removes temporary/orphan LVs.
- `remove_mirror_images()` may descend into temporary mirror layers and retry because removing one layer can expose another layer that becomes removable only after the first pass.
- `_add_mirror_images()` initializes a log before forming the mirror, meaning failure after log initialization must explicitly remove and commit away the abandoned log LV.

## Dependencies

This file depends on metadata graph helpers from `metadata.c`/`lv_manip.c`, allocation handles, LV segment creation helpers, activation/deactivation/reload helpers, device-cache and low-level device writes, tag lists, configuration flags for mirrored mirror logs, and mirror target status queries.

## Risks And Edge Cases

- Mirror removal is stateful and partially commits/reloads metadata; interruption can leave visible error-target LVs that the code intentionally asks the user to remove manually.
- Mirrored mirror logs are deprecated and guarded by configuration, but repair paths still need to handle failed mirrored logs.
- Removing the primary mirror image is blocked while an active mirror is out of sync unless the LV is already partial.
- Several paths only support single-segment mirrors, especially log conversion.
- Pvmove cleanup must maintain valid metadata after each incremental redirect of parent segments away from the pvmove LV.
- `get_pvmove_pvname_from_lv_mirr()` assumes usable first-area PV/device aliases and can return `NULL` for missing devices.
- Temporary mirror layer collapse is destructive: it requires metadata commits and suspend/resume, and it stops when a layer is not fully in sync.

## Summary

`mirror.c` is the classic mirror and pvmove-mirror topology mutator. Its main job is to keep LV segment arrays, internal image/log LVs, reverse references, activation state, and metadata commits coherent while adding, removing, splitting, collapsing, or repairing mirror structures.
