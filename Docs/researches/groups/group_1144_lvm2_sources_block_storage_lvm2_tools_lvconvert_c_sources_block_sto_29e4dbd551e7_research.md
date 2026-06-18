# Group Research: group_1144_lvm2_sources_block_storage_lvm2_tools_lvconvert_c_sources_block_sto_29e4dbd551e7

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvconvert.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvconvert.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvconvert_poll.c -->
# File Research: sources/block-storage/lvm2/tools/lvconvert_poll.c

This file contains helper routines used by `lvconvert.c` polling and merge completion. It is separated from the large command file but still implements core finalization behavior for mirror conversion and snapshot/thin merge.

Main functions:
- `lvconvert_mirror_finish()` finishes mirror conversion polling. If the LV still has `CONVERTING`, it collapses the temporary mirrored sync layer with `collapse_mirrored_lv()`, clears `CONVERTING`, reloads metadata with `lv_update_and_reload()`, and reports completion.
- `swap_lv_identifiers()` swaps two logical volumes’ identifiers, allocation policy, read-ahead, profile, major/minor numbers, timestamps, hostnames, tags, and names. It uses a temporary rename to `pvmove_tmeta` to avoid name collision, then completes the name swap.
- `thin_merge_finish()` uses `swap_lv_identifiers()` so the merge result takes the intended identity, preserves status, and removes the old merge LV with `lv_remove_single()`.
- `lvconvert_merge_finish()` finalizes snapshot merge polling. For thin snapshots it clears snapshot merge state and calls `thin_merge_finish()`. For classic snapshots it removes the COW LV merged into the origin.
- `poll_merge_progress()` reports classic snapshot merge progress. It treats no-longer-merging origins as complete, checks snapshot percent, handles invalidated/failed merge values, and displays `100 - percent` as progress.
- `poll_thin_merge_progress()` checks thin snapshot merge completion by comparing device IDs and returns finished after a single successful check because thin snapshot merge is immediate from this polling perspective.

Important behavior:
- The code assumes the caller has selected the right poll function set for mirror conversion, classic merge, or thin merge.
- `swap_lv_identifiers()` is a powerful metadata mutation helper used by conversion paths; it swaps more than UUID/name and includes tags and persistent device numbers.
- Thin merge completion removes the previous origin after swapping identities, while classic merge completion removes the COW snapshot.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvconvert_poll.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvconvert_poll.h -->
# File Research: sources/block-storage/lvm2/tools/lvconvert_poll.h

This header declares the polling and merge-finalization helpers implemented in `lvconvert_poll.c` and used by `lvconvert.c`.

Declarations:
- Forward declarations for `cmd_context`, `logical_volume`, and `volume_group`.
- Includes `lib/lvmpolld/polldaemon.h` for `progress_t`, `daemon_parms`, and polling callback types.
- Declares:
  - `lvconvert_mirror_finish()`
  - `swap_lv_identifiers()`
  - `thin_merge_finish()`
  - `lvconvert_merge_finish()`
  - `poll_merge_progress()`
  - `poll_thin_merge_progress()`

Role:
- This is the small public interface between the main `lvconvert` command logic and its polling completion helpers.
- It intentionally exposes only conversion/merge finalization and progress callbacks, not the larger command-dispatch machinery.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvconvert_poll.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvcreate.c -->
# File Research: sources/block-storage/lvm2/tools/lvcreate.c

This file implements `lvcreate` command parsing, validation, size calculation, VG processing, and final delegation to the common LVM LV creation library. It supports standard linear/striped LVs, mirrors, RAID, snapshots, thin volumes/pools, cache volumes/pools, VDO volumes/pools, and helper flows that create an LV then attach cache/writecache using `lvconvert` functions.

Core data flow:
- `struct lvcreate_cmdline_params` stores raw command-line size, virtual size, percent mode, and PV arguments before VG-dependent conversion.
- `struct processing_params` passes `lvcreate_params` plus command-line parameters through `process_each_vg()`.
- `_lvcreate_params()` is the main command-line parser. It selects the segment type, validates compatible option sets, reads zero/wipe settings, parses names, sizes, stripes, pool/cache/VDO/mirror/RAID options, allocation policy, and tags.
- `_lvcreate_single()` runs after opening the VG. It reads activation settings, resolves ambiguous snapshot/cache/pool cases, performs final VG-dependent validation and extent calculations, prepares lockd state, then calls `lv_create_single()`.

Name and syntax parsing:
- `_lvcreate_name_params()` resolves VG name, LV name, pool name, origin name, and ambiguous positional syntax.
- Cache creation syntax is special: a positional `vg/lv` can mean an existing cache pool or an origin that should be cached, and `_determine_cache_argument()` decides after the VG is open.
- Snapshot syntax distinguishes classic COW snapshots from thin snapshots in `_determine_snapshot_type()`.
- Pool-style commands allow `--name` to name the pool and guard against the same name being used for both pool and LV.

