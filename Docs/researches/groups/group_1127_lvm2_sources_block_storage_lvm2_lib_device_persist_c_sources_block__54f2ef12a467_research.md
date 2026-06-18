# Group Research: group_1127_lvm2_sources_block_storage_lvm2_lib_device_persist_c_sources_block__54f2ef12a467

Scope source tree: `sources/block-storage/lvm2`, which is included in `Docs/research_subset_a.md`. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/persist.c -->
# File Research: sources/block-storage/lvm2/lib/device/persist.c

This file implements LVM2 command-side persistent reservation orchestration for VG/PV devices. It parses `--setpersist` options, derives local PR keys from `local_pr_key` or `local_host_id`, reads SCSI/NVMe registrations/reservations, coordinates with `lvmpersist`, and keeps sanlock host-generation encoded keys synchronized.

Key responsibilities:
- Defines PR support checks in `dev_allow_pr`, accepting SCSI, multipath, and NVMe devices when NVMe support is compiled in.
- Maps SCSI persistent reservation types into internal `PR_TYPE_*` values, formats names such as `WE` and `WEAR`, and validates PR key strings as up to 16 hex digits.
- Maintains an optimization key file under `/var/lib/lvm/persist_key_<vg_name>_<vgid>`, with helpers to remove, rename, read, and write it. Sanlock VGs use the key file as a shortcut but fall back to device key discovery by host_id.
- Reads reservations and registered keys directly for SCSI devices with `SG_IO` persistent reserve-in commands. NVMe paths are delegated through `dev_read_reservation_nvme` and `dev_find_key_nvme` declared in `persist.h`.
- Normalizes multipath key discovery by sorting key arrays and removing duplicate keys reported through multiple paths.

The core state queries are `vg_is_registered`, `persist_is_started`, `persist_is_started_gen`, and `persist_is_started_by_other_hosts`. For non-shared VGs they expect a single local key and exclusive-style reservation. For shared/sanlock VGs they search for keys by `local_host_id`, accept WEAR shared reservation semantics, and validate sanlock generation bits when available. Partial registrations, inconsistent generations, read errors, missing reservations, and wrong reservation types are surfaced as errors or warnings depending on the caller's `may_fail` path.

Start/stop workflows are mostly wrappers around the external `lvmpersist` program:
- `persist_start` builds `lvmpersist start --ourkey ... --access ex|sh --vg ... --device ...` and optionally `--ptpl` or `--removekey`, then verifies every PV has the expected local key and a WE/WEAR reservation.
- `persist_stop`, `persist_stop_devs`, `persist_finish_before`, and `persist_finish_after` build stop commands and handle vgremove sequencing so PV lists are captured before metadata removal while the reservation is removed afterward.
- `persist_remove` and `persist_clear` invoke `lvmpersist remove` and `lvmpersist clear`.
- `persist_read` invokes `lvmpersist read` for all PV devices.

VG lifecycle integration:
- `persist_vgcreate_begin` starts an exclusive PR before PV initialization, using the raw configured key or host_id-derived key.
- `persist_vgcreate_update` converts a newly created shared VG from initial exclusive access to normal shared access, and for sanlock starts with generation 1.
- `persist_start_extend` starts PR on new PVs for local VGs, but for shared VGs requires all hosts to have pre-started PR on new devices and verifies new devices match existing registered keys.
- `persist_upgrade_ex` temporarily stops shared PR and restarts with exclusive access; `persist_upgrade_stop` stops a held upgraded key.

Sanlock-specific key handling is a major design point. Keys encode a fixed prefix, a 24-bit generation, and a 16-bit host_id. `get_our_key_sanlock_start` chooses the next generation from the running lockspace, key file, or devices. `persist_key_update` updates the registered key and key file after lockstart if sanlock reports a generation that differs from the guessed key. This avoids races where a rebooted host reuses an old key while another host removes it.

Important dependencies include `cmd_context`, `volume_group`, `pv_list`, `device`, device-type helpers from `dev-type.h`, config lookups from `config.h`, lvmlockd generation queries, endian conversion helpers, `exec_cmd`, and Linux SCSI generic headers. The file assumes command memory pools for short-lived arrays and uses explicit `malloc/free` for SG response buffers.

