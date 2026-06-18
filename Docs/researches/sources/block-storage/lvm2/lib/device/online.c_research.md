# File Research: sources/block-storage/lvm2/lib/device/online.c

## Purpose
Manages transient `/run` online-state files used by pvscan/autoactivation to record online PVs and VGs. These files are not persistent metadata; they coordinate activation behavior and avoid losing context between udev-triggered scans.

## File Formats and Directories
PV online files live under `PVS_ONLINE_DIR` with filename equal to the PVID. Contents begin with `<major>:<minor>\n` and may include `vg:<vgname>\n` and `dev:<devname>\n`. VG online files live under `VGS_ONLINE_DIR`. Lookup files under `PVS_LOOKUP_DIR` map a VG to PVIDs when PV online files lack VG names.

## Main Functions
- `online_pvid_file_read` parses a PV online file, validates optional VG name and devname fields, and returns dev numbers.
- `get_pvs_online` lists PV online files, optionally filtered by VG name.
- `online_vg_file_create` and `online_vg_file_remove` create/remove VG online markers.
- `online_pvid_file_create` writes a PV online file atomically with `O_EXCL`, detects duplicate PVIDs when an existing file names a different devno, and logs pvscan-aware errors.
- `online_pvid_file_exists` checks whether a PVID file exists.
- `get_pvs_lookup` reads a VG lookup file and resolves listed PVIDs through PV online files.
- `online_dir_setup` creates the required run directories.
- `online_lookup_file_remove` removes a VG lookup file.
- `online_vgremove` removes VG and PV online files for a removed VG.

## Dependencies
Depends on defaults for online directory paths, `struct device`, PVID/VG name lengths, `validate_name`, and pvscan-aware logging macros declared in `online.h`.

## Risk Notes
- Online files are intentionally not fsynced because they are transient `/run` state.
- Duplicate PVID detection prevents autoactivation from blindly accepting a second device with the same PVID.
- Optional `dev:` is required to start with `/dev/`; optional `vg:` must pass LVM name validation.
- `online_vg_file_remove` removes the VG marker when any PV goes offline so a complete VG can be activated again later.