Size and extent handling:
- `_read_size_params()` enforces mutually exclusive `--size` and `--extents`, rejects invalid negative/zero values, and allows size omission only for snapshots/thin cases where another rule supplies meaning.
- `_update_extents_params()` converts sizes and percentages into extents after the VG is known. It handles `%VG`, `%FREE`, `%PVS`, `%ORIGIN`, mirror image division, stripe-boundary rounding, snapshot COW maximum sizing, VDO maximum pool size, and pool metadata reservation.
- Pool creation updates thin/cache pool metadata extents and chunk sizes using `update_thin_pool_params()` or `update_cache_pool_params()`.

Segment-specific validation:
- Mirror and RAID parsing is split across `_read_mirror_params()`, `_read_raid_params()`, and `_read_mirror_and_raid_params()`.
- RAID validation enforces minimum stripes, RAID10 mirror/stripe rules, RAID6 `--nosync` prohibition, recovery rate ordering, RAID0/RAID4/RAID10 target feature support, region-size minimums, and optional RAID integrity settings.
- Thin validation ensures a consistent final state among thin LV, thin pool, snapshot, origin, and pool parameters.
- Cache validation reads cache mode, policy, metadata format, and settings.
- VDO validation reads target settings, handles pool header sizing near maximum virtual size, and checks VDO constraints after extents are known.
- `_check_zero_parameters()` disables or rejects zeroing when the target cannot be zeroed, the LV is read-only/inactive/activation-skipped, or an origin is involved.

Pool handling:
- `_check_pool_parameters()` validates pool-only options, pool name existence, pool type compatibility, persistent major/minor restrictions for pools, and whether pool metadata options are legal.
- For pool creation, `_lvcreate_single()` ensures a pool metadata spare with `handle_pool_metadata_spare()` before calling `lv_create_single()`, and removes a newly created spare on failure when possible.

Activation and locking:
- `_read_activation_params()` parses activation mode, error-when-full behavior, readahead with page-size alignment, persistent major/minor, activation-skip flags, and autoactivation.
- `_lvcreate_single()` uses `lockd_lvcreate_prepare()` and `lockd_lvcreate_done()` around `lv_create_single()`.

Create-and-attach helpers:
- `_lvcreate_and_attach_cmd()` creates a normal linear/striped LV while ignoring the user-visible `--type`, then attaches a cache or writecache by calling a supplied attach function.
- `lvcreate_and_attach_writecache_cmd()` reuses `lvconvert_writecache_attach_single()`.
- `lvcreate_and_attach_cache_cmd()` reuses `lvconvert_cachevol_attach_single()`.
- If attach fails, `_lvcreate_and_attach_single()` deactivates and removes the newly created LV with dependencies.

Important implementation notes:
- The parser uses explicit option allowlists/disallowlists per segment type, making this file the first line of defense against unsupported combinations.
- Many decisions are deferred until VG open because existing LV names and types determine whether syntax means pool creation, cache attachment, classic snapshot, or thin snapshot.
- `lvcreate.c` does not itself implement low-level allocation; it normalizes and validates user intent, then delegates to metadata/library helpers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvcreate.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvdisplay.c -->
# File Research: sources/block-storage/lvm2/tools/lvdisplay.c

This file implements the `lvdisplay` command variants.

Functions:
- `_lvdisplay_colon_single()` skips hidden LVs unless `--all` is set, then prints colon-format output with `lvdisplay_colons()`.
- `_lvdisplay_general_single()` skips hidden LVs unless `--all` is set, prints full LV details with `lvdisplay_full()`, and prints segment maps with `lvdisplay_segments()` when `--maps` is set.
- `lvdisplay_colon_cmd()` processes target LVs with `_lvdisplay_colon_single()`.
- `lvdisplay_general_cmd()` processes target LVs with `_lvdisplay_general_single()`.
- `lvdisplay_columns_cmd()` delegates column output to `lvs()`.
- Generic `lvdisplay()` is an internal-error fallback for missing command-definition dispatch.

Behavior:
- The file is a thin command wrapper around shared display functions.
- Hidden/internal LVs are filtered by default and shown only with `--all`.
- Column-mode output is intentionally delegated to the reporting command implementation rather than duplicated here.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvdisplay.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvextend.c -->
# File Research: sources/block-storage/lvm2/tools/lvextend.c

This file is a minimal command wrapper for `lvextend`.

Function:
- `lvextend()` directly calls `lvresize_cmd(cmd, argc, argv)`.

Role:
- `lvextend` shares implementation with the general LV resize command path.
- All option parsing, validation, allocation, filesystem resize handling, and metadata updates are handled by `lvresize_cmd()` elsewhere.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvextend.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/lvm-static.c -->
# File Research: sources/block-storage/lvm2/tools/lvm-static.c

This file provides the entry point for the statically linked LVM binary.

Functions:
- `main()` calls `init_is_static(1)` to mark the process as static, then delegates all command-line handling to `lvm2_main(argc, argv)`.
- `lvm_shell()` is provided as a stub returning `0`, with unused parameters marked, presumably because the static build does not provide interactive shell support here.

Role:
- This is not command logic; it is build/entry-point glue for the static executable.
- It includes `tools.h` and `lvm2cmdline.h`, then relies on the shared LVM command-line dispatcher.
- Licensing differs from most command files in this group: this file states GPL v2, while the other listed LVM command files state LGPL v2.1.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/lvm-static.c -->