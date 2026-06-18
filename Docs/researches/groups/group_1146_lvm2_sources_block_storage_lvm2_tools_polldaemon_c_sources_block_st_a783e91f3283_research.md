# Group Research: group_1146_lvm2_sources_block_storage_lvm2_tools_polldaemon_c_sources_block_st_a783e91f3283

Scope: `Docs/research_subset_a.md`, specifically `sources/block-storage/lvm2/tools`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/polldaemon.c -->
# File Research: sources/block-storage/lvm2/tools/polldaemon.c

## Purpose

`polldaemon.c` implements the generic polling engine used by LVM2 for long-running copy/synchronization operations, especially `pvmove` and mirror/lvconvert-style work. It supports both classic in-process/background polling and `lvmpolld` daemon-backed polling.

## Main Responsibilities

- Query mirror copy progress via `poll_mirror_progress()`.
- Re-read VG/LV metadata safely while a copy operation progresses.
- Advance multi-segment copy operations through operation-specific callbacks.
- Finish or abort operations through `finish_copy`.
- Poll a specific operation by `poll_operation_id`, or scan all VGs for active pollable LVs.
- Fork a background classic poller when requested.
- Delegate polling to `lvmpolld` when support is compiled in and enabled.

## Key Entry Points

- `poll_daemon()`: public dispatcher. Initializes `daemon_parms`, chooses `lvmpolld` or classic polling, and restricts classic polling to `PVMOVE`.
- `wait_for_single_lv()`: repeatedly locks/reads the target VG, finds the LV, checks active state, polls progress, and runs update/finish callbacks.
- `poll_mirror_progress()`: uses `lv_mirror_percent()` for segment progress and `copy_percent()` for overall progress, returning one of the `PROGRESS_*` states.
- `_check_lv_status()`: central state transition helper for abort, unfinished, segment-finished, and all-finished outcomes.

## Classic Polling Flow

- `_poll_daemon()` optionally daemonizes with `become_daemon()`.
- Child pollers clear inherited `lvmcache` and label-scan state before doing work.
- With an explicit ID, polling calls `wait_for_single_lv()`.
- Without an ID, `_poll_for_all_vgs()` repeatedly calls `process_each_vg()` and `_poll_vg()`.
- `_poll_vg()` first copies stable `poll_operation_id` records for matching LVs, then polls those copied IDs. This avoids mutating the VG/LV list while iterating it.
- `_poll_for_all_vgs()` repeats until no LV reports outstanding unfinished work.

## `lvmpolld` Flow

When `LVMPOLLD_SUPPORT` and `lvmpolld_use()` are active:

- `_lvmpoll_daemon()` dispatches daemon-backed work.
- `_lvmpoll_daemon_id()` initializes daemon polling for one operation and optionally waits in the foreground with `lvmpolld_request_info()`.
- `_lvmpolld_poll_for_all_vgs()` initializes daemon polling for all matching LVs, tracks foreground IDs, and loops until daemon reports completion.
- `_report_progress()` re-reads VG metadata and calls the progress callback, but intentionally avoids taking a VG lock because this path only reports local progress.

## Locking and Metadata Safety

- `wait_for_single_lv()` takes an exclusive `lockd_vg()` lock for lockd VGs because polling may finish the copy and write metadata.
- VG reads that may write on completion use `READ_FOR_UPDATE`.
- If no UUID was supplied, the first successful LV lookup captures the LVID; later iterations reject an LV with the same name but a different LVID.
- Missing VGs/LVs are treated as no longer active or already complete in several non-fatal cases.
- Inactive LVs stop polling because kernel device-mapper status cannot be queried.
- `CONVERTING` is masked out of some LV status checks because it may be derived during metadata import rather than persisted.

## Timing and Interrupt Handling

- `_nanosleep()` temporarily allows SIGINT and reports interruption.
- A zero interval still sleeps at least `WAIT_AT_LEAST_NANOSECS` unless the caller allows zero-time behavior.
- `_sleep_and_rescan_devices()` destroys stale cache state, drops label-scan state, sleeps, and rescans labels.

