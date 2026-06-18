# File Research: sources/block-storage/lvm2/tools/lvmdevices.c

## Purpose
Implements the `lvmdevices` command for inspecting and maintaining the LVM devices file.

## Major Helper: `_search_devs_for_pvids()`
- Builds a device list without applying filters that read device contents.
- Skips devices already matched to device-use entries.
- Applies no-data filters first.
- Reads LVM label PVIDs with `label_read_pvid()`.
- Matches requested PVIDs, records found devices, and reports missing PVIDs.
- Re-runs data-aware filters on found devices and warns if found PVIDs are on excluded devices.

## Major Helper: `_print_check()`
Compares the current processed `cmd->use_devices` state with freshly reread devices-file entries:
- Handles system identifier changes:
  - `PRODUCT_UUID`
  - `HOSTNAME`
- Correlates old/new entries by:
  - non-devname ID type and ID name
  - devname entries by PVID
  - changed IDTYPE by PVID
  - fully identical but insufficient entries as indeterminate
- Prints whether entries are unchanged, updated, missing, old, or new.
- Restores `cmd->use_devices` after comparison.

## `lvmdevices()` Modes
- `--listids`:
  - Does not use the devices file.
  - Scans device cache and lists available system device IDs for a device.
- Setup:
  - Calls `setup_devices_file()`.
  - Requires devices file support to be enabled.
  - Takes exclusive lock for mutating operations, shared lock for read/check.
  - Creates the devices file for add operations when missing.
  - Clears hints for default/system devices file mutations.
  - Reads device IDs, scans dev cache, and matches IDs to devices.

## Check/Update Path
For `--check` and `--update`:
- Invalidates searched devnames.
- Reads PVIDs and applies filters for each matched device.
- Validates devices-file entries against labels.
- Removes multipath components and optionally adds multipath devices.
- Checks serial-related IDs.
- Searches for moved devname/PVID entries, optionally with refresh.
- Prints old/new comparison via `_print_check()`.
- `--delnotfound` removes missing entries.
- `--update` writes only when needed, hash mismatch exists, found devices exist, or `--force`.
- `--check` exits with failure when real updates are needed.

## Add/Delete Paths
- `--adddev`:
  - Adds a named device even if filters exclude it, but warns.
  - Reads PVID if present.
  - Allows optional `--deviceidtype`.
- `--addpvid`:
  - Validates PVID format.
  - Searches all eligible devices for that PVID.
  - Adds found devices unless filtered out.
- `--addid --deviceidtype`:
  - Adds by explicit system device ID.
- `--deldev` without `--deviceidtype`:
  - Removes by device name.
  - Warns if argument does not look like `/dev/...`.
  - Prompts if used by active LV unless `--yes`.
- `--delid` or old `--deldev --deviceidtype`:
  - Removes by device ID.
- `--delpvid`:
  - Removes by PVID, rejects ambiguous duplicate entries, and prompts for active-LV use.

## Default Output
With no modifying/checking option, prints every devices-file entry:
- resolved device name or `none`
- IDTYPE
- IDNAME
- DEVNAME
- PVID
- optional partition number.

## Important Details
- Devices file locking is explicit and mode-dependent.
- The command deliberately separates filters that read device data from filters that do not.
- Multipath component cleanup is integrated into check/update.
- Active LV usage prompts protect users from removing devices currently in use.
