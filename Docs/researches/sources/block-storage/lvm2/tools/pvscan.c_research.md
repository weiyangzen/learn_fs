# File Research: sources/block-storage/lvm2/tools/pvscan.c

## Purpose

`pvscan.c` implements both display-oriented `pvscan` and event/cache-oriented `pvscan --cache`. The cache path supports incremental PV online tracking and event-driven autoactivation.

## Display Mode

Entry point: `pvscan_display_cmd()`.

- Validates incompatible `--exported` and `--novolumegroup`.
- `--allpvs` disables device-id filtering and hints.
- Processes PVs with `process_each_pv()`.
- `_pvscan_display_single()` filters exported/orphan selections, updates totals, and calls `_pvscan_display_pv()`.
- `_pvscan_display_pv()` formats short output, UUID output, all-PV output, orphan PVs, exported VG PVs, and normal VG PVs.
- Final summary reports total, in-use, and no-VG PV counts and sizes.

## Online File Model

The cache/autoactivation path uses runtime files under LVM online directories:

- `PVS_ONLINE_DIR`: one file per online PVID, storing device major/minor and VG info.
- `VGS_ONLINE_DIR`: one file per VG chosen/finished for activation coordination.
- `PVS_LOOKUP_DIR`: per-VG lookup files containing all PVIDs, used when a PV has no metadata.

Helpers include:

- `_online_pvid_file_remove_devno()`: removes online state for a missing device by major/minor.
- `_online_files_remove()`: clears an online directory.
- `_write_lookup_file()`: creates a VG lookup file with all PVIDs.
- `_count_pvid_files()` and `_count_pvid_files_from_lookup_file()`: decide whether a VG is complete.

## Autoactivation Flow

Entry point: `pvscan_cache_cmd()`.

- Respects `global/event_activation`.
- Suppresses complete VG/LV reporting when event activation is disabled.
- Disables udev/external device info sources because pvscan helps populate them.
- Sets up online directories.
- For no arguments, `_pvscan_cache_all()` scans all devices and recreates hints.
- For device or major/minor arguments, `_pvscan_cache_args()` performs optimized single-device processing.
- Complete VG names are accumulated in `complete_vgnames`.
- If `-aay` is requested, `_pvscan_aa()` activates complete VGs.

## Single-Device Cache Path

`_pvscan_cache_args()`:

- Parses path and major/minor args with `_get_args()`.
- Builds devices without filters using `_get_args_devs()`.
- Removes stale online files for disappeared major/minor devices.
- Sets up devices-file behavior without a full dev-cache scan.
- Applies nodata filters first.
- Handles udev `DEVLINKS` to make regex filters work before all symlinks exist.
- Optionally relaxes device-id filtering for unstable devnames, then checks PVID against the devices file after reading the label.
- Reads PVID labels, drops non-LVM devices, applies full filters, and scans selected devices into lvmcache.
- Calls `_online_devs()` to create online files, check completeness, list VGs/LVs, and collect activation candidates.
- Invalidates hints when PV state changes.

## All-Device Cache Path

`_pvscan_cache_all()`:

- Clears PV/VG/lookup online directories.
- Removes searched-devname state.
- Enables hint recreation.
- Runs full `lvmcache_label_scan()`.
- Iterates filtered devices from the device cache.
- Calls `_online_devs()` for all scanned devices.

## `_online_devs()` Behavior

For each selected device:

- Looks up lvmcache info by PVID.
- Skips unused PV extensions.
- Creates a format instance and tries to read VG metadata from MDA1 then MDA2.
- Validates that the PV belongs to the read VG.
- Filters MD components when full metadata checks indicate this may be needed.
- Ignores shared, foreign, or exported VGs for autoactivation.
- Creates `pvs_online/<pvid>` when `--cache` is used.
- For activation/checkcomplete, counts online/offline PVs using VG metadata or lookup files.
- Writes lookup files for multi-PV VGs and rechecks to close races with concurrent pvscans.
- Emits VG/LV completeness output for udev or human callers.
- Saves one complete VG in `saved_vg` for quick activation optimization.

## Quick Activation Optimization

`_pvscan_aa_quick()` avoids a broad scan when one complete VG was found from a single PV event:

- `_get_devs_from_saved_vg()` builds the VG device list from saved VG metadata and PVID online files.
- It locks the VG before label scanning.
- It label-scans only the VG's devices.
- It reads the VG with `READ_WITHOUT_LOCK | READ_FOR_ACTIVATE`.
- It verifies the read VG uses the expected devices.
- It calls `vgchange_activate(..., CHANGE_AAY, ...)`.

If quick activation fails or is unsuitable, `_pvscan_aa()` falls back to `process_each_vg()`.

## Race Handling

The file explicitly handles concurrent pvscans:

- `online_vg_file_create()` ensures only one process activates a completed VG.
- Lookup files are created with exclusive create; losers skip writing.
- After writing a lookup file, the writer recounts PVID online files to avoid missed completeness when another pvscan checked during the write.
- Device removal by major/minor removes matching PVID online files and associated VG/lookup files.

## Notable Constraints

- Clustered, shared, exported, and foreign VGs are skipped for event autoactivation.
- Shared VG activation is intentionally not handled here.
- Udev output mode prints only key/value lines for udev import compatibility.
- `pvscan()` itself is a placeholder internal-error function; command definitions dispatch to `pvscan_display_cmd()` or `pvscan_cache_cmd()`.