## Extension Points

The polling behavior is parameterized by `struct poll_functions`:

- `get_copy_name_from_lv`
- `poll_progress`
- `update_metadata`
- `finish_copy`

`pvmove` plugs its own metadata progression and cleanup functions into this generic engine.

## Notable Edge Cases

- Abort mode bypasses progress polling and calls `finish_copy`.
- Background classic poller children call `_exit(lvm_return_code(ret))` and must not return to the normal caller path.
- Daemon-backed abort sets polling interval to zero.
- `devicesfile` is copied into daemon parameters for `lvmpolld`; overly long names are rejected.
- `_copy_poll_operation_id()` requires all ID fields, including UUID, to be present.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/polldaemon.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvchange.c -->
# File Research: sources/block-storage/lvm2/tools/pvchange.c

## Purpose

`pvchange.c` implements `pvchange`, which mutates existing physical volume attributes: allocatability, tags, metadata-ignore state, and PV UUID.

## Main Entry Points

- `pvchange()`: validates command-line options, prepares a processing handle, handles lock/hint setup for UUID changes, and invokes `process_each_pv()`.
- `_pvchange_single()`: applies requested mutations to one PV and commits either VG metadata or standalone PV metadata.

## Supported Mutations

- `--allocatable`: sets or clears `ALLOCATABLE_PV`.
- `--addtag` / `--deltag`: changes PV tags for PVs in tag-capable VGs.
- `--metadataignore`: toggles metadata-area ignore state, optionally prompting when overriding VG metadata-copy preferences.
- `--uuid`: generates a new random PV UUID and updates device metadata plus devices-file state when applicable.

## Safety Checks

- Rejects invocations with no mutation option.
- Requires PV paths, `--all`, or selection.
- Rejects combining `--all` with explicit PV paths.
- Blocks VG changes when duplicate PV devices exist unless configuration allows them.
- Rejects UUID changes when duplicate PVs are present or when the containing VG has active LVs.
- Rejects tag changes on orphan PVs.
- For orphan PVs that appear used by a VG with missing metadata, requires force level `-ff`.
- Converts a shared global lock to exclusive when mutating orphan PVs.

## Metadata Commit Behavior

- Non-orphan PV changes use `vg_write()`, `vg_commit()`, and then `backup(vg)`.
- Orphan PV changes use `pv_write()`.
- UUID changes on non-orphan PVs call `pv_write(cmd, pv, 1)` after saving `pv->old_id`, before committing VG metadata.

## Devices File Integration

For UUID changes:

- `cmd->edit_devices_file` is enabled.
- `pvchange()` takes the global lock exclusively before clearing hints to preserve lock ordering.
- `_pvchange_single()` finds the current devices-file entry with `get_du_for_pvid()`.
- After metadata commit, it replaces the entry PVID and persists with `device_ids_write()`.

## Output and Accounting

`struct pvchange_params` tracks total processed and changed PVs. The command prints a final changed/not-changed summary.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvchange.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvck.c -->
# File Research: sources/block-storage/lvm2/tools/pvck.c

## Purpose

`pvck.c` implements `pvck`, a diagnostic and repair utility for LVM PV on-disk structures. It can inspect labels, PV headers, metadata-area headers, raw metadata locations, current/all metadata text, and can repair label headers, PV headers, and metadata areas.

## Major Modes

- Historical scan/check mode: reports whether LVM labels and text metadata areas are found.
- `--dump headers`: prints label header, PV header, PV header extension, metadata-area headers, and raw location fields.
- `--dump metadata`: dumps current metadata text referenced by the active raw location.
- `--dump metadata_all`: scans a metadata area for all discoverable metadata copies.
- `--dump metadata_area`: writes/dumps an entire metadata area.
- `--dump metadata_search`: searches common or user-specified MDA ranges without trusting headers.
- `--dump backup_to_raw`: converts an LVM backup file into raw text metadata form.
- `--repairtype label_header`: rewrites the label header only.
- `--repairtype pv_header`: rebuilds label/PV header fields.
- `--repairtype metadata`: writes metadata text and MDA headers.
- `--repair`: combined PV-header plus metadata repair.

## Core Data Structures

- `struct settings`: parsed from `--settings`; carries byte offsets/sizes, sequence number, PV UUID, MDA number, device/data sizes, and backup-file path.
- `struct metadata_file`: represents input metadata text, including size, CRC, filename, and extracted VG UUID string.
- `struct devicefile`: wraps a regular file descriptor so dump paths can inspect regular files as well as block devices.

## Read Abstraction

- `get_devicefile()` opens regular files for dump operations.
- `_read_bytes()` dispatches to `dev_read_bytes()` for LVM devices or `lseek()`/`read()` for regular files.
- Repair operations require a real LVM device path, not a regular file.

## Metadata Discovery and Dumping

- `_dump_label_and_pv_header()` reads the label sector, validates label and PV header fields, walks data-area and metadata-area disk location lists, and prints PV header extension bootloader areas.
- `_dump_mda_header()` validates the metadata-area header and raw locations, then optionally dumps current metadata, all metadata copies, or the whole metadata area.
- `_dump_current_text()` reads contiguous or wrapped text metadata, verifies CRC, parses the config tree, extracts VG name and seqno, and prints or writes text.
- `_dump_all_text()` scans 512-byte boundaries in an MDA for plausible `vgname {` metadata starts, validates nearby `id` and `seqno` lines, extracts wrapped metadata copies, calculates CRCs, and warns on parse or termination issues.
- `_dump_search()` infers MDA ranges from headers, defaults, device size, or `--settings`, then scans those ranges without requiring valid headers.

## Validation Logic

- `_check_label_header()` checks label ID, sector, CRC, offset, and type.
- `_check_pv_header()` verifies PV UUID formatting.
- `_check_mda_header()` checks MDA checksum, magic, version, start, and size.
- `_dump_raw_locn()` prints and validates raw metadata location entries, detects wrapped metadata, handles ignored raw locations, and warns when the precommit slot is unexpectedly non-empty.
- `_check_vgname_start()` recognizes plausible starts of raw VG metadata.

## Settings Parsing

`_get_settings()` supports grouped `--settings` options containing key/value pairs. Recognized keys include:

- `metadata_offset`
- `seqno`
- `backup_file`
- `mda_offset`, `mda_size`
- `mda2_offset`, `mda2_size`
- `device_size`
- `data_offset`
- `pv_uuid`
- `mda_num`

All offsets and sizes are in bytes unless explicitly noted in comments.

## Repair: Label Header

`_repair_label_header()`:

- Reads the label sector.
- Warns if no existing LVM label is found.
- Rewrites label ID/type, sector, PV-header offset, and recalculated CRC.
- Honors test mode and prompts unless `--yes` is supplied.
- Writes the full 512-byte label/PV-header sector back to disk.

## Repair: PV Header

`_repair_pv_header()`:

- Determines PV UUID, device size, and data offset from complete `--settings` or from an input metadata file.
- `_get_pv_info_from_metadata()` parses VG metadata and selects the PV by existing PV UUID, user-supplied UUID, or matching device hint.
- Checks that the selected PVID is not present on another device with `label_scan_for_pvid()`.
- Decides whether to include MDA1 and MDA2, using conservative checks to avoid mistakenly writing MDA2 into data space.
- Rebuilds label header, PV header data-area and metadata-area disk locations, PV header extension, and label CRC.
- Logs planned values and writes only after confirmation/test checks.

## Repair: Metadata

`_repair_metadata()`:

- Requires an input metadata file.
- Requires a valid label and metadata-area locations in the PV header.
- Writes to a selected MDA through `mda_num`, or to all existing MDAs by default.
- `_update_mda()` writes metadata text immediately after the MDA header, sets raw location 0, clears raw location 1, calculates the MDA header checksum, then writes text and header.

## Backup and Raw Metadata Handling