Edge cases and invariants:
- `setpersist_arg_flags` rejects contradictory option pairs such as `y,n` or `ptpl,noptpl`.
- Key-file corruption, parse failures, or host_id mismatches cause the key file to be removed and device discovery attempted.
- For exclusive starts, the file checks existing registered keys first to avoid starting a local VG already started by another host, especially on WEAR-capable multipath setups where device semantics alone may not enforce exclusivity.
- The key file is treated as an optimization; failure to write it generally logs but does not fail a successfully established PR.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/persist.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/persist.h -->
# File Research: sources/block-storage/lvm2/lib/device/persist.h

This header declares the persistent reservation API used by LVM command and metadata code. It defines string and numeric constants for supported reservation types: write exclusive, exclusive access, registrants-only variants, and all-registrants variants.

It also defines `SETPR_*` bit flags for user-facing persistent reservation options: enable/disable, require/norequire, autostart/noautostart, and PTPL/no-PTPL. `MAX_SETPR_ARGS` bounds comma-separated option parsing in `persist.c`.

The public API covers:
- PR state operations: `persist_check`, `persist_read`, `persist_start`, `persist_stop`, `persist_remove`, and `persist_clear`.
- VG lifecycle hooks: `persist_start_extend`, `persist_vgcreate_begin`, `persist_vgcreate_update`, `persist_finish_before`, `persist_finish_after`, and upgrade helpers for exclusive access.
- Query helpers for started/registered state and other-host detection.
- Key-file lifecycle helpers used by VG rename/remove paths.
- Device-level key/reservation functions for SCSI/NVMe dispatch and generic callers.

The header intentionally exposes NVMe-specific entry points while `persist.c` selects SCSI vs NVMe at runtime. Callers must provide full LVM context objects (`cmd_context`, `volume_group`, `device`, `dm_list`) and should treat integer return values as LVM-style success/failure booleans.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/persist.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/display/display.c -->
# File Research: sources/block-storage/lvm2/lib/display/display.c

This file implements human-readable and legacy-colon display helpers for LVM metadata objects and common conversion routines. It covers allocation policy conversion, lock-type conversion, size and percentage formatting, PV/LV/VG display output, segment display, name validation diagnostics, and the interactive yes/no prompt used by commands.

Allocation and lock helpers:
- `_policies` maps `alloc_policy_t` values to strings and report characters. `get_alloc_from_string` also accepts old metadata text `next free` as normal allocation.
- `get_lock_type_string` and `get_lock_type_from_string` map internal lock types to text values such as `none`, `dlm`, `sanlock`, and `idm`.
- `get_percent_string` maps percent denominator types to strings used in reports.

Formatting helpers:
- `display_lvname` and `display_percent` use a ring buffer in `cmd_context` to return short-lived strings.
- `display_size`, `display_size_long`, and `display_size_units` delegate sector-based formatting to `dm_size_to_string` using current command unit settings.
- `display_mb_size` converts MiB units to sectors before formatting.

PV display functions produce colon, segment, full, and short output. Full PV display derives usable/unusable size from PE layout, shows allocation state, PE counts, and UUID. Segment display iterates PV segments and prints either mapped LV extent ranges or free ranges.

LV display is broad and target-aware:
- `lvdisplay_full` handles historical LVs, visible vs internal naming, activation/read-only state, snapshots, thin volumes/pools, cache, cache pools, integrity, VDO pools/volumes, mirrors, RAID availability, read ahead, persistent major/minor, and block device numbers.
- It queries activation status with `lv_info`, target-specific status helpers such as `lv_thin_status`, `lv_cache_status`, `lv_vdo_pool_status`, and releases status memory pools after use.
- `lvdisplay_colons` preserves legacy colon output fields.
- `lvdisplay_segments` iterates segments and delegates segment-specific display to each segment type handler.

VG display functions emit full, colon, and short summaries including system_id, format, metadata area count, seqno, access mode, resize/export/shared status, LV/PV counts, active PVs, extent counts, sizes, free space, and UUID.

`display_formats`, `display_segtypes`, and `display_tags` simply iterate command-context lists and print names. `display_name_error` translates name validation enum values into user-facing errors.

`yes_no_prompt` is a robust stdin prompt parser. It defaults to `n` in silent mode or EOF, accepts lowercase yes/no prefixes with stricter newline behavior for yes, ignores leading/trailing whitespace, logs invalid input, and integrates with LVM signal handling so interrupts result in a negative answer.

Important dependencies include metadata object definitions, activation/status helpers, segment type handlers, config defaults, signal helpers, and logging functions. Most routines are display-only, but they can trigger target status queries and therefore may allocate/free transient status structures.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/display/display.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/display/display.h -->
# File Research: sources/block-storage/lvm2/lib/display/display.h

This header declares display and conversion helpers implemented by `display.c`. It includes metadata exports and LVM string helpers, then exposes functions for LV names, percentages, sector/MiB size formatting, and stripe area display.

The object display API covers PV, LV, and VG output variants: full, short, colon, and segment-oriented forms. It also declares simple enumerators for formats, segment types, and tags.

Conversion declarations include allocation policy string/char mapping, lock type string mapping, and percent-type string mapping. `display_name_error` is the central name validation diagnostic emitter, and `yes_no_prompt` is declared with a printf-format attribute for compile-time format checking.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/display/display.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/error/errseg.c -->
# File Research: sources/block-storage/lvm2/lib/error/errseg.c

This file registers LVM's virtual `error` segment type. The segment type represents logical extents that map to the device-mapper error target, causing I/O to fail predictably.

Core behavior:
- `_errseg_merge_segments` merges adjacent error segments by adding lengths and area lengths.
- Under `DEVMAPPER_SUPPORT`, `_errseg_add_target_line` emits an error target line into the device-mapper tree.
- `_errseg_target_present` lazily checks kernel support for the current and old truncated error target names, caching the result.
- `_errseg_modules_needed` requests the kernel error module in activation dependency lists.
- `_errseg_destroy` frees the allocated segment type.

`init_error_segtype` allocates and initializes the `segment_type` with name `SEG_TYPE_NAME_ERROR`, handler table `_error_ops`, and flags `SEG_CAN_SPLIT`, `SEG_VIRTUAL`, and `SEG_CANNOT_BE_ZEROED`. This makes error areas splittable and virtual while preventing zeroing semantics that would be nonsensical for an error target.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/error/errseg.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-composite.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-composite.c

This file implements a composite device filter that ANDs together a sequence of `struct dev_filter` instances. `composite_filter_create` copies the supplied filter pointer array, appends a NULL terminator, allocates the wrapper filter, and assigns name `composite`.

`_and_p` enables external device info for the duration of filtering, then invokes each child filter unless `use_filter_name` selects a specific child by name. The first failing child stops evaluation and returns failure without treating filter rejection as an internal error.

`_wipe` forwards cache/device wipe requests to child filters that implement a `wipe` method, honoring `use_filter_name`. `_composite_destroy` warns if the filter is still in use, destroys all child filters, then frees the copied array and wrapper.

The composite filter is the coordination point for ordered filter chains; the order of the child array determines which rejection reason is observed first.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-composite.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-deviceid.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-deviceid.c

This file implements the devices-file/devices-list admission filter. `_passes_deviceid_filter` clears deviceid-related filtered flags, then passes all devices when both devices file and devices list are disabled, or when the command has set `filter_deviceid_skip`.

When device matching is enabled, only devices with `DEV_MATCHED_USE_ID` pass. Non-matching devices are marked with `DEV_FILTERED_DEVICES_FILE` or `DEV_FILTERED_DEVICES_LIST` depending on which mechanism is active, then rejected with a debug message.

`deviceid_filter_create` allocates a simple `dev_filter` named `deviceid`; destruction only checks use count and frees the filter. The filter depends on `cmd_context` policy flags populated elsewhere by device-id discovery.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-deviceid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-fwraid.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-fwraid.c

This Linux-only filter rejects firmware RAID component devices when firmware RAID filtering is enabled. With udev support, `_udev_dev_is_fwraid` checks the udev blkid type property and treats non-software RAID values with a RAID suffix as firmware RAID components. Without udev, native detection logs that firmware RAID detection is unsupported and passes the device.

`_ignore_fwraid` skips data-dependent checks when `cmd->filter_nodata_only` is set, clears `DEV_FILTERED_FWRAID`, checks the global `fwraid_filtering()` setting, and rejects detected components while recording the filtered flag.

`fwraid_filter_create` returns a filter named `fwraid` on Linux and `NULL` on non-Linux builds. The implementation relies on external device info when available, especially udev, and logs an internal error if an unsupported external info source reaches the detector.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-fwraid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-md.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-md.c

This Linux-only filter rejects md RAID component devices so LVM scans the md aggregate device rather than its member devices. The file documents three md detection modes: checking superblocks at the start, checking both start and end, and relying on udev. Full checking is used for formatting commands and when older md metadata placement may exist.

`_passes_md_filter` skips work for nodata scans, clears `DEV_FILTERED_MD_COMPONENT`, honors the global `md_filtering()` setting, then calls `dev_is_md_component(cmd, dev, NULL, cmd->use_full_md_check)`. A return of 1 means the device is a component and should be rejected; a negative detection error is also rejected to avoid unsafe scanning.

`md_filter_create` allocates a filter named `md`, stores `dev_types` in `private`, and returns `NULL` on non-Linux builds. The filter is defensive: detection errors produce a skip rather than a pass, preventing component devices from being treated as PVs.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-md.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-mpath.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-mpath.c

This Linux-only filter rejects multipath component paths so LVM uses the multipath aggregate device. `_ignore_mpath_component` calls `dev_is_mpath_component`, records `DEV_FILTERED_MPATH_COMPONENT` on rejection, and logs the skipped component.

A notable devices-file safeguard warns when a multipath component is explicitly present in the devices file but the corresponding multipath device is missing. It looks up the aggregate devno with `get_du_for_devno` and `dev_cache_get_by_devt`, then emits a one-time suggestion to run `lvmdevices --update` outside the `lvmdevices` command itself.

`mpath_filter_create` requires sysfs to be mounted; without sysfs it logs that the multipath filter is skipped. On non-Linux builds it returns `NULL`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-mpath.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-partitioned.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-partitioned.c

This filter rejects devices that contain a partition table signature. `_passes_partitioned_filter` skips data reads during nodata-only scans, clears `DEV_FILTERED_PARTITIONED`, then calls `dev_is_partitioned`. Detected partitioned devices are rejected and flagged.

The filter is used to avoid accidentally treating whole disks with partition tables as LVM PV candidates. `partitioned_filter_create` allocates a filter named `partitioned`; the `dev_types` argument is unused in this implementation.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-partitioned.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-persistent.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-persistent.c

This file implements a caching wrapper around another device filter. The cache maps every device alias string to either a static good marker or bad marker in a radix tree, avoiding repeated evaluation of the underlying filter chain.

`struct pfilter` stores the radix tree, wrapped real filter, and `dev_types`. `_init_hash` recreates the radix tree. `_persistent_filter_wipe` clears the entire cache when called without a device or removes all aliases for a specific device.

`_lookup_p` behavior:
- If a specific `use_filter_name` does not target this filter, or the cache tree is unavailable, it delegates directly to the wrapped filter.
- Devices with no aliases are rejected.
- Cached bad devices are rejected, cached good devices pass.
- Uncached devices are evaluated by `pf->real->passes_filter`; pass/fail is cached against every alias.
- Invalid filter return values are logged, treated as pass, and not cached.

`persistent_filter_create` initializes the wrapper named `persistent` and owns the wrapped filter; `_persistent_destroy` destroys the radix tree, destroys the wrapped filter, and frees all wrapper storage. The file explicitly notes that this cache is a workaround for repeated filter evaluation elsewhere in the scanning path.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-persistent.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-regex.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-regex.c

This file implements the user-configured regex device filter. Patterns are config strings beginning with `a` or `r`, followed by a delimiter and a regex, for example accept or reject rules. `_extract_pattern` parses the action, recognizes paired delimiters such as parentheses/brackets/braces, strips the trailing separator, and records whether the indexed pattern accepts.

`_build_matcher` validates the config list, allocates a scratch pool, reverses the configured order when building the matcher to get the desired first-match precedence, creates a bitset of accepting patterns, and builds a `dm_regex` engine in the filter memory pool.

`_accept_p` clears `DEV_FILTERED_REGEX` and may bypass regex filtering when a devices list is active, when `filter_regex_skip` is set, or when the devices file is enabled without `filter_regex_with_devices_file`. In the devices-file bypass case it emits one-time warnings that `filter` or `global_filter` is ignored.

When active, it tests all aliases. The first matching accept passes the device and may set the preferred name if a non-first alias matched. Matching rejects mark the device rejected; aliases that match nothing pass by default unless a reject was seen. `regex_filter_create` owns all memory through a dm pool and names the filter `regex`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-regex.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-signature.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-signature.c

This Linux-only filter rejects devices with legacy signatures that LVM should not treat as normal PV candidates. `_ignore_signature` reads the first 4096 bytes, rejects on read failure, rejects LVM1 devices detected by `dev_is_lvm1`, and rejects old GFS pool devices detected by `dev_is_pool`.

It skips data reads when `cmd->filter_nodata_only` is set. Rejections set `DEV_FILTERED_SIGNATURE`; successful signature checks pass. `signature_filter_create` allocates a filter named `signature` and stores `dev_types` in `private`; non-Linux builds return `NULL`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-signature.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-sysfs.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-sysfs.c

This Linux-only filter rejects devices that do not have a corresponding sysfs block entry. `_accept_p` clears `DEV_FILTERED_SYSFS`, passes devices whose non-devname IDs already imply sysfs discovery, then checks `<sysfs_dir>/dev/block/<major>:<minor>` with `lstat`.

If sysfs path construction fails, the filter passes rather than rejecting on an internal formatting problem. If the sysfs entry is absent, it marks `DEV_FILTERED_SYSFS` and rejects the device.

`sysfs_filter_create` requires a configured sysfs directory and verifies that `/sys/dev/block` exists for old-kernel compatibility. It allocates one object containing both the filter and a trailing copy of the sysfs directory string, stores that string in `private`, and names the filter `sysfs`. Non-Linux builds return `NULL`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-type.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-type.c

This filter rejects unrecognized block device major types. `_passes_lvm_type_device_filter` looks up the device major in `dev_types->dev_type_array` and requires a nonzero `max_partitions` entry. Unknown majors are marked `DEV_FILTERED_DEVTYPE` and rejected.

`lvm_type_filter_create` allocates a filter named `type` with `dev_types` stored in `private`. It is a low-cost structural filter and does not perform data reads.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-type.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-usable.c -->
# File Research: sources/block-storage/lvm2/lib/filters/filter-usable.c

This filter rejects block devices that are too small or unusable as PV scan candidates. `_check_pv_min_size` reads the device size and requires it to be at least `pv_min_size()`, logging a specific "too small" reason on failure.

`_passes_usable_filter` clears minsize/unusable/LV flags. For device-mapper devices it calls `dm_device_is_usable` with parameters stored in `private`; unusable devices are marked as either `DEV_FILTERED_IS_LV` or `DEV_FILTERED_UNUSABLE`. If the DM usability checks pass, it applies the PV minimum size check and marks `DEV_FILTERED_MINSIZE` on failure.

`usable_filter_create` builds a `dev_usable_check_params` object with checks for empty, blocked, suspended, error-target, reserved, and LV devices. The LV check is disabled when `devices/scan_lvs` is enabled. The filter is named `usable` and owns both the filter and parameter allocation.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter-usable.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter.h -->
# File Research: sources/block-storage/lvm2/lib/filters/filter.h

This header declares the LVM device filter constructors and filtered-reason bit flags. It includes device cache and device-type definitions because filters operate on `struct device`, `struct dev_types`, and command contexts.

Constructors cover composite, type, md, firmware RAID, multipath, partitioned, persistent cache, sysfs, signature, deviceid, regex, and usable filters. The regex comment documents pattern grammar: strings begin with accept/reject (`a`/`r`) and use a delimiter around the regex.

The `DEV_FILTERED_*` constants are bit flags stored in `device->filtered_flags` to explain why a device was rejected, including md/mpath components, partition tables, regex rejection, signatures, missing sysfs, unrecognized type, too-small devices, unusable DM devices, devices-file/list mismatch, and LV scanning exclusion.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/filters/filter.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/archive.c -->
# File Research: sources/block-storage/lvm2/lib/format_text/archive.c

This file implements low-level text metadata archive listing, creation, expiration, and display. Archive files are expected to live in a directory and use a VG-derived name with a numeric index and `.vg` suffix.

Archive discovery:
- `_split_vg` parses filenames of the form `<vg>_<number...>.vg` and extracts the VG name and index.
- `_scan_archive` uses `scandir` with `versionsort` when available, filters entries for the requested VG, copies file names into a memory pool, and inserts them into a list sorted newest-first by index.
- `_insert_archive_file` maintains that sorted list.

Expiration and creation:
- `_remove_expired` walks old archives from the back of the list, removes files older than the configured retention days while preserving the minimum archive count, and warns if archive storage grows beyond broad size/count thresholds.
- `archive_vg` writes metadata to a temporary file, closes it safely, scans existing archive names to choose the next index, tries up to ten rename names using a random suffix, and then prunes expired archives.

Display:
- `_display_archive` creates a private text format instance for the archive file, reads metadata with timestamp and description, and prints file, VG name, description, and backup time.
- `archive_list` lists all archives for a VG from oldest display order by iterating the sorted list backward.
- `archive_list_file` displays one explicit archive path.
- `backup_list` displays the current backup file if present, using the same display path.

The file depends on text import/export, config parsing, LVM file helpers, and command context backup format support. It treats archive files as text metadata files and validates them by reading the VG before display.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/archive.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/archiver.c -->
# File Research: sources/block-storage/lvm2/lib/format_text/archiver.c

This file provides command-context lifecycle and high-level workflows for metadata archives and backups. Archives are pre-change historical copies; backups are the current post-change VG metadata copy.

Initialization and control:
- `archive_init`, `archive_exit`, and `archive_enable` manage `cmd->archive_params`, including directory, retention days, minimum archive count, and enabled state.
- `backup_init`, `backup_exit`, and `backup_enable` manage `cmd->backup_params`, including directory, enabled state, and warning suppression count.
- `_build_desc` creates descriptions recording whether metadata was created before or after executing the command line.

Archive/backup creation:
- `_archive` skips orphan VGs, disabled archive configs, test mode, and already-archived VGs. When enabled it creates the archive directory, handles read-only filesystems differently for compulsory vs best-effort calls, and calls `archive_vg`.
- `archive` wraps `_archive` with signal-interrupt handling.
- `backup_locally` creates the backup directory and writes the current backup with `_backup`, while warning if backups are disabled. `backup` unlocks memory first and skips orphan VGs.
- `backup_to_file` creates a private text-format instance and writes/commits VG metadata through its metadata area operations.

Read and restore:
- `backup_read_vg` reads a VG from a backup file through the backup text format instance and attaches PV devices with `set_pv_devices`.
- `_restore_vg_should_write_pv` decides whether a PV label/metadata must be written during restore, considering `do_pvcreate`, format feature support, and cached PV extension flags.
- `backup_restore_vg` optionally recreates PV structures, removes existing metadata areas, builds a new format instance, schedules PV writes, runs format-specific PV setup, optionally wipes labels/initial sectors, then performs `vg_write` and `vg_commit`.
- `backup_restore_from_file` reads a VG, rejects missing PV restores, requires `--force` for thin volumes, validates LV segment completeness, and restores the VG.
- `backup_restore` resolves the standard backup path and delegates.

Maintenance:
- `backup_remove` silently unlinks a current backup.
- `archive_display` and `archive_display_file` list archive/backup metadata.
- `check_current_backup` verifies the current backup matches VG seqno and ID; when stale, it archives the old backup, archives the current VG, and writes a fresh backup. It suppresses noisy read errors while checking.

The code is careful around test mode, read-only filesystems, signal handling, and orphan VGs. It uses both command memory pools and ordinary `strdup/free` for long-lived context settings.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/archiver.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/archiver.h -->
# File Research: sources/block-storage/lvm2/lib/format_text/archiver.h

This header declares the public archive and backup APIs. Its comment defines the key distinction: archives are pre-change historical VG configurations, usually kept under `/etc/lvm/archive`; backups are the current VG configuration, usually kept under `/etc/lvm/backup`.

The API includes initialization/exit/enable functions for archive and backup settings, archive display helpers, backup creation/removal, backup VG reading, restore-from-VG and restore-from-file paths, raw backup-to-file output, and `check_current_backup`.

Callers are expected to pass initialized `cmd_context` and `volume_group` objects, and restore callers must already hold appropriate ORPHAN and VG locks as documented in `archiver.c`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/archiver.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/export.c -->
# File Research: sources/block-storage/lvm2/lib/format_text/export.c

This file serializes in-memory LVM volume group metadata into the text metadata format, either to a `FILE`, to a dynamically resized raw buffer, or to a parsed config tree. It also exposes formatter helpers used by segment-specific text exporters.

Formatter design:
- `struct formatter` stores output destination, indentation, header placement, comment behavior, newline/output callbacks, and a radix tree mapping PV pointers to stable `pvN` names.
- File output emits tab-indented lines with optional aligned comments. Raw output appends to a heap buffer and doubles the buffer as needed.
- `_init` caches `uname` data used in metadata headers.
- Public formatter helpers include `out_inc_indent`, `out_dec_indent`, `out_newline`, `out_size`, `out_hint`, `out_text_with_comment`, `out_text`, `out_config_node`, and `out_areas`.

Header and common field output:
- `_print_header` writes LVM version, contents marker, format version, escaped description, creation host/system_id, and creation time.
- `_print_flag_config` uses `print_flags` to emit `status` and compatible `flags` arrays.
- `_out_list` formats tag/other string lists.
- `_sectors_to_units` provides human-readable size comments for file output.

VG/PV/LV serialization:
- `_print_vg` writes VG id, seqno, informational format name, status/flags, tags, system_id, lock_type/lock_args, persistent reservation settings, extent size, max LV/PV counts, allocation policy, profile, and metadata copies.
- `_build_pv_idx` assigns PV pointer-to-index mappings, and `_get_pv_idx` resolves them while exporting segment areas.
- `_print_pvs` writes each `pvN` block with id, hint device name, device-id metadata, status/flags, tags, device size, PE start/count, and optional bootloader area.
- `_print_lv` writes each LV block with id, status/flags, tags, creation timestamp/host, lock args, allocation policy, profile, read ahead, persistent major/minor, segment count, and each segment block.
- `_print_segment` writes segment extent range, reshape count, type plus encoded segtype LV flags, segment tags, and delegates target-specific fields to `segtype->ops->text_export`.
- `_print_lvs` writes visible LVs before hidden/internal LVs.
- Historical LV support writes creation/removal times, origin references, and live descendant lists while omitting historical descendants from the descendant buffer.

Top-level exports:
- `_text_vg_export` builds the PV index, optionally writes the header before or after the VG block, writes the VG block and child sections, then destroys the PV radix tree.
- `text_vg_export_file` writes comment-rich metadata to a `FILE`.
- `text_vg_export_raw` writes compact metadata to a dynamically allocated buffer sized from `vg->buffer_size_hint + 16384`.
- `export_vg_to_config_tree` exports to a raw buffer and reparses it into a `dm_config_tree`.

Important invariants:
- PV references in segment areas are exported as `pvN` names derived from pointer identity for the current export pass.
- Raw exports set `header = 0`, so the header is written after the VG block.
- WRITE flags may be transformed to `LVM_WRITE_LOCKED` for old-version compatibility when the VG is write-locked.
- Output helpers return failure on allocation, formatting, radix tree, or target text-export errors, causing the whole export to fail.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/export.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/flags.c -->
# File Research: sources/block-storage/lvm2/lib/format_text/flags.c

This file converts LVM status bitmasks to and from text metadata flag arrays. It defines static flag tables for VG, PV, and LV flags. Each entry has a bit mask, optional text description, and kind: status flag, compatible flag, or segment-type flag.

Flag tables intentionally include many internal-only flags with `NULL` descriptions. These bits are recognized so exports can clear them from the "unknown leftovers" check without writing them to metadata.

`print_flags` selects the table by object type, walks set bits, emits matching descriptions for the requested kind into a comma-separated quoted array, and warns if any unrecognized status bits remain. This is used by `export.c` for `status = [...]` and `flags = [...]`.

`read_flags` parses config values back into a status bitmask. It accepts empty arrays, requires string values, and has compatibility behavior for historical metadata:
- `CACHE_VOL` may be read as either status or compatible flag.
- Old VG `PARTIAL` status is accepted for backup restore compatibility even though live metadata no longer writes it.
- Unknown status flags are fatal.

`read_lvflags` parses extra LV flags embedded in a segment `type` string as `+FLAG` suffixes. These are intentionally treated as incompatible with old LVM versions. Unknown segtype flags produce a warning and failure.

`print_segtype_lvflags` appends all set `SEGTYPE_FLAG` LV flags to a buffer as `+FLAG` suffixes. This pairs with `read_lvflags` for metadata round-tripping of segment-level incompatibility markers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/flags.c -->