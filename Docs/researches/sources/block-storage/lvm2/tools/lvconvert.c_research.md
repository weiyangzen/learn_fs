# File Research: sources/block-storage/lvm2/tools/lvconvert.c

This is the main `lvconvert` command implementation. It contains the command entry points and most of the orchestration for converting existing LVM logical volumes between segment types and roles: mirror/RAID reshapes, snapshot split/merge, thin/cache pool creation or metadata swapping, cache/writecache attach/detach, VDO conversion, repair, replacement, and RAID integrity changes.

Key structures and dispatch:
- `struct lvconvert_params` stores parsed command state for mirror/RAID conversions, including requested type, mirror counts, striping, region size, allocation policy, PV list, polling state, and split names.
- `conversion_type_t` currently distinguishes only `CONV_SPLIT_MIRRORS` from `CONV_OTHER`; comments show it is a partial migration away from many separate booleans.
- `_read_params()` parses common legacy mirror/RAID conversion options such as `--type`, `--mirrors`, `--splitmirrors`, `--trackchanges`, `--mirrorlog`, `--corelog`, stripes, region size, force/yes, and background polling behavior.
- Public command entry points are split by command definition, while generic `lvconvert()` is intentionally an internal-error fallback if a command definition lacks a specific function.

Polling integration:
- `_create_id()` builds a `poll_operation_id` from VG/LV names and UUID.
- `_lvconvert_poll_by_id()` selects mirror-conversion polling or snapshot/thin-merge polling and calls `poll_daemon()`.
- `lvconvert_poll()` exposes polling for a specific LV and detects whether the LV is a merging origin.
- Conversion commands collect `convert_poll_id_list` entries and run polling after `process_each_lv()` releases normal processing context.

Mirror conversion and repair:
- `_lvconvert_mirrors_parse_params()` derives old/new mirror image and log counts, handles relative mirror counts, split-mirror restrictions, default log counts, region size preservation, and multi-segment mirror rejection.
- `_lvconvert_mirrors_aux()` performs linear-to-mirror conversion, mirror image increases using a temporary sync layer, mirror image reductions, split mirrors, and mirror log changes.
- `mirror_remove_missing()` removes failed mirror images/logs and can remove an LV if all images are unusable under force.
- `_lvconvert_mirrors_repair()` implements the two-stage repair flow: remove failed devices, then optionally replace mirror images/logs using policies or prompts.
- Mirror code relies heavily on metadata helpers such as `lv_add_mirrors()`, `remove_mirror_log()`, `add_mirror_log()`, `lv_remove_mirrors()`, `lv_split_mirror_images()`, `lv_update_and_reload()`, and temporary mirror-layer helpers.

RAID conversion:
- `_lvconvert_raid()` handles RAID image-count changes, RAID split/trackchanges, RAID level conversion, mirror/striped/linear transitions through RAID conversion helpers, RAID0/RAID4/RAID10 target feature checks, and RAID integrity restrictions.
- `_lvconvert_raid_types()` resolves the target segtype, checks device-mapper target availability, parses stripe parameters, redirects cache/VDO-pool cases to data sub-LVs, and dispatches to `_convert_mirror()`, `_convert_raid()`, or `_convert_striped()`.
- `_raid_split_image_conversion()` blocks operations on RAID tracking LVs or tracked RAID subvolumes.
- `_raid4_conversion_supported()` validates kernel support for RAID4 conversions.

Snapshot flows:
- `_lvconvert_splitsnapshot()` separates a classic COW snapshot from its origin, rejecting virtual origins and shared VGs.
- `_lvconvert_snapshot()` converts an existing LV into a classic snapshot exception store for a named origin, after validation, warning, deactivate, optional zeroing, and `vg_add_snapshot()`.
- `_lvconvert_merge_old_snapshot()` starts classic snapshot merge into an origin, including open-device delay logic and snapshot-merge target checks.
- `_lvconvert_merge_thin_snapshot()` handles thin snapshot merge; if both origin and snapshot can be deactivated, it completes by swapping identifiers and removing the old origin via `thin_merge_finish()`, otherwise marks merge-on-activation.
- `lvconvert_merge_cmd()` multiplexes `--merge` across classic snapshots, thin snapshots, and RAID mirror-image merge.

