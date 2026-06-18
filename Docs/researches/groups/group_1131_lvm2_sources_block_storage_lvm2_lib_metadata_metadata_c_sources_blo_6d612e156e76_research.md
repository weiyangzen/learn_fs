# Group Research: group_1131_lvm2_sources_block_storage_lvm2_lib_metadata_metadata_c_sources_blo_6d612e156e76

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/lvm2`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/metadata.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/metadata.c

## Purpose

`metadata.c` is the central in-core VG/PV/LV metadata orchestration file for LVM2. It creates, reads, validates, writes, commits, reverts, and tears down volume-group metadata; manages PV membership and metadata areas; performs access-control checks for system IDs, clustered/shared locking, exported VGs, and missing devices; and provides lookup/helper APIs used by LV manipulation, pool, mirror, activation, and command code.

## Key Responsibilities

- PV setup and VG membership: computes default PV metadata size, PE alignment, alignment offsets, adds/removes PVs from VGs, moves PVs between VGs, initializes new PVs, writes PV labels, and handles orphan PV reads.
- VG lifecycle: validates VG create/rename parameters, creates VGs with format instances, checks VG removal, removes VG metadata areas, archives metadata before writes, and updates backups/notifications after commits/removal.
- Metadata-area management: copies, indexes, ignores/unignores, moves, writes, precommits, commits, reverts, repairs, and removes `metadata_area` instances attached to a `format_instance`.
- Read path: `vg_read()` locks the VG, resolves duplicate names/VGIDs, optionally rescans labels, imports the newest valid metadata copy from MDAs, reconciles lvmcache with full VG metadata, sets PV device pointers, detects missing/wrong/outdated PVs, validates segment graphs, and creates a committed copy for update operations.
- Write path: `vg_write()` handles historical LV cleanup, optional validation, partial/duplicate/unknown-segment rejection, MDA copy balancing, outdated PV wiping, archive creation, PV header rewrites, MDA writes, precommit, and lockd update. `vg_commit()` commits MDAs and advances the cached committed VG; `vg_revert()` rolls back precommitted metadata.
- Validation and graph traversal: verifies PV/LV list consistency, duplicate names/UUIDs, segment integrity, pvmove shape, historical LV chains, tags, shared-lock metadata, pool metadata spare uniqueness, and LV/PV reference membership.
- Access policy: enforces `system_id`, shared lock type/lvmlockd state, clustered/exported flags, write permissions, missing PV behavior, persistent reservation requirements, and legacy `LVM_WRITE_LOCKED` encoding.

## Main Data And APIs

- `struct volume_group`, `struct physical_volume`, `struct logical_volume`, `struct lv_segment`, `struct pv_list`, `struct lv_list`, and `struct metadata_area` are the main metadata graph objects.
- `struct format_instance` is the per-VG metadata-location object, holding active/ignored MDA lists plus optional MDA index state.
- Important public entry points include `vg_create()`, `vg_read()`, `vg_read_for_update()`, `vg_write()`, `vg_commit()`, `vg_revert()`, `vg_validate()`, `pv_create()`, `pv_write()`, `add_pv_to_vg()`, `vg_extend_each_pv()`, `vg_split_mdas()`, `vg_remove_direct()`, `find_lv()`, `find_pv*()`, `find_seg_by_le()`, `lv_calculate_readahead()`, `vg_mark_partial_lvs()`, `pv_change_metadataignore()`, `scan_text_mismatch()`, and MDA/FID helpers.
- Temporary radix trees in validation check uniqueness and membership for PV IDs, LV names, LV IDs, historical LV names/IDs, and lock args. Read-only committed VGs may cache `lv_uuids` for activation lookups.
- `POSTORDER_FLAG` and `POSTORDER_OPEN_FLAG` are temporary LV status bits used while walking LV dependency graphs.

## Control Flow Notes

- `_vg_read()` first decides whether cached scan results are stale by checking lvmcache mismatches and text MDA offset/checksum changes. It builds a format instance from lvmcache-discovered MDAs, reads each candidate MDA, chooses the highest seqno metadata copy, warns about inconsistent old copies, then updates lvmcache using the chosen VG.
- `vg_read()` wraps `_vg_read()` with locking, duplicate-name handling, missing-PV detection, partial-LV marking, segment validation, device-size checks, device-use mismatch checks, access policy checks, and optional committed-copy import for later rollback/activation decisions.
- `vg_write()` increments the VG seqno only after validation and MDA-copy adjustment. It writes any needed PV headers first, then writes every usable MDA, reverts already-written MDAs on failure, precommits successful writes, and leaves the caller responsible for `vg_commit()` or `vg_revert()`.
- `_vg_commit_mdas()` temporarily moves ignored MDAs so ignored copies commit before active copies, reducing the chance that interruption leaves the ignored copy as the newest active-looking metadata.
- LV dependency walks visit snapshot origin/COW, external LVs, mirror logs, pools, metadata LVs, writecache/integrity metadata, AREA_LV segment areas, and origin snapshot COWs.

## Dependencies

This file depends heavily on lvmcache label-scan state, format handlers, text metadata import/export, device-cache and block-size helpers, allocation/PV segment helpers, activation state, archiver/backup code, lvmlockd, persistent reservation checks, configuration lookup, radix trees, and device-mapper cache state. Several public functions are consumed by `lv_manip.c`, `mirror.c`, `pool_manip.c`, thin/cache/VDO/integrity code, and command front ends.

## Risks And Edge Cases

- PV label writes and VG metadata writes are not atomic together; comments explicitly note limited revert support around non-orphan PV writes.
- `pv_create()` has a FIXME for detaching from the orphan VG in the error path, so partial in-memory state can persist after failure.
- Metadata read chooses newest seqno among MDAs but only warns about older inconsistent copies; repair is separate.
- Some lookup indexes (`vg->lv_names`, `vg->pv_names`, `vg->lv_uuids`) are valid only in specific read-only/read contexts and are not universally maintained after mutations.
- Missing PV handling distinguishes absent devices from reappeared devices with `MISSING_PV`; allocated reappeared PVs remain treated as missing until explicit repair/reduce actions.
- Shared-lock validation intentionally skips some missing `lock_args` errors due known transient states during snapshot and thin-pool conversion.
- `vg_write()` may proceed with failed MDAs when the command handles missing PVs, so later commit health depends on at least one good MDA.
- Outdated PV wiping mutates headers/MDAs based on lvmcache's outdated-device lists and is only run when commanded.

## Summary

`metadata.c` is the transaction and consistency core for LVM2 metadata. It coordinates cached scan data, on-disk metadata copies, in-memory VG graphs, PV headers, locks, access policy, validation, and repair-adjacent cleanup so higher-level LV operations can mutate metadata through a common read/write/commit model.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/metadata.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/metadata.h

## Purpose

`metadata.h` defines the internal metadata contracts shared across LVM2 metadata modules. It exposes format/MDA operation tables, format-instance state, metadata-area flags and error bits, segment access macros, small list wrapper types, format handler callbacks, and declarations for core VG/PV/LV metadata helpers implemented across `metadata.c`, `lv_manip.c`, `mirror.c`, `pool_manip.c`, thin manipulation, and PV accessors.

## Key Contents

- Constants and macros: `MIN_PE_SIZE`, `MAX_PE_SIZE`, `MIRROR_LOG_OFFSET`, `VG_MEMPOOL_CHUNK`, `dm_div_up()`, `dm_round_up()`, temporary postorder flags, `SHARED`, `FMT_PRECOMMIT`, MDA status bits, primary-MDA IO reasons, and `BAD_MDA_*` read/repair flags.
- `struct metadata_area_ops`: per-MDA callbacks for VG read/precommit-read, write, precommit, commit, revert, remove, metadata-location copy/name/offset, free/total sectors, membership check, PV MDA analysis, location comparison, device lookup, and config import/export.
- `struct metadata_area`: per-location state including ops pointer, opaque location, status, header start, scan-time text offset/checksum, MDA number, detected bad fields, and fields to suppress during repair.
- `struct format_instance_ctx` and `alloc_fid()`: describe and allocate format instances for a PV or VG reference.
- `struct format_handler`: per-format callbacks for scan, PV read/init/setup/add/remove/resize/write/rewrite check, LV/VG setup, segment support, format instance creation/destruction, and format destruction.
- Segment access macros: `seg_pvseg()`, `seg_dev()`, `seg_pe()`, `seg_le()`, and `seg_metale()`.
- Lightweight list records: `name_list`, `mda_list`, `peg_list`, and `seg_list`.

## Exposed API Surface

- Core metadata utilities: default PV metadata sizing, PE alignment, PV/device size checks, VG status checks, PV addition, LV/PV lookup, segment lookup, LV segment validation/merge/split, LV dependency reverse-link management, sub-LV traversal, segment movement, and readahead calculation.
- Metadata import/export: `export_vg_to_config_tree()`, `import_vg_from_config_tree()`, and `vg_from_config_tree()`.
- Mirror and pool hooks: mirror import fixup; pool attach/detach/create/spare sizing; thin-pool message and metadata sizing functions.
- Library-facing PV accessors: `pv_id()`, `pv_format_type()`, and `pv_vg_id()`.
- MDA/FID helpers: add/remove/index MDA, copy MDA, compare MDA locations, get MDA device, set/get ignored state, and set PV/VG format instances with reference counting.

## Design Notes

- The header separates format-independent metadata graph operations from format-specific disk layout through callback tables. `metadata.c` and format modules communicate through `metadata_area_ops` and `format_handler`.
- Comments emphasize that `format_instance` must be assigned only through `pv_set_fid()` and `vg_set_fid()` because the reference count and destructor behavior are centralized there.
- MDA state is intentionally not owned directly by a PV. The same abstraction can describe raw disk MDAs, file MDAs, or cached scan locations, and the owning list changes between lvmcache and VG format instances.

## Dependencies

The header includes device-cache, LVM string helpers, and `metadata-exported.h`, and it declares types from config trees, lvmcache, format metadata, allocation, devices, logical volumes, physical volumes, and command contexts.

## Risks And Edge Cases

- Many macros directly dereference segment area arrays and assume callers have already validated area type and bounds.
- `BAD_MDA_*` flags are low-level repair policy inputs; misclassifying a bad field can cause either missed repair or unsafe metadata overwrite.
- `format_handler` documents that `vg_write()` must not touch PVs outside the supplied VG, while noting format1 breaks this rule.
- Some declarations are intentionally cross-file internal APIs rather than stable library interfaces; misuse outside the expected metadata transaction flow can bypass validation or reverse-link maintenance.

## Summary

`metadata.h` is the internal ABI for LVM2's metadata subsystem. It defines how formats, metadata areas, PVs, VGs, LV segments, mirror code, pool code, and import/export code plug into the shared in-memory metadata model.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/mirror.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/mirror.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pool_manip.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pool_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/pv.c

## Purpose

`pv.c` is a compact accessor and reporting helper file for LVM2 physical volumes. It exposes PV identity, naming, size, status, metadata-area, usage, and label information, mostly for reporting and external-library style getters, while bridging PV objects to lvmcache metadata-area state.

## Key Responsibilities

- Duplicates report strings for PV format, name, UUID, tags, device ID, and device ID type.
- Returns core PV fields such as ID, format type, VG ID, device pointer, visible VG name, device name, PV size, PE size/start/count, bootloader area start/size, allocated PE count, status, free space, used space, and computed size field.
- Reads current device size through `dev_get_size()`.
- Reports PV metadata-area count, used metadata-area count, minimum MDA size, and minimum MDA free space by consulting lvmcache.
- Classifies PVs as orphan, real PV, missing PV, or used PV based on `vg_name`, status bits, format flags, and PV header extension flags.
- Produces the three-character PV attribute string for duplicate/allocatable/used, exported, and missing status.
- Sets or clears the ignored flag on a PV's metadata areas while keeping lvmcache and VG format-instance MDA lists coherent.
- Returns the cached label for a PV.

## Main Data And APIs

- Public functions include `pv_fmt_dup()`, `pv_name_dup()`, `pv_id()`, `pv_uuid_dup()`, `pv_tags_dup()`, `pv_deviceid_dup()`, `pv_deviceidtype_dup()`, `pv_format_type()`, `pv_vg_id()`, `pv_dev()`, `pv_vg_name()`, `pv_dev_name()`, `pv_size()`, `pv_dev_size()`, `pv_size_field()`, `pv_free()`, `pv_status()`, `pv_pe_size()`, `pv_ba_start()`, `pv_ba_size()`, `pv_pe_start()`, `pv_pe_count()`, `pv_pe_alloc_count()`, `pv_mda_count()`, `pv_mda_used_count()`, `is_orphan()`, `is_pv()`, `is_missing_pv()`, `is_used_pv()`, `pv_attr_dup()`, `pv_mda_size()`, `lvmcache_info_mda_free()`, `pv_mda_free()`, `pv_used()`, `pv_mda_set_ignored()`, and `pv_label()`.
- The file uses a simple `pv_field(handle, field)` macro for field getters, with a FIXME noting that handle validity is not checked.

## Control Flow Notes

- `is_used_pv()` treats any non-orphan PV as used, and for orphan PVs only reports used when the format supports PV flags and the lvmcache PV header extension has `PV_EXT_USED`.
- `pv_attr_dup()` prioritizes duplicate-device status (`d`) over allocatable (`a`), then orphan-used (`u`), then `-`; the second and third characters report exported and missing state.
- `pv_mda_set_ignored()` is simple for orphan PVs, but for non-orphan PVs it prevents disabling all VG metadata areas, then iterates cached PV MDAs and matching VG FID MDAs by location to update ignored bits and move ignored MDAs back to the in-use list when unignoring.
- `lvmcache_info_mda_free()` returns the minimum free space across MDAs that can report free sectors, or zero when no suitable MDA exists.

## Dependencies

This file depends on `metadata.h` helpers, lvmcache lookups and MDA iteration, device helpers, tag formatting, ID formatting, duplicate-device detection, MDA location comparison, and MDA ignored-state setters.

## Risks And Edge Cases

- Most getters directly dereference PV fields and assume a valid PV object, VG pointer, device pointer, and memory pool when needed.
- `pv_name_dup()` and `pv_dev_name()` assume `pv->dev` is non-null; missing PV callers need to avoid these paths or tolerate lower-level behavior.
- `pv_mda_set_ignored()` uses location matching rather than a direct per-PV MDA index; comments note this should be improved.
- `is_used_pv()` returns `-1` on missing cache info, so callers must distinguish error from boolean used/not-used.
- `pv_label()` logs an internal error only for real cached PV expectations; dummy PVs from PV iteration may legitimately have no label.

## Summary

`pv.c` is the PV reporting/accessor layer. It keeps callers away from direct struct-field access for common PV properties and centralizes lvmcache-backed metadata-area accounting and ignored-MDA state changes.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv.c -->