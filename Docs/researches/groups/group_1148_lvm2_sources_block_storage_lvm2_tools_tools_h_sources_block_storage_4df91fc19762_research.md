# Group Research: group_1148_lvm2_sources_block_storage_lvm2_tools_tools_h_sources_block_storage_4df91fc19762

Scope verified against `Docs/research_subset_a.md`: `sources/block-storage/lvm2` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/tools.h -->
# File Research: sources/block-storage/lvm2/tools/tools.h

## Purpose
`tools.h` is the shared front-door header for LVM2 command implementations under `tools/`. It pulls together command framework headers, metadata/activation/cache/locking/device/display helpers, and declares the command entry points and option/value access APIs used by individual command files.

## Main Constructs
- Include guard `LVM_TOOLS_H` wraps the file (`lines 16-17`, `254`).
- Includes command framework and major library surfaces: errors/tool/toollib, activation, archiver, cache, lvmlockd, config, device/device_id, display, metadata, locking, exec/file/signal/string, segtypes, lists, toolcontext, notify, and hints (`lines 19-47`).
- Defines command parser sizing constants `CMD_LEN` and `MAX_ARGS` (`lines 51-52`).
- Uses an X-macro include of `commands.h` to declare every command function as `int command(struct cmd_context *, int argc, char **argv)` (`lines 56-59`).
- Defines argument behavior flags such as countable, groupable, noninteractive, and long-option marker (`lines 61-64`).
- `struct arg_values` stores normalized parsed option values in string, signed/unsigned integer, 64-bit, sign, percent, and count forms (`lines 66-75`).
- `struct arg_value_group_list` groups per-priority option values for groupable command options (`lines 77-81`).

## API Surface
- Argument verifier/normalizer declarations cover booleans, activation, cache, discard, mirror log, sizes, extents, permissions, metadata types, units, segment types, allocation, locking, readahead, metadata copies, poll operations, write-mostly, sync actions, report/config/repair/dump/headings values (`lines 85-129`).
- Argument query helpers expose whether an option is valid/set, counts, values in typed forms, grouped values, and force handling (`lines 131-157`).
- Command name lookup and common command helpers include polling, mirror missing removal, VG activation/background polling, and specialized `vgchange` subcommands (`lines 158-179`).
- Metadata lookup helpers retrieve option/value names, LV properties/types, and command definitions (`lines 180-184`).
- Declares specialized command entry points for `lvchange`, `lvdisplay`, `pvdisplay`, `vgdisplay`, `lvconvert`, `lvcreate` attach modes, `pvscan`, and resize/extend policy paths (`lines 186-252`).

## Dependencies And Interactions
- `vals.h` relies on parser functions declared here, e.g. `yes_no_arg`, `activation_arg`, `segtype_arg`, and `locktype_arg`.
- Command implementations in this group include `tools.h` and depend on its shared command context, arg accessors, processing iterators, metadata helpers, and lock/activation declarations.
- The X-macro command declaration pattern ties `commands.h` definitions directly to C function prototypes.

## Notable Design Details
- The header intentionally centralizes broad LVM2 tool dependencies, so individual command files can include a single tool umbrella.
- Argument values are normalized into `struct arg_values`, avoiding repeated command-local parsing.
- Grouped arguments are first-class through `arg_value_group_list`, used by commands such as `vgcreate` for repeated `--addtag` handling.

## Risks / Caveats
- Because this is an umbrella header, changes can have wide rebuild and namespace impact across many command files.
- The X-macro prototype generation depends on `commands.h` maintaining compatible command names and signatures.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/tools.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vals.h -->
# File Research: sources/block-storage/lvm2/tools/vals.h

## Purpose
`vals.h` defines LVM2 command value types using a `val(a, b, c, d)` X-macro. These entries describe values accepted by options and positional arguments, linking enum names to parser functions, command-definition names, and usage text.

## Main Constructs
- Introductory comments document the value model: value types are shared by options and positional command definitions, and improve validation and usage output (`lines 2-95`).
- `val()` fields are documented as enum, parser function, command-definition reference name, and usage display string (`lines 41-47`).
- The file enumerates standard scalar values: none, bool, number, signed/plus-only number, uint32, string, VG/LV/PV names, tags, and command-definition-only select (`lines 97-108`).
- Specialized value types cover activation, cache metadata/mode, discard behavior, mirror log location, sizes, extents, permissions, metadata type, units, segment type, allocation policy, lock type, readahead, metadata copies, poll operation, write-mostly PV, sync action, report/config/repair/dump/headings types, and const command-definition values (`lines 109-162`).
- `VAL_COUNT` is explicitly last (`lines 163-164`).

## Conditional Behavior
- Lock type usage strings are compiled from supported lock managers:
  - `LOCKDSANLOCK_SUPPORT` contributes `sanlock|` (`lines 131-135`).
  - `LOCKDDLM_SUPPORT` contributes `dlm|` (`lines 136-140`).
  - `LOCKDIDM_SUPPORT` contributes `idm|` (`lines 141-145`).
  - The final lock type string always includes `none` (`line 146`).

## Dependencies And Interactions
- Parser function names correspond to declarations in `tools.h`, e.g. `yes_no_arg`, `activation_arg`, `cachemode_arg`, `extents_arg`, `locktype_arg`, and `headings_arg`.
- `args.h` option definitions reference these `_VAL` enum identifiers.
- Command definitions reference the string names, e.g. `VG`, `LV`, `SizeMB`, `LockType`, which are translated to enum values during command definition processing.

## Notable Design Details
- The comments explicitly call out that accepted specialized strings are not centrally stored; parser functions and implementation code may still need coordinated updates (`lines 56-66`).
- Usage strings may intentionally show only common or recommended accepted values, not every legacy or obscure parser-accepted value (`lines 68-80`).
- Size usage strings prefer concise lower-case default-unit examples such as `Size[k|UNIT]` and `Size[m|UNIT]` rather than listing every unit (`lines 82-94`, `115-120`).

## Risks / Caveats
- Adding a new accepted value to a specialized type can require updates in three places: this usage string, the parser function, and command implementation logic.
- Some values use generic `string_arg`, so validation may be deferred to command-specific code.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vals.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgcfgbackup.c -->
# File Research: sources/block-storage/lvm2/tools/vgcfgbackup.c

## Purpose
Implements `vgcfgbackup`, which writes backup copies of VG metadata either through normal backup infrastructure or to a user-specified file/template.

## Main Functions
- `_expand_filename()` expands a filename template with the VG name unless `security_level()` is active, in which case it copies the template literally (`lines 18-35`).
- `_expand_filename()` rejects backing multiple VGs into the same expanded path and tells the user to use `%s` for the VG name (`lines 37-40`), then stores the expanded path in `last_filename` (`lines 42-46`).
- `_vg_backup_single()` is the per-VG callback used by `process_each_vg` (`lines 49-81`).
- `vgcfgbackup()` creates a processing handle, stores a stack `last_filename` buffer in `handle->custom_handle`, sets missing-PV and unknown-segment handling flags, processes each VG, destroys the handle, and returns the aggregate result (`lines 83-109`).

## Behavior
- With `--file`, the callback expands the filename and calls `backup_to_file(last_filename, vg->cmd->cmd_line, vg)` (`lines 55-61`).
- Without `--file`, it refuses normal backup if the VG has missing PVs or unknown segments, because the default backup path may not be safe/complete (`lines 63-70`).
- For normal backup it enables forced backup with `backup_enable(cmd, 1)` and calls `backup(vg)` (`lines 72-75`).
- On success it prints `Volume group "<name>" successfully backed up.` (`line 78`).

## Dependencies And Interactions
- Uses `process_each_vg` for selection/iteration (`lines 104-105`).
- Uses archive/backup helpers from the LVM metadata archive layer.
- Uses `cmd->handles_missing_pvs` and `cmd->handles_unknown_segments` so the command can read VGs with these conditions and emit command-specific guidance (`lines 96-102`).

## Risks / Caveats
- `last_filename` is stack storage passed through the processing handle; this is safe only because processing is synchronous within `vgcfgbackup()`.
- User-supplied filename templates use `dm_snprintf` as a format string when security level permits, so the command relies on controlled expected `%s` use and Coverity annotation (`lines 31-32`).
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgcfgbackup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgcfgrestore.c -->
# File Research: sources/block-storage/lvm2/tools/vgcfgrestore.c

## Purpose
Implements `vgcfgrestore`, restoring VG metadata from archive/backup data and guarding against restoring while LVs from the VG are active.

## Main Functions
- `_check_all_dm_devices()` lists device-mapper devices and counts active devices belonging to the target VG (`lines 25-74`).
- `vgcfgrestore()` validates arguments, supports archive listing mode, checks for active volumes, locks the VG, scans labels, and invokes restore helpers (`lines 76-159`).

## Behavior
- Accepts exactly one VG name unless `--list` and `--file` are both set (`lines 82-91`).
- Validates the VG name after stripping the device directory (`lines 82-87`).
- In `--list` mode, displays either a specific archive file or archive list for the VG and exits successfully (`lines 93-105`).
- Before restoring, `_check_all_dm_devices()` scans `DM_DEVICE_LIST`, splits LVM device names with `dm_split_lvm_name`, and reports matching active LVs (`lines 34-69`).
- If active volumes are found, it warns, explains metadata mismatch risk, and prompts unless `--yes` is set (`lines 110-123`).
- Takes global exclusive and VG write locks before restore (`lines 125-131`).
- Clears hints, runs `lvmcache_label_scan`, sets `cmd->handles_unknown_segments`, and restores from file or default archive based on `--file` (`lines 133-146`).
- Unlocks the VG on both failure and success paths (`lines 136-156`).

## Dependencies And Interactions
- Directly uses libdevmapper task APIs (`dm_task_create`, `dm_task_run`, `dm_task_get_names`, `dm_task_destroy`) via `libdm` includes (`lines 17-18`, `34-73`).
- Uses archive helpers `archive_display_file`, `archive_display`, `backup_restore_from_file`, and `backup_restore`.
- Uses LVM locking and cache scan infrastructure before metadata write/restore operations.

## Risks / Caveats
- The active-volume scan matches by split device-mapper name and has a TODO about validating the `LVM-` UUID prefix as well (`line 53`).
- If active-device checking fails, the command only warns and continues (`lines 110-112`).
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgcfgrestore.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgchange.c -->
# File Research: sources/block-storage/lvm2/tools/vgchange.c

## Purpose
Implements `vgchange` and its specialized subcommands: general VG metadata changes, activation/deactivation, monitoring/polling, refresh, autoactivation setup, lock type conversion, lock start/stop, system ID changes, persistent reservation operations, PR setting changes, and lock-argument updates.

## Main Structures
- `struct vgchange_params` carries lock-start counters, whether sanlock was involved, whether VG completeness is required for activation, and root DM UUID state for root-VG device import (`lines 21-26`).

## Activation, Monitoring, And Polling
- `_monitor_lvs_in_vg()` registers or unregisters active LVs with dmeventd, skipping inactive and pvmove LVs (`lines 31-59`).
- `_poll_lvs_in_vg()` starts background polling for active pvmove/converting/merging LVs (`lines 61-84`).
- `_activate_lvs_in_vg()` iterates visible/component LVs, skips snapshots, mirror internals, VDO pools, activation-skip LVs, autoactivation-filter failures, and `LV_NOAUTOACTIVATE`, then calls `lv_change_activate()` (`lines 86-163`).
- `_vgchange_monitoring()` updates monitoring state only when LVs are active and monitoring is not ignored (`lines 165-180`).
- `vgchange_background_polling()` starts polling when global background polling is enabled (`lines 182-196`).

## `vgchange_activate`
- Rejects activation of foreign VGs when local and VG system IDs differ (`lines 207-218`).
- Honors `NOAUTOACTIVATE` for autoactivation (`lines 220-223`).
- Optionally requires a complete VG before activation by checking every PV has a device (`lines 225-232`).
- Coordinates activation with persistent reservation start for `--persist start`, disallowing that mode on shared VGs (`lines 234-250`).
- Allows missing PV handling for activation and partial activation (`lines 252-256`).
- On deactivation, invalidates LV label scan state and refuses deactivation if visible LVs are open/in use (`lines 258-274`).
- For activation, checks current backup and monitors already-active LVs when requested (`lines 276-293`).
- Calls `_activate_lvs_in_vg()` and then optionally stops PR after complete deactivation for `--persist stop` (`lines 295-310`).
- Can trigger root-VG system.devices auto-import by creating `DEVICES_IMPORT_PATH` when the active VG matches the root DM UUID and auto-import marker exists (`lines 312-347`).
- Prints the active LV count at the end (`lines 349-352`).

## Metadata Change Helpers
- `_vgchange_refresh()` refreshes visible LVs (`lines 355-363`).
- `_vgchange_alloc()`, `_vgchange_resizeable()`, `_vgchange_autoactivation()`, `_vgchange_logicalvolume()`, `_vgchange_physicalvolumes()`, and `_vgchange_pesize()` update allocation policy, resizeable status, autoactivation flag, max LV/PV counts, and extent size (`lines 365-479`).
- `_vgchange_addtag()` and `_vgchange_deltag()` delegate tag changes to `change_tag()` (`lines 481-489`).
- `_vgchange_uuid()` requires inactive LVs, creates a new VG UUID, updates LV LVIDs, and updates device IDs for PVs stacked on LVs (`lines 491-520`).
- `_vgchange_metadata_copies()` changes preferred metadata copy count, warning if unchanged (`lines 523-545`).
- `_vgchange_profile()` attaches or detaches metadata profiles (`lines 547-572`).
- `_vgchange_system_id()` validates and changes VG system ID with warnings/prompts when making the VG foreign or removing ownership protection (`lines 574-640`).

## Lock Start/Stop Support
- `_passes_lock_start_filter()` checks config lists that restrict which shared VGs may have lockspaces started (`lines 642-678`).
- `_vgchange_lock_start()` skips non-shared VGs, applies lock-start filters unless forced, starts PR if needed, verifies PR is started when required, starts the VG lockspace, and tracks wait status (`lines 680-726`).
- `_vgchange_lock_stop()` stops the VG lockspace and optionally stops PR (`lines 728-738`).

## General `vgchange`
- `_vgchange_single()` dispatches set options through a static table, writes/commits VG metadata when changed, then handles activation, refresh, monitor, or poll actions (`lines 740-817`).
- The autoactivation comment block documents first-boot root VG devices-file generation using `auto-import-rootvg`, `/run/lvm/lvm-devices-import`, and `vgimportdevices --rootvg --auto` (`lines 819-876`).
- `_get_rootvg_dev()` checks whether root-VG auto-import should be considered and obtains the root DM UUID (`lines 877-893`).
- `_vgchange_autoactivation_setup()` handles `--autoactivation event`, event activation config, online PV scanning, early VG locking optimization, complete-VG detection, and fallback to full scanning (`lines 895-1030`).
- `vgchange()` validates option combinations, separates update vs non-update operations, handles partial VG safety flags, PR activation/deactivation rules, active foreign VG inclusion for deactivation, lock mode defaults, autoactivation setup, boot-time monitor behavior, read flags, processing handle setup, and `process_each_vg()` dispatch (`lines 1032-1220`).

## Lock Type Subcommand
- `_vgchange_locktype()` handles lock type transitions and recovery:
  - Forced `--locktype none --lockopt force` strips cluster/lock metadata (`lines 1229-1239`).
  - Rejects no-op changes and direct lockd-to-lockd conversion (`lines 1248-1261`).
  - Requires inactive LVs (`lines 1273-1277`).
  - Converts from `clvm` or lockd types to `none`, freeing lockd metadata when needed (`lines 1279-1306`).
  - Converts to lockd types, preparing LV lock args and handling sanlock’s two-stage lock LV allocation (`lines 1308-1382`).
  - Converts to `none` and restores local system ID (`lines 1385-1390`).
- `_vgchange_locktype_single()` brackets locktype change with PR finish/start handling, writes/commits metadata, deactivates sanlock LV after conversion, and reports success (`lines 1396-1438`).
- `vgchange_locktype_cmd()` handles forced recovery prompts/disable flags, requires lvmlockd otherwise, optionally takes global lock for cache validation, and processes VGs for update (`lines 1440-1510`).

## Lock Start/Stop Subcommand
- `_vgchange_lock_start_stop_single()` calls lock start or stop based on selected option (`lines 1512-1527`).
- `vgchange_lock_start_stop_cmd()` requires lvmlockd, configures lock behavior for start/stop, processes VGs, and waits for lock-start completion unless nowait/autonowait is set (`lines 1529-1593`).

## System ID Subcommand
- `_vgchange_systemid_single()` optionally requires a majority of PVs, changes system ID, coordinates PR start/stop with ownership transfer, writes/commits metadata, and reports success (`lines 1595-1678`).
- `vgchange_systemid_cmd()` enables missing-PV handling for majority checks and bypasses PR-required reads when `--persist start` must be performed inside the callback (`lines 1680-1708`).

## Persistent Reservation Subcommands
- `_vgchange_persist_single()` supports PR actions `check`, `read`, `start`, `stop`, `remove`, `clear`, and `autostart` (`lines 1710-1787`).
- `start` protects shared VGs from unexpectedly disrupting other hosts when lockspaces are busy and PR is not required (`lines 1727-1755`).
- `stop` refuses active LVs unless forced (`lines 1756-1762`).
- `clear` prompts unless `--yes` is set (`lines 1766-1773`).
- `vgchange_persist_cmd()` includes foreign VGs for `check/read`, disables lvmlockd VG locking around PR operations, and reads with `READ_FOR_PERSIST` to serialize local PR commands (`lines 1789-1828`).

## PR Settings And Lock Args
- `_vgchange_setpersist_single()` validates local PR key/host ID, blocks automated/required PR for root VG, tests PR access on PV devices, validates lock args compatibility, prevents unsafe PR enablement while shared lockspaces are busy, optionally starts PR before enabling settings, updates `vg->pr`, writes/commits, and rolls back PR start on write failure (`lines 1830-1949`).
- `vgchange_setpersist_cmd()` sets `READ_FOR_UPDATE`, bypasses PR-required reads, and adds `READ_FOR_PERSIST` when combined with `--persist` (`lines 1951-1970`).
- `_vgchange_setlockargs_single()` delegates lock-argument changes to `lockd_setlockargs()`, writes/commits, and releases upgraded PR if held (`lines 1973-2001`).
- `vgchange_setlockargs_cmd()` processes VGs for update (`lines 2003-2018`).

## Dependencies And Interactions
- Heavily depends on activation, lvmlockd, persistent reservation, device ID, hint, metadata write/commit, process iterator, and config subsystems.
- Coordinates with `vgimportdevices` through the root-VG auto-import trigger path.
- Uses command framework argument accessors from `tools.h` throughout.

## Risks / Caveats
- `vgchange.c` has many mode-specific safety gates; changing option validation can affect activation, metadata mutation, PR, and lock manager behavior simultaneously.
- PR ordering is critical: several paths intentionally bypass read-time PR checks only because they start/stop PR inside the command.
- Root-VG auto-import creates an external trigger file, so activation can have systemd/device-file side effects.
- Lock type conversion, especially sanlock, is multi-stage and sensitive to partially written metadata or interrupted operations.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgchange.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgck.c -->
# File Research: sources/block-storage/lvm2/tools/vgck.c

## Purpose
Implements `vgck`, checking VG metadata consistency and optionally rewriting metadata to repair/update metadata areas.

## Main Functions
- `_update_metadata_single()` rewrites and commits VG metadata, then attempts to write the same metadata to bad metadata areas (`lines 24-72`).
- `_update_metadata()` enables missing-PV, outdated-PV wiping, and unknown-segment handling, then processes VGs for update (`lines 74-82`).
- `vgck_single()` validates a VG and fails if it has missing PVs (`lines 84-99`).
- `vgck()` chooses update-metadata mode when `--updatemetadata` is set, otherwise runs validation mode (`lines 101-108`).

## Behavior
- Metadata update relies on `vg_write()` to correct old metadata copies, wipe outdated PVs, fix PV header flags/versions, strip historical LVs, and clear missing PV flags on unused PVs (`lines 30-37`).
- Calls `preserve_text_fidtc()` before `vg_commit()` so `vg_write_commit_bad_mdas()` can reuse the same text metadata buffer for bad metadata areas (`lines 43-63`).
- Frees preserved text metadata with `free_text_fidtc()` (`lines 65-69`).
- Validation mode calls `vg_validate()` and then rejects VGs with missing PVs (`lines 89-96`).

## Dependencies And Interactions
- Includes `lib/format_text/format-text.h` for text metadata preservation and bad-MDA write support (`line 17`).
- Uses `process_each_vg()` for normal and update flows.

## Risks / Caveats
- Comments explicitly note that some corruption types still cannot be repaired, including label header, PV header/location, and some MDA header fields (`lines 19-22`).
- Update mode writes metadata and can alter on-disk state; normal validation mode does not.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgck.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgcreate.c -->
# File Research: sources/block-storage/lvm2/tools/vgcreate.c

## Purpose
Implements `vgcreate`, creating a new VG from one or more PV paths, including PV initialization, VG metadata initialization, tags, persistent reservation settings, and shared-lock startup.

## Flow
- Requires at least a VG name and PVs (`lines 30-34`).
- Splits the first argument as `vg_name`; remaining args become PV names (`lines 36-38`).
- Initializes and populates `pvcreate_params`, setting PV count/names, VG name, `preserve_existing = 1`, and block-size consistency checking (`lines 40-49`).
- Initializes default and argument-derived `vgcreate_params`, validates them, then takes global file and lockd create locks (`lines 51-63`).
- Clears hints, locks the new VG name, and runs a label scan before creating PVs so existing VG name conflicts are detected first (`lines 65-95`).
- Enables devices-file creation/editing (`line 84`).
- Initializes a processing handle, runs `pvcreate_each_device()`, then unlocks the devices file (`lines 97-109`).
- Creates the in-memory VG, applies profile/default metadata settings, sets extent size, max LV/PV, allocation policy, system ID, metadata copies, and PR persistence flags (`lines 111-124`).
- Applies `NOAUTOACTIVATE` when requested (`lines 126-127`).
- Attaches PVs with `vg_extend_each_pv()` (`lines 129-131`).
- Handles repeated grouped `--addtag` values (`lines 141-154`).
- Writes and commits VG metadata (`lines 156-158`).
- Initializes lock args for shared VG lock types with `lockd_init_vg()`; on failure removes PVs/direct VG state (`lines 160-171`).
- Unlocks VG, reports success, and starts shared VG lockspace if applicable (`lines 173-207`).
- Releases VG and processing handle on success or failure (`lines 208-217`).

## Dependencies And Interactions
- Uses `pvcreate_params_*`, `vgcreate_params_*`, `vg_create`, `vg_set_*`, `vg_extend_each_pv`, `vg_write`, and `vg_commit`.
- Uses devices-file support through `cmd->create_edit_devices_file` and `unlock_devices_file()`.
- Uses persistent reservation support through `vg_set_persist()` and `persist_vgcreate_update()`.
- Uses lvmlockd create/start/init functions for shared VGs.

## Notable Design Details
- Existing VG name detection is done before PV creation to avoid modifying devices when the requested VG name is already present (`lines 67-95`).
- Shared VG creation writes the VG initially as local, then `lockd_init_vg()` writes it again with lock metadata (`lines 160-165`).
- Shared lockspace start may wait unless `LOCKOPT_NOWAIT` is set (`lines 197-205`).

## Risks / Caveats
- Failure after PV creation but before final VG setup relies on cleanup paths in `bad:`.
- The command touches both VG metadata and device-file state, so ordering around `unlock_devices_file()` is important.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgcreate.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgdisplay.c -->
# File Research: sources/block-storage/lvm2/tools/vgdisplay.c

## Purpose
Implements `vgdisplay` command variants: colon output, general/full/short output, and column output delegated to `vgs`.

## Main Functions
- `_vgdisplay_colon_single()` optionally filters to active VGs, then calls `vgdisplay_colons()` (`lines 18-28`).
- `_vgdisplay_general_single()` optionally filters to active VGs, supports short output, full output, verbose LV/PV display, and backup freshness checking (`lines 30-56`).
- `vgdisplay_colon_cmd()` rejects `-A` with explicit VG names and processes VGs with the colon callback (`lines 58-66`).
- `vgdisplay_general_cmd()` performs the same `-A` argument check and processes VGs with the general callback (`lines 68-76`).
- `vgdisplay_columns_cmd()` delegates to `vgs()` (`lines 78-81`).
- `vgdisplay()` is an internal-error fallback for missing command-definition function mapping (`lines 83-88`).

## Behavior
- `-A` / active volume groups mode is only valid without explicit VG arguments (`lines 60-63`, `70-73`).
- Verbose general display lists full LV info and short PV info after the VG summary (`lines 44-51`).
- `check_current_backup(vg)` is called for general display (`line 53`).

## Dependencies And Interactions
- Relies on display helpers `vgdisplay_colons`, `vgdisplay_short`, `vgdisplay_full`, `lvdisplay_full`, and `pvdisplay_short`.
- Uses `process_each_vg`, `process_each_lv_in_vg`, and `process_each_pv_in_vg`.

## Risks / Caveats
- The plain `vgdisplay()` function should not be reached for valid command definitions; reaching it indicates command table misconfiguration.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgdisplay.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgexport.c -->
# File Research: sources/block-storage/lvm2/tools/vgexport.c

## Purpose
Implements `vgexport`, marking a VG and its PVs as exported after ensuring it is inactive and safe to move/import elsewhere.

## Main Functions
- `vgexport_single()` validates and modifies one VG (`lines 19-70`).
- `vgexport()` validates command-line shape and processes selected VGs for update (`lines 72-86`).

## Behavior
- Refuses to export a VG with active logical volumes (`lines 27-31`).
- For shared VGs, attempts to take exclusive LV locks on lock-using LVs to ensure they are inactive on all hosts, then unlocks them (`lines 33-48`).
- Sets `EXPORTED_VG` on the VG, clears `system_id`, and sets `EXPORTED_VG` on each PV (`lines 50-54`).
- Writes and commits the VG (`lines 56-57`).
- If `--persist stop` is supplied, attempts `persist_stop()` and warns on failure (`lines 59-62`).
- Requires explicit VG names, `--select`, or `-a`; rejects combining `-a` with names or selection (`lines 74-82`).

## Dependencies And Interactions
- Includes persistent reservation support (`line 17`).
- Uses lvmlockd LV locks for shared VG safety.
- Uses `process_each_vg(... READ_FOR_UPDATE ...)`.

## Risks / Caveats
- PR stop failure is warning-only after export metadata is committed (`lines 59-62`).
- Shared VG checks depend on lockd being able to confirm LV inactivity across hosts.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgexport.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgextend.c -->
# File Research: sources/block-storage/lvm2/tools/vgextend.c

## Purpose
Implements `vgextend`, adding PVs to an existing VG or restoring missing PVs back into a VG.

## Main Structures
- `struct vgextend_params` wraps `struct pvcreate_params` for callback use (`lines 19-21`).

## Main Functions
- `_restore_pv()` finds a named PV in the VG and clears its `MISSING_PV` flag when appropriate (`lines 23-53`).
- `_vgextend_restoremissing()` applies `_restore_pv()` to requested PVs, writes/commits if at least one was restored, and reports success (`lines 55-79`).
- `_vgextend_single()` performs normal VG extension with new PVs (`lines 81-128`).
- `vgextend()` parses arguments, prepares PV creation parameters, handles locking/scanning/device-file editing, and dispatches the right callback (`lines 130-204`).

## Behavior
- Requires VG name and physical volumes (`lines 139-143`).
- Uses `skip_dev_dir()` for the VG name and remaining args as PV names (`lines 145-147`).
- Initializes PV creation params from args, sets `preserve_existing = 1`, and forces `pp->force = PROMPT` because pvcreate within vgextend cannot be forced (`lines 149-162`).
- Takes global exclusive lock, clears hints, enables devices-file editing, and runs label scan (`lines 163-171`).
- For normal extension, runs `pvcreate_each_device()` before processing the VG (`lines 178-183`).
- Sets `cmd->handles_missing_pvs = 1` because adding PVs is allowed even when existing PVs are missing (`lines 187-193`).
- Normal extension calls `vg_extend_each_pv()`, starts PR on new devices if the VG requires/autostarts PR, optionally adjusts metadata-copy preference when `--metadataignore` changes used MDA count, writes/commits, and reports success (`lines 90-125`).
- Restore-missing mode only clears missing state for existing PVs and commits the VG (`lines 64-78`).

## Dependencies And Interactions
- Uses pvcreate helper stack, devices-file locking, LVM cache label scan, VG write/commit, and PR extension support (`persist_start_extend`).
- Uses `process_each_vg(... READ_FOR_UPDATE | PROCESS_SKIP_SCAN ...)` after the explicit scan (`lines 197-199`).

## Risks / Caveats
- `--metadataignore` can prompt and adjust VG metadata copy policy based on current MDA usage (`lines 90-116`).
- Restore-missing requires the PV to be found in the VG and have an associated device; otherwise it only warns.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgextend.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgimport.c -->
# File Research: sources/block-storage/lvm2/tools/vgimport.c

## Purpose
Implements `vgimport`, clearing exported state from VGs/PVs and optionally setting local ownership/system ID and starting persistent reservations.

## Main Functions
- `_vgimport_single()` imports one exported VG (`lines 19-70`).
- `vgimport()` validates command line and processes VGs for update (`lines 72-112`).

## Behavior
- Requires a VG name, selection, or `-a`; rejects combining `-a` with names/selection (`lines 74-82`).
- With `--force`, allows missing PVs and warns, enabling repair workflows for partial exported VGs (`lines 84-98`).
- If `--persist start` is present, disables PR-required read checks because PR will be started before writing in the callback (`lines 100-108`).
- Callback rejects VGs that are not exported and rejects partial VGs unless `--force` allowed them through (`lines 27-35`).
- Clears `EXPORTED_VG` on the VG (`line 37`).
- For non-shared VGs, sets `vg->system_id` to the local command system ID when available (`lines 39-44`).
- Starts/updates persistent reservation inclusion before clearing exported state from PVs (`lines 46-52`).
- Writes/commits metadata, reports success, and invalidates hints (`lines 54-64`).

## Dependencies And Interactions
- Includes hint support to invalidate stale hint data after importing moved/shared disks (`line 17`, `line 64`).
- Uses `persist_start_include()` when PR start is involved.
- Uses `process_each_vg(... READ_FOR_UPDATE ...)`.

## Risks / Caveats
- `--force` is intentionally not default because importing a partial VG could mask forgotten disks (`lines 84-95`).
- Hint invalidation is defensive for unconventional disk sharing scenarios.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgimport.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgimportclone.c -->
# File Research: sources/block-storage/lvm2/tools/vgimportclone.c

## Purpose
Implements `vgimportclone`, importing a cloned set of VG devices by giving the clone a new VG name and regenerated VG/PV UUIDs so it can coexist with the original.

## Main Structures
- `struct vgimportclone_params` stores the list of new devices, base/old/new VG names, and flags for importing devices and exported VG state (`lines 19-26`).

## `_update_vg`
- Rejects exported VGs unless `--import` is specified (`lines 40-43`).
- Rejects partial VGs (`lines 45-48`).
- Checks that every PV has a device and that none of the clone devices are used by active LVs (`lines 50-67`).
- Ensures the provided device list exactly matches the PVs in the VG; missing or extra devices fail (`lines 69-97`).
- Optionally clears exported status, generates a new VG UUID, saves `old_name`, renames the VG, clears shared lock type/args, sets local system ID, and clears PR settings (`lines 99-122`).
- For each PV, prepares a write-list entry, updates VG name, optionally clears exported status, stores old PV ID, generates a new PV ID, updates the device PVID, and adds to `vg->pv_write_list` (`lines 123-144`).
- Updates each LV LVID to the new VG ID and clears LV lock args (`lines 146-149`).
- Adds device IDs before VG write when importing devices or when devices file is enabled (`lines 151-163`).
- Writes and commits VG metadata (`lines 165-166`).

## Device Scanning Flow
- `_get_other_devs()` builds a list of scan-eligible devices excluding the clone devices (`lines 173-200`).
- `vgimportclone()` initializes lists, PR bypass, global locking, hints, devices-file editing, and device setup (`lines 202-242`).
- When `--importdevices` is requested, it only remains active if devices file support is enabled and the devices file exists; otherwise it is ignored (`lines 244-259`).
- The command first resolves explicit device args using nodata filters (`lines 261-281`), wipes filter results, scans the new devices with full filters (`lines 283-300`), and rejects devices excluded by filters (`lines 302-313`).
- It verifies all scanned clone devices appear to be from the same VG name via lvmcache (`lines 315-349`).
- It invalidates clone-device cache entries, scans all other devices, collects existing VG names, and chooses a unique new VG name from `--basevgname` or old VG name plus numeric suffix (`lines 351-455`).
- It invalidates other-device cache entries, locks both new and old VG names, rescans clone devices read/write, reads the old VG from clone devices, and calls `_update_vg()` (`lines 457-510`).
- Writes the devices file if needed and unlocks devices file on exit (`lines 512-527`).

## Dependencies And Interactions
- Uses low-level device cache/filter/label scan flows directly rather than only `process_each_vg`, because duplicate cloned metadata conflicts with existing VG metadata.
- Uses lvmcache invalidation to alternate between viewing clone devices and other devices.
- Uses device ID management to add cloned devices to the devices file before writing VG metadata.

## Risks / Caveats
- The command must import all PVs in the cloned VG together; partial clone imports are rejected.
- It forcibly turns a cloned shared VG into a local VG and clears PR settings because clone devices may not share the original lock/PR environment (`lines 115-121`).
- Name selection is race-sensitive in theory, but the command holds global/VG locks around the final update.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgimportclone.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgimportdevices.c -->
# File Research: sources/block-storage/lvm2/tools/vgimportdevices.c

## Purpose
Implements `vgimportdevices`, scanning VGs and adding their PV devices to the LVM devices file, with support for root-VG auto-import and optional foreign/shared VG handling.

## Main Structures
- `struct vgimportdevices_params` tracks number of added devices, root-VG match state, root DM UUID, and root VG name (`lines 22-27`).

## Per-VG Callback
- `_vgimportdevices_single()` optionally filters to the root VG by comparing root DM UUID payload with VG ID (`lines 42-47`).
- Skips VGs with missing PVs, printing the missing PVID (`lines 49-56`).
- Allows importing devices for foreign/shared VGs but avoids updating their VG metadata (`lines 58-68`).
- For each PV, adds a device ID using the PV device, PVID, and existing device ID type; increments added count on success (`lines 70-88`).
- If local metadata updates are allowed and PVs were updated, writes device IDs into VG metadata; failure is non-fatal and only prints a message (`lines 90-98`).

## Root-VG Auto Import Helpers
- `_get_rootvg_dev()` implements `--auto` skip logic: skip if devices file already exists or if `auto-import-rootvg` marker does not exist (`lines 103-139`).
- It sets `cmd->device_ids_auto_import` so `device_ids_write()` can annotate the auto-generated devices file (`lines 127-132`).
- `_clear_rootvg_auto()` removes the auto-import marker and runtime import trigger file (`lines 141-153`).

## Command Flow
- Includes foreign VGs when `--foreign` is set and always includes shared VGs (`lines 191-195`).
- Handles missing PVs to allow command-specific warnings (`lines 196-197`).
- For `--rootvg`, obtains the root VG DM UUID or skips if auto-import is not enabled (`lines 199-210`).
- Takes global file lock, prepares the devices file, requires devices-file support, locks the devices file, and creates it if missing (`lines 212-239`).
- Clears hint file only when using the default/system devices file (`lines 241-246`).
- Sets filter behavior so import is not limited by an existing devices file: skip device-id filter, use regex filter, and create/edit devices file (`lines 254-267`).
- Disables lockd global/VG locking so shared VGs can be bootstrapped into the devices file before lockstart can find them (`lines 268-277`).
- Processes VGs for update and adds devices in callback (`lines 279-291`).
- Fails if no devices were added, writes the devices file, reports count, clears root auto markers when appropriate, and removes a newly created devices file on failure (`lines 300-324`).

## Dependencies And Interactions
- Uses `device_id_add()` and `device_ids_write()` for devices-file state.
- Interacts with root-VG auto-import flow triggered by `vgchange -aay --autoactivation event`.
- Includes activation header for root VG device UUID helper (`line 18`) and `<sys/file.h>` for devices-file locking compatibility (`lines 19-20`).

## Risks / Caveats
- Updating VG metadata with device IDs is explicitly non-critical; command success is based on devices-file write.
- Shared VG import disables lvmlockd locks intentionally, relying on the fact that shared VG metadata is not updated in this mode.
- If the command creates the devices file and later fails, it attempts to unlink that file (`lines 320-322`).
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgimportdevices.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgmerge.c -->
# File Research: sources/block-storage/lvm2/tools/vgmerge.c

## Purpose
Implements `vgmerge`, merging one or more source VGs into a destination VG.

## Main Functions
- `_vgmerge_vg_read()` reads a VG for update and rejects shared VGs (`lines 18-34`).
- `_vgs_are_compatible_for_merge()` requires source VG LVs to be inactive and delegates compatibility checks to `vgs_are_compatible()` (`lines 36-50`).
- `_vgmerge_select_pool_metadata_spare()` keeps the larger pool metadata spare LV when both VGs have one and retests compatibility (`lines 52-73`).
- `_vgmerge_single()` merges one source VG into the destination (`lines 75-240`).
- `vgmerge()` validates args, takes global lock, clears hints, and merges each source argument into the first VG (`lines 242-271`).

## Merge Flow
- Rejects identical destination/source names (`lines 86-89`).
- Runs label scan and locks VGs in lexicographic order to reduce lock-order deadlock risk (`lines 91-112`).
- Removes one pool metadata spare if both VGs have one, preserving the larger (`lines 114-126`).
- Requires matching PR settings (`lines 128-133`).
- Checks compatibility and archives both VGs before moving structures (`lines 135-143`).
- Moves all PVs from source to destination, updates PV VG name, and marks PVs as `PV_MOVED_VG` (`lines 146-154`).
- Resolves duplicate LV ID second components by generating new IDs for source LVs when needed (`lines 156-179`).
- Moves LVs and metadata areas from source VG lists to destination VG lists (`lines 181-203`).
- Preserves pool metadata spare pointer when needed, updates extent/free counts, records old name, handles pool metadata spare sizing, writes/commits destination VG, backs it up, and reports success (`lines 205-230`).
- Releases destination before source because destination references moved elements (`lines 231-239`).

## Dependencies And Interactions
- Uses metadata list operations (`del_pvl_from_vgs`, `add_pvl_to_vgs`, `lv_set_vg`, `dm_list_move`).
- Uses archive/backup before and after metadata mutation.
- Uses pool metadata spare management and PR setting checks.

## Risks / Caveats
- Shared VGs are unsupported (`lines 27-31`).
- Source LVs must be inactive.
- Release order is mandatory after moving source elements into destination (`lines 232-237`).
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgmerge.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgmknodes.c -->
# File Research: sources/block-storage/lvm2/tools/vgmknodes.c

## Purpose
Implements `vgmknodes`, ensuring device nodes exist for LVs, optionally refreshing visible LVs first.

## Main Functions
- `_vgmknodes_single()` handles one LV (`lines 18-33`).
- `vgmknodes()` handles global setup and iterates LVs (`lines 35-43`).

## Behavior
- If `--refresh` is set and the LV is visible, calls `lv_refresh()` and then `sync_local_dev_names()` (`lines 21-27`).
- Calls `lv_mknodes()` for each LV (`lines 29-30`).
- If udev sync support is unavailable, calls `lv_mknodes(cmd, NULL)` once before iterating LVs (`lines 37-40`).
- Processes each LV with VG read lock mode `LCK_VG_READ` (`line 42`).

## Dependencies And Interactions
- Uses activation/device node helpers `lv_refresh`, `sync_local_dev_names`, and `lv_mknodes`.
- Iterates through `process_each_lv()`.

## Risks / Caveats
- Refresh failures are fatal for that LV.
- Non-udev fallback creates nodes globally before per-LV processing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgmknodes.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgreduce.c -->
# File Research: sources/block-storage/lvm2/tools/vgreduce.c

## Purpose
Implements `vgreduce`, removing PVs from a VG or repairing a VG by removing missing PVs and affected partial LVs.

## Main Structures
- `struct vgreduce_params` tracks force, whether repair fixed anything, and whether the VG was already consistent (`lines 18-22`).

## Main Helpers
- `_remove_pv()` refuses to remove the last PV, refuses allocated PVs, adjusts VG free/extent counts, removes the PV from VG lists, and frees PV format instance data (`lines 24-51`).
- `_consolidate_vg()` warns about partial LVs, instructs force repair commands, and removes empty missing PVs when possible (`lines 53-83`).
- `_make_vg_consistent()` enables partial activation, repeatedly marks partial LVs, repairs RAID/mirror missing components when possible, removes visible partial LVs when forced, then consolidates missing PVs (`lines 85-148`).
- `_vgreduce_single()` calls library `vgreduce_single()` for a specific PV after checking VG write/resizeable status (`lines 150-165`).
- `_vgreduce_repair_single()` handles `--removemissing` repair for one VG and commits the resulting metadata (`lines 167-190`).

## Command Flow
- Validates required VG/PV arguments and combinations of `--removemissing`, `--mirrorsonly`, and `-a` (`lines 201-231`).
- Splits first arg as VG name and remaining args as PV paths (`lines 233-235`).
- Takes global exclusive lock, clears hints, initializes processing handle, and stores params (`lines 237-246`).
- Normal mode processes each PV in the target VG for update (`lines 248-255`).
- Repair mode sets force count, enables missing-PV handling, ignores suspended devices during repair, processes the VG, and reports already-consistent/fixed/failure (`lines 258-278`).
- Restores previous suspended-device ignore setting and destroys handle on exit (`lines 279-283`).

## Dependencies And Interactions
- Uses LV repair/removal helpers `lv_raid_remove_missing`, `mirror_remove_missing`, and `lv_remove_with_dependencies`.
- Uses `process_each_pv()` for normal PV removal and `process_each_vg()` for repair.
- Uses metadata write/commit after repair consolidation.

## Risks / Caveats
- Forced repair can remove partial visible LVs and dependencies.
- `--mirrorsonly` is only valid with `--removemissing` and blocks non-mirror partial LV removal.
- Temporarily changes global suspended-device handling and restores it at exit.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgreduce.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgremove.c -->
# File Research: sources/block-storage/lvm2/tools/vgremove.c

## Purpose
Implements `vgremove`, removing entire VGs, including contained LVs, pool metadata spare, persistent reservation cleanup, lockd cleanup, online state, and PV metadata removal.

## Main Functions
- `_vgremove_single()` removes one VG (`lines 20-99`).
- `vgremove()` validates command line, sets global flags, and processes VGs for update (`lines 101-124`).

## Behavior
- Requires VG names or `--select` (`lines 105-109`).
- Takes global exclusive lock and clears hints (`lines 111-114`).
- Enables wiping outdated PVs and missing-PV handling (`lines 116-119`).
- In callback, constructs a local `void_handle` to disable internal per-LV selection because selection has already happened per VG (`lines 24-35`).
- Computes force behavior from `--force` or `--yes` (`lines 37-43`).
- If visible LVs exist and prompting is enabled, warns about missing PVs and asks for confirmation (`lines 50-64`).
- Removes each LV in the VG through `process_each_lv_in_vg(... lvremove_single)` (`lines 66-70`).
- Removes pool metadata spare LV if present (`lines 73-75`).
- If PR is required/autostarted, prepares PR finish state before removal and completes PR cleanup after lockd/VG removal (`lines 77-97`).
- Frees lockd VG state, checks remove safety when not forced, updates online state, removes PVs, removes VG metadata, and finalizes lockd cleanup (`lines 80-93`).

## Dependencies And Interactions
- Uses `lvremove_single`, `persist_finish_before/after`, `lockd_free_vg_before/final`, `online_vgremove`, `vg_remove_pvs`, and `vg_remove`.
- Iterates with `process_each_vg(... READ_FOR_UPDATE ...)`.

## Risks / Caveats
- LV selection must remain per-VG; callback explicitly disables internal per-LV selection to avoid semantic mismatch.
- PR cleanup happens across multiple phases; warning/failure behavior differs before and after VG removal.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgremove.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgrename.c -->
# File Research: sources/block-storage/lvm2/tools/vgrename.c

## Purpose
Implements `vgrename`, renaming a VG while handling VG-name locking order, UUID-as-old-name cases, lockd rename hooks, PR key-file rename, active LV refresh, and backup cleanup.

## Main Structures
- `struct vgrename_params` stores old/new names, whether old name is a UUID, lock ordering choice, and whether the prelocked new name still needs unlocking (`lines 19-25`).

## Main Helpers
- `_lock_new_vg_for_rename()` obtains a write lock for the target VG name (`lines 27-36`).
- `_vgrename_single()` performs the actual rename on the matched VG (`lines 38-170`).

## Rename Flow
- `vgrename()` requires exactly old and new VG names, strips dev dirs, validates rename params, stores names in the command pool, takes global exclusive lock, and clears hints (`lines 181-201`).
- If old name is not a UUID, it determines lock ordering lexicographically and may prelock the new VG name before `process_each_vg()` locks the old name (`lines 203-231`).
- If old name may be a UUID, locking of the new name is deferred because the real old VG name is not known yet (`lines 203-211`, `220-231`).
- `_vgrename_single()` checks UUID old-name resolution did not make old/new equal (`lines 49-59`).
- Rejects a new VG name that already exists in lvmcache or matches an existing VG UUID string (`lines 61-81`).
- Locks the new name if old-name-first ordering or UUID special case applies (`lines 83-107`).
- Runs lockd pre-rename hook, renames PR key file if needed, calls `vg_rename()`, writes/commits metadata, and refreshes active visible LVs if the old `/dev/<vg>` path exists (`lines 109-149`).
- Runs lockd final hook, removes old backup, unlocks the new VG name, reports success (`lines 151-161`).
- Error path unlocks new name and finalizes lockd rename as failed (`lines 163-169`).
- After processing, `vgrename()` unlocks prelocked new name if the callback was never reached (`lines 240-245`).

## Dependencies And Interactions
- Uses validation helper `validate_vg_rename_params`.
- Uses lvmcache to detect name and UUID collisions.
- Uses lockd rename hooks and persistent key-file rename support.
- Uses activation refresh to update active device names instead of directly renaming directories.

## Risks / Caveats
- Lock ordering is central to avoiding deadlocks and has special handling for UUID input.
- Active LV path update depends on `vg_refresh_visible()` when activation is enabled and old path exists.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgrename.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgscan.c -->
# File Research: sources/block-storage/lvm2/tools/vgscan.c

## Purpose
Implements `vgscan`, scanning and reporting VGs, optionally notifying D-Bus or creating missing device nodes.

## Main Functions
- `_vgscan_single()` reports each found VG, noting exported state and metadata type, then checks backup freshness (`lines 18-29`).
- `vgscan()` handles special modes and main VG processing (`lines 31-64`).

## Behavior
- `--notifydbus` requires LVM to be built with D-Bus support and `global/notify_dbus` enabled; if valid, sets PV/VG/LV notification flags and returns without scanning output (`lines 35-48`).
- `--cache` is ignored with a warning because lvmetad is no longer used (`lines 50-53`).
- Normal mode processes each VG and prints `Found [exported] volume group ... using metadata type ...` (`lines 22-24`, `55`).
- If `--mknodes` is set, calls `vgmknodes()` after scanning and returns the worse status (`lines 57-61`).

## Dependencies And Interactions
- Uses lvmnotify support for D-Bus notification mode.
- Uses `process_each_vg()` and `vgmknodes()`.
- Calls `check_current_backup(vg)` for each found VG.

## Risks / Caveats
- `--cache` no longer performs cache work; callers relying on old lvmetad behavior only receive a warning.
- D-Bus notification mode is gated both by build support and runtime config.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgscan.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/vgsplit.c -->
# File Research: sources/block-storage/lvm2/tools/vgsplit.c

## Purpose
Implements `vgsplit`, moving selected PVs or an LV’s used PVs from one VG into a new or existing destination VG while preserving LV dependency integrity.

## LV Movement Helpers
- `_lv_is_in_vg()` and `_lvh_in_vg()` test LV ownership and find LV list handles (`lines 19-36`).
- `_lv_tree_move()` moves an LV list item to another VG, updates LV VG/LVID, and recursively moves AREA_LV dependencies from the source VG (`lines 38-68`).
- `_move_one_lv()` requires inactive LVs, refuses LVs still allocated on source PVs, moves the LV tree, and transfers pool metadata spare pointer when the spare itself moves (`lines 70-104`).
- `_move_lvs()` handles ordinary LVs, skipping snapshots, RAID, mirrors, thin, VDO, cache/writecache classes for specialized passes; it ensures each LV’s PV areas are wholly in one VG before moving (`lines 106-186`).
- `_move_snapshots()` moves hidden snapshot LVs only when both cow and origin are already in the destination; refuses split snapshot pairs (`lines 188-233`).
- `_move_mirrors()` ensures mirror images and logs move together and refuses split mirrors (`lines 235-293`).
- `_move_raids()` moves whole RAID LV stacks when allocations are on destination PVs (`lines 295-324`).
- `_move_thins()` keeps thin pool data/metadata and external origins consistent (`lines 326-383`).
- `_move_vdos()` moves VDO and VDO pool stacks based on VDO data LV placement (`lines 385-419`).
- `_move_cache()` keeps cache/writecache origin, data, metadata, cache pool, and cachevol components together (`lines 421-509`).
- `_new_vg_option_specified()` detects options only valid when destination VG is newly created (`lines 511-521`).

## Command Flow
- Requires source VG, destination VG, and either PVs or an LV name; rejects combining `--name` LV mode with PV args (`lines 538-548`).
- Takes global exclusive lock and clears hints (`lines 550-553`).
- Extracts optional LV name, source VG name, and destination VG name; rejects duplicate names (`lines 555-568`).
- Runs label scan, then either creates a new destination VG with a locked name or reads an existing destination VG for update (`lines 570-601`).
- Reads source VG for update and rejects shared VGs for both source and destination (`lines 603-614`).
- Sets command format from source VG (`line 616`).
- For existing destination VG, rejects new-VG-only options and checks compatibility (`lines 618-624`).
- For new destination VG, derives and validates `vgcreate_params` from source defaults and applies extent size, max LV/PV, allocation, system ID, and metadata copies (`lines 625-648`).
- Archives source VG before mutation (`lines 650-652`).
- Moves requested PVs or PVs used by the named LV into destination structures (`lines 654-665`).
- Performs dependency movement passes in order: RAID, generic LVs, mirrors, thin pools/volumes, VDO, cache, snapshots (`lines 667-700`).
- Splits metadata areas and requires metadata storage when source still has PVs (`lines 702-706`).
- Renames destination VG metadata and records source old name (`lines 708-713`).
- Computes PR state for moved PVs, starts destination PR before move when needed, and handles pool metadata spares in both VGs (`lines 718-744`).
- Archives destination, writes it first as exported, backs it up, writes old source VG if it still has PVs, clears exported state on destination, writes destination again, and backs it up (`lines 746-771`).
- Stops PR on moved devices when source had PR and destination does not, reports success, and releases VGs in destination-before-source order (`lines 773-790`).

## Dependencies And Interactions
- Uses `move_pv()` and `move_pvs_used_by_lv()` for PV relocation.
- Uses VG creation parameter helpers when creating a new destination VG.
- Uses LV type predicates and segment relationships extensively to preserve topology.
- Uses archive/backup, metadata area splitting, pool metadata spare handling, PR start/stop, and VG write/commit sequencing.

## Notable Design Details
- Destination VG is written as exported first so a crash after creating destination metadata leaves a recoverable exported VG (`lines 729-735`).
- After source VG is updated, recovery expectation changes to importing the new VG (`lines 754-757`).
- Shared VGs are not supported (`lines 596-600`, `609-614`).

## Risks / Caveats
- The split correctness depends on the ordering and completeness of LV dependency movement passes.
- Several comments note recovery is manual or not automated after crashes during multi-step writes.
- Destination VG references moved elements from source, so release order is significant (`lines 782-788`).
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/vgsplit.c -->