Thin/cache pool repair and metadata handling:
- `_lvconvert_thin_pool_repair()` runs configured `thin_repair` using the current metadata LV as input and pool metadata spare as output, optionally validates transaction ID using `thin_dump`, then swaps repaired metadata into the pool and keeps the old metadata as a backup LV.
- `_lvconvert_cache_repair()` performs the analogous cache metadata repair with configured `cache_repair`.
- `_lvconvert_swap_pool_metadata()` swaps an existing visible LV into a thin/cache pool as metadata, checks type restrictions, deactivates the new metadata LV, optionally changes chunk size with force/prompt rules, and swaps identifiers/locks.
- Both repair paths manage `_pmspare`, activation skip flags, read-only backup metadata, and shared-VG lock details.

Pool and thin conversion:
- `_lvconvert_to_pool()` is the central conversion routine for turning an LV into a thin pool, cache pool, or fully provisioned thin volume. It validates metadata LVs, computes pool metadata/chunk settings, warns for destructive metadata wiping, allocates metadata when needed, handles `_pmspare`, inserts hidden `_tdata`/`_cdata` layers, applies thin/cache pool segment parameters, manages lockd state, commits metadata, and optionally reactivates pools.
- `_lvconvert_insert_thin_layer()` converts the original LV into a thin LV backed by a newly inserted pool-data-like layer before pool construction.
- `_lvconvert_to_thin_with_external()` creates a thin LV using an existing LV as read-only external origin, then swaps identifiers so the new thin LV takes the original name/id.
- `lvconvert_to_pool_or_swap_metadata_cmd()` handles ambiguous `--thinpool/--cachepool` syntax by deciding whether to create a pool or swap metadata in an existing pool.

Cache and writecache:
- `_cache_vol_attach()` attaches a cachevol LV to an origin by renaming the fast LV with `_cvol`, creating cache metadata, and updating/reloading the cache LV.
- `_cache_pool_attach()` attaches an existing cache pool to an origin.
- `_lv_create_cachevol()` can create a cachevol from one or more `--cachedevice` PVs, requiring `--cachesize` for tags or already-used PVs.
- `_lvconvert_split_cache_single()` handles `--splitcache`/`--uncache` for cache, cachepool, writecache, thin-pool data, and VDO-pool data redirection.
- `_lvconvert_detach_writecache()` starts writecache detach, using cleaner mode when possible; if cleaning is long-running it records a poll id and defers completion.
- `_lvconvert_detach_writecache_when_clean()` repeatedly reopens the VG, checks dirty writecache blocks, and completes detach/removal once clean.
- `lvconvert_writecache_attach_single()` attaches writecache by validating/creating a cachevol, choosing a safe 512/4096 writecache block size using PV logical block sizes and filesystem block size, warning about memory use, wiping the fast LV, renaming it to `_cvol`, inserting `_wcorig`, and reloading.

VDO and integrity:
- `_lvconvert_to_vdopool_single()` converts a supported visible writable LV into a VDO pool and creates the virtual VDO LV, with destructive-formatting warnings and VDO parameter validation.
- `_lvconvert_check_vdopool_lv()` blocks unsupported source types, read-only/hidden/virtual/origin/external-origin LVs, and RAID with integrity.
- `_lvconvert_integrity_add()` and `_lvconvert_integrity_remove()` add or remove dm-integrity from RAID LVs using optional integrity settings and PV allocation lists.
- `lvconvert_integrity_cmd()` allows missing PV handling so integrity can be removed from partial RAID LVs.

Important implementation notes:
- Many paths are intentionally destructive and use prompts unless `--yes` is set: snapshot exception-store conversion, pool metadata wiping, cache metadata reuse, writecache no-flush detach, VDO formatting, and cachevol erasure.
- Shared VG/lvmlockd support is threaded through conversion paths using `lockd_lv()`, `lockd_vg()`, saved `lock_args`, and explicit lock freeing after role changes.
- Hidden internal LV naming conventions are central: `_tdata`, `_tmeta`, `_cdata`, `_cmeta`, `_pmspare`, `_corig`, `_wcorig`, `_cvol`, and mirror sync layers.
- Error handling is strongest before VG metadata commit. Several comments explicitly note that after the main conversion commit, later activation/unlock/spare failures may require manual intervention rather than rollback.
- This file depends on broad LVM metadata, activation, device-mapper target, polling, cache, thin, RAID, VDO, and locking APIs provided elsewhere in the LVM2 tree.