- `_backup_file_to_raw_metadata()` strips backup-file preamble/comment formatting and reconstructs raw metadata text with the expected null termination.
- `_dump_backup_to_raw()` reads a backup file specified by `backup_file=...` and prints or writes raw metadata.
- `_read_metadata_file()` accepts raw metadata or backup files, converts backups automatically, appends a null terminator, validates the input, and computes CRC.
- `_check_metadata_file()` rejects common mistakes such as redirected `pvck` stdout or unconverted backup files, warns about unexpected final bytes, and extracts the VG UUID.

## Command Flow

- `pvck()` owns the `metadata_file` lifetime and calls `_pvck_mf()`.
- `_pvck_mf()` parses label-sector and settings options, prepares devices, loads metadata-file input for repairs, sets up bcache/filtering, then dispatches dump, repair, combined repair, or historical scan mode.
- Dump mode can inspect block devices or regular files.
- Repair mode takes the global lock exclusively, clears hints, sets up the target device, and disables hints for the operation.

## Safety Characteristics

- Repair paths are guarded by explicit modes, prompts, and test-mode checks.
- Existing on-disk evidence is used where possible before reconstructing headers.
- MDA2 repair is deliberately cautious because a false positive could overwrite data.
- Input metadata is checked for plausibility before writing.
- The code logs `CHECK:` diagnostics for suspicious but inspectable on-disk fields.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvck.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvcreate.c -->
# File Research: sources/block-storage/lvm2/tools/pvcreate.c

## Purpose

`pvcreate.c` implements `pvcreate`, initializing devices as LVM physical volumes. It also supports PV recreation/recovery from a VG backup file and explicit PV UUID.

## Main Flow

`pvcreate()` builds `struct pvcreate_params` in five stages:

1. Defaults from `pvcreate_params_set_defaults()`.
2. Recovery-related command-line arguments from `_pvcreate_restore_params_from_args()`.
3. Recovery parameters read from a backup file by `_pvcreate_restore_params_from_backup()`.
4. Normal command-line argument parsing via `pvcreate_params_from_args()`.
5. Positional device arguments assigned to `pp.pv_names`.

## Recovery Argument Handling

`_pvcreate_restore_params_from_args()` validates:

- `--restorefile` requires `--uuid`.
- `--uuid` may require `--restorefile` depending on `devices/require_restorefile_with_uuid`, unless `--norestorefile` is used.
- UUID assignment is allowed for exactly one PV.
- Negative `--setphysicalvolumesize` is rejected.
- Supplying `--restorefile` or `--uuid` disables zeroing.

## Backup-Derived Parameters

`_pvcreate_restore_params_from_backup()`:

- Reads a VG backup with `backup_read_vg()`.
- Finds the PV matching the supplied UUID.
- Copies bootloader area start/size, PE start, extent size, and extent count from the backup PV.
- Releases the temporary VG after extracting values.

## Locking and Device State

- `pvcreate()` takes the global lock exclusively because it changes the orphan-PV set.
- It clears the hint file.
- It enables `cmd->create_edit_devices_file`.
- It runs `lvmcache_label_scan()` before processing devices.
- It initializes a processing handle and delegates actual per-device work to `pvcreate_each_device()`.

## Notable Detail

When `--restorefile` is used without an explicit `--metadatasize`, `pvmetadatasize` is set to `pe_start`; later code treats this as a maximum and reduces it to fit.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvcreate.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvdisplay.c -->
# File Research: sources/block-storage/lvm2/tools/pvdisplay.c

## Purpose

`pvdisplay.c` implements legacy/full PV display paths and delegates column output to the `pvs` reporting command.

## Main Entry Points

- `pvdisplay_cmd()`: processes PVs through `_pvdisplay_single()`.
- `pvdisplay_columns_cmd()`: handles report/column mode by calling `pvs()`.
- `pvdisplay()`: defensive stub for missing command-definition wiring; logs an internal error.

## Display Behavior

`_pvdisplay_single()`:

- Computes display size as total PV size for orphan PVs, or free PE space for PVs in VGs.
- With `--short`, prints only the device capacity.
- Warns when the PV belongs to an exported VG.
- Identifies orphan PVs as new physical volumes.
- Uses `pvdisplay_colons()` for colon output or `pvdisplay_full()` for normal full output.
- Prints PV segment maps when `--maps` is set.

## Hints Behavior

In column mode, `pvdisplay_columns_cmd()` disables hints when `--all` is used, because `-a` requires looking at all devices rather than only hinted PVs.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvdisplay.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvmove.c -->
# File Research: sources/block-storage/lvm2/tools/pvmove.c

## Purpose

`pvmove.c` implements `pvmove`, which relocates allocated extents away from a source PV by inserting temporary mirror layers, activating them, then polling until data movement completes.

## Main Data Structure

`struct pvmove_params` tracks:

- Original source PV argument and optional LV-name argument.
- Allocation policy and destination PV list.
- Captured poll identity: LVID, VG name, LV name.
- Whether an operation is already in progress.
- Setup result and whether the source PV was found.

## Command Entry Points

- `pvmove()`: validates environment and arguments, sets up or reads an in-progress pvmove, releases the global lock before long polling, then calls `pvmove_poll()`.
- `pvmove_poll()`: builds a `poll_operation_id` when UUID/VG/LV are known and calls `poll_daemon()` with pvmove callbacks.

## Setup Validation

`pvmove()`:

- Requires the mirror device-mapper target through `_pvmove_target_present()`.
- Requires `lvmpolld` when `lvmlockd` is in use.
- Requires explicit pvmove arguments when `lvmlockd` is in use.
- Parses source PV names, stripping PE-range suffixes after unescaping.
- Handles `--name` by storing the LV name argument.
- Uses shared locking differently for abort mode by setting `cmd->lockd_vg_default_sh`.

## LV Name Handling

`_extract_lvname()` accepts:

- A bare LV name.
- `vg/lv`.
- `/dev/vg/lv`.

It rejects incomplete names and names whose VG does not match the source PV's VG.

## Allocation PV Selection

- `_get_allocatable_pvs()` builds destination candidates from remaining args or all VG PVs.
- It excludes the source PV unless allocation policy is `ALLOC_ANYWHERE`.
- It removes full PVs.
- `_trim_allocatable_pvs()` removes PVs that must be avoided to preserve mirror/RAID redundancy.
- `_remove_sibling_pvs_from_trim_list()` allows RAID data/meta sibling colocation by removing sibling PVs from the avoidance list when moving a specific RAID sub-LV.

## Temporary Mirror Setup

`_set_up_pvmove_lv()`:

- Creates a hidden temporary LV named `pvmove%d`.
- Marks it `PVMOVE | LOCKED`.
- Builds `lvs_changed`.
- Scans top-level RAID/mirror LVs to determine PVs that must be avoided and whether exclusive activation is needed.
- Rejects unsupported cases such as converting/merging LVs, writecache cachevol movement, and RAID with integrity.
- Scans bottom-level striped LVs on the source PV.
- Activates lock holders as needed.
- Inserts pvmove mirror layers with `_insert_pvmove_mirrors()`.
- Adds mirror legs with `lv_add_mirrors()`.
- Splits parent segments for the inserted layer.

## Existing Operation Handling

`_pvmove_setup_single()` detects an existing pvmove LV for the source PV:

- Reports the in-progress operation.
- Ignores remaining command-line arguments.
- Builds `lvs_changed` from LVs using the temporary mirror.
- Determines whether exclusive activation is required.
- Activates the temporary mirror and proceeds to polling.

`_pvmove_read_single()` is used by abort/read paths to find an existing pvmove and capture poll identity.

## Metadata and Activation

- `_update_metadata()` updates/reloads the first changed LV, then ensures the temporary pvmove mirror is active.
- `activate_lvs()` locks and activates all changed LVs before metadata is updated.
- `_copy_id_components()` stores VG/LV names and LVID in pool memory for later polling.

## Poll Integration

`_pvmove_fns` wires pvmove into the generic polling engine:

- `get_copy_name_from_lv = get_pvmove_pvname_from_lv_mirr`
- `poll_progress = poll_mirror_progress`
- `update_metadata = pvmove_update_metadata`
- `finish_copy = pvmove_finish`

## Shared VG Constraints

For shared VGs:

- A named LV is required.
- Internal sanlock LVs cannot be moved.
- The named LV must be locked exclusively through `lockd_lv()`.

## Notable Edge Cases

- Locked LVs are skipped.
- If all relevant data is skipped, setup fails with no data to move.
- `test_mode()` skips actual polling and returns success from `pvmove_poll()`.
- The global lock is released before potentially long polling.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvmove.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvmove_poll.c -->
# File Research: sources/block-storage/lvm2/tools/pvmove_poll.c

## Purpose

`pvmove_poll.c` provides pvmove-specific callbacks used by `polldaemon.c`: advancing pvmove metadata and finishing/cleaning up a completed or aborted pvmove.

## Main Entry Points

- `pvmove_update_metadata()`: advances the mirror to the next segment by calling `lv_update_and_reload()`.
- `pvmove_finish()`: detaches pvmove mirror state, reloads affected LVs, deactivates temporary components, removes the temporary pvmove LV, and commits final VG metadata.

## Mirror Detach Logic

- `_is_pvmove_image_removable()` verifies that a mirror image LV is a valid removable image in the pvmove mirror segment.
- `_detach_pvmove_mirror()` chooses which mirror leg to remove.
- In abort mode with an LV-type first segment, it removes the second mirror leg; otherwise it removes the default first image.
- Detachment is performed through `lv_remove_mirrors()` with the `PVMOVE` flag.

## Finish Flow

`pvmove_finish()`:

- Records the current visible LV count.
- Detaches the temporary pvmove mirror if any LVs were changed.
- Requires `lv_mirr` to have become an error LV before final replacement/reload.
- Calls `lv_update_and_reload()`.
- Refreshes all moved LVs with `activate_pvmoved_lvs()`.
- Synchronizes local device names.
- Deactivates no-longer-used invisible component LVs that have zero open count.
- Deactivates the temporary mirror LV.
- Removes the temporary LV with `lv_remove()`.
- Writes and commits final VG metadata.
- Verifies that visible LV count did not increase, warning about orphan temporary LVs if cleanup failed.

## Safety Notes

- Component LVs are only deactivated after checking `lv_info()` and `open_count`.
- Cleanup failures are treated as aborting errors.
- The final visible-LV count check guards against leaked temporary logical volumes.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvmove_poll.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvmove_poll.h -->
# File Research: sources/block-storage/lvm2/tools/pvmove_poll.h

## Purpose

`pvmove_poll.h` declares the pvmove-specific polling callbacks implemented in `pvmove_poll.c`.

## Contents

The header forward-declares:

- `struct cmd_context`
- `struct dm_list`
- `struct logical_volume`
- `struct volume_group`

It declares:

- `pvmove_update_metadata()`: callback for advancing pvmove metadata after a segment finishes.
- `pvmove_finish()`: callback for final pvmove cleanup and VG commit.

## Role

This header provides the narrow interface between `pvmove.c` and `pvmove_poll.c`, allowing `pvmove.c` to populate `struct poll_functions` without exposing the implementation details of mirror detachment and cleanup.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvmove_poll.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvremove.c -->
# File Research: sources/block-storage/lvm2/tools/pvremove.c

## Purpose

`pvremove.c` implements `pvremove`, clearing LVM physical-volume metadata from one or more devices.

## Main Flow

`pvremove()`:

- Requires at least one physical volume path.
- Initializes `struct pvcreate_params` with defaults.
- Sets `pp.is_remove = 1`, force level, yes count, PV count, and PV names.
- Takes the global lock exclusively because it changes the orphan-PV set.
- Allows `pvremove -ff` to continue if the global lock cannot be taken.
- Clears hints.
- Runs `lvmcache_label_scan()`.
- Disables lockd VG locking for forced clearing with `-ff`.
- Delegates actual per-device removal to `pvcreate_each_device()`.

## Implementation Reuse

`pvremove` intentionally uses the same toollib path as `pvcreate`; the `is_remove` flag changes validation and execution from create behavior to remove behavior.

## Safety Notes

- Normal operation requires the global lock.
- `-ff` is an explicit override path that can skip locking and lockd VG checks.
- The command destroys the processing handle before returning.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvremove.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvresize.c -->
# File Research: sources/block-storage/lvm2/tools/pvresize.c

## Purpose

`pvresize.c` implements `pvresize`, resizing or refreshing one or more physical volumes.

## Main Data Structure

`struct pvresize_params` stores:

- `new_size`: requested PV size in bytes, or zero for auto-detect/update.
- `done`: number of PVs resized/updated.
- `total`: number of PVs processed.

## Main Flow

`pvresize()`:

- Requires at least one PV argument.
- Rejects negative `--setphysicalvolumesize`.
- Initializes counters and requested size.
- Calls `set_pv_notify(cmd)`.
- Creates a processing handle and stores `pvresize_params` in `custom_handle`.
- Calls `process_each_pv()` with `READ_FOR_UPDATE`.
- Prints resized/updated vs not-resized summary.

## Per-PV Behavior

`_pvresize_single()`:

- Validates the custom handle.
- Increments total count.
- Converts the global lock to exclusive for orphan PVs, because resizing an orphan changes orphan PV state.
- Calls `pv_resize_single()` with the requested size and `--yes` count.
- Increments done count on success.

## Safety Notes

- Uses VG update reads because resizing may change metadata.
- Orphan PVs get explicit global-lock escalation.
- The processing handle is destroyed on all exit paths.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvresize.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/pvscan.c -->
# File Research: sources/block-storage/lvm2/tools/pvscan.c

## Purpose

`pvscan.c` implements PV discovery/display and the `pvscan --cache` event path used for online PV tracking, VG completeness detection, and event-based autoactivation.

## Major Command Paths

- `pvscan_display_cmd()`: traditional display/listing of physical volumes.
- `pvscan_cache_cmd()`: cache/update path used by udev/system events and manual `pvscan --cache`.
- `pvscan()`: defensive command-definition stub that logs an internal error if wired directly.

## Display Mode

`_pvscan_display_single()` filters exported or orphan/no-VG PVs based on options, updates totals, and calls `_pvscan_display_pv()`.

`_pvscan_display_pv()` supports:

- Short output with just the PV device name.
- Optional UUID display.
- `--allpvs` output including devices-file ID type/name when devices files are enabled.
- Orphan, exported, and normal VG PV formatting.
- Running totals for all PVs, in-use PVs, and no-VG PVs.

When `--allpvs` is used, display mode disables device-id filtering and hints so all devices can be considered.

## Online File Model

The cache path uses runtime files under online directories:

- `PVS_ONLINE_DIR`: one file per online PVID, containing major/minor and VG/device names.
- `PVS_LOOKUP_DIR`: one file per VG listing PVIDs in that VG.
- `VGS_ONLINE_DIR`: one file per VG used to serialize autoactivation ownership.

Supporting helpers:

- `_online_pvid_file_remove_devno()` removes online PVID records when a device disappears and only major/minor is known.
- `_online_files_remove()` clears an online directory.
- `_write_lookup_file()` writes the PVID list for a VG.
- `_count_pvid_files()` checks online status using VG metadata.
- `_count_pvid_files_from_lookup_file()` checks online status for a PV that lacks metadata by using a prior lookup file.

## VG Completeness Detection

`_online_devs()` is the core event scanner:

- Iterates scanned devices.
- Looks up lvmcache info by PVID.
- Skips unused PV headers.
- Reads VG metadata from MDA1 or MDA2 when available.
- Verifies the PV belongs to the read VG.
- Performs extra MD-component checks when size/device hints suggest risk.
- Ignores shared, foreign, and exported VGs for autoactivation.
- Creates PVID online files in `--cache` mode.
- Checks whether all PVs for a VG are online.
- Writes lookup files for multi-PV VGs so later metadata-less PV arrivals can still determine completeness.
- Adds complete VG names to the activation list.
- Supports listing VG/LV completion state for udev-oriented callers.

## Autoactivation

`_pvscan_aa()` autoactivates complete VGs:

- Uses `online_vg_file_create()` so only one concurrent pvscan owns activation for a VG.
- Uses a quick path when exactly one VG is complete and `saved_vg` is available.
- Falls back to `process_each_vg()` for the slow path.
- Skips clustered, exported, and shared VGs in `_pvscan_aa_single()`.
- Activates with `vgchange_activate(cmd, vg, CHANGE_AAY, 1, NULL)`.

## Quick Autoactivation Path

`_pvscan_aa_quick()` avoids broad device scanning:

- `_get_devs_from_saved_vg()` uses saved VG metadata plus PVID online files to build the exact device list.
- It locks the VG before scanning those devices.
- It destroys stale cache state and scans only the selected devices.
- It reads the VG with `READ_WITHOUT_LOCK | READ_FOR_ACTIVATE`.
- It verifies that the devices found match the VG's PV list.
- It then runs autoactivation.

This optimization reduces scan overhead when many PVs appear concurrently.

## `pvscan --cache` With All Devices

`_pvscan_cache_all()`:

- Clears online PV, VG, and lookup files.
- Removes searched-devname records.
- Enables hint recreation.
- Runs a full `lvmcache_label_scan()`.
- Builds a device list from the filtered device iterator.
- Calls `_online_devs()` in all-devices mode.

## `pvscan --cache` With Arguments

`_pvscan_cache_args()`:

- Sets `expect_missing_vg_device`.
- Uses special online-autoactivation device setup to avoid scanning unrelated devices.
- Parses positional args as `/dev/...` paths or `major:minor`, and grouped `--major --minor`.
- Sets up devices for those args without initial filters.
- Removes online files for missing major/minor device-removal events.
- Applies nodata filters first.
- Handles devices-file matching and a relaxed device-id filter mode when devname IDs or refresh triggers require PVID-based matching.
- Adds aliases from `DEVLINKS` or scans `/dev` so regex filters can match udev-created symlinks.
- Reads labels with `label_read_pvid()`, drops non-LVM devices, then applies full filters.
- Uses `label_scan_devs_cached()` to populate lvmcache from already-read label data.
- Calls `_online_devs()` and invalidates hints if PVs were found.

## Udev and Event Activation

`pvscan_cache_cmd()`:

- Disables device listing/info from udev because pvscan itself populates udev information.
- Honors `global/event_activation`.
- Suppresses completion reporting for `--checkcomplete` when event activation is disabled, including `LVM_EVENT_ACTIVATION=0` for udev output.
- Supports `--autoactivation event`; unknown values cause the command to skip work.
- Treats no device arguments and no major/minor args as the all-devices cache path.
- After cache processing, autoactivates complete VGs only if `-aay` was requested.
- Calls `sync_local_dev_names()` after activation.

## LV/VG Listing Support

Within `_online_devs()`:

- `--listvg` can print unknown, complete, incomplete, or finished VG state.
- `--udevoutput` prints `LVM_VG_NAME_COMPLETE=...` or `LVM_VG_NAME_INCOMPLETE=...` in a form suitable for udev import.
- `--listlvs` can list LVs using the arriving PV.
- If VG completeness is unknown and the PV lacks metadata, LV listing is not possible.
- Partial LV detection uses `vg_mark_partial_lvs()` when the VG is incomplete.

## Notable Safety and Race Handling

- Lookup-file creation is race-tolerant: concurrent pvscans race to create the file, and the winner writes it.
- After writing a lookup file, the code rechecks PVID online files to close a race with another pvscan checking the lookup file before it was complete.
- VG online files serialize actual activation so multiple pvscans do not activate the same VG concurrently.
- The quick activation path validates device identity against the VG read after scanning.
- Device removal by major/minor removes associated online and lookup/VG completion state.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/pvscan.c -->