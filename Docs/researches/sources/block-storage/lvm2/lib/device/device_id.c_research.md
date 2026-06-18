# File Research: sources/block-storage/lvm2/lib/device/device_id.c

## Purpose
Implements persistent device-ID handling for LVM's `system.devices` mechanism. It reads, writes, locks, validates, repairs, and searches device-file entries that map stable identifiers and PVIDs to actual block devices.

## Main Responsibilities
- Maintains devices-file version state, lock fd/path state, and temporary `searched_devnames` state used to suppress repeated expensive devname searches.
- Normalizes PVID strings with `strdup_pvid` so buffers are always `ID_LEN + 1`.
- Reads sysfs and DM identifiers for many ID types: sysfs WWID, sysfs serial, multipath UUID, crypt UUID, LV UUID, MD UUID, loop backing file, devname, SCSI WWIDs, and NVMe WWIDs.
- Chooses a preferred ID type in `device_id_system_read_preferred`: DM UUIDs for DM devices, loop backing file for loops, MD UUID for MD, then WWID/VPD serial, then devname fallback.
- Parses `system.devices` into `cmd->use_devices`, including `PRODUCT_UUID`, `HOSTNAME`, `REFRESH_UNTIL`, `VERSION`, hash comments, IDTYPE, IDNAME, DEVNAME, PVID, and PART fields.
- Writes `system.devices` atomically through a temporary file, version bump, hash generation, directory fsync, and optional backup retention.
- Adds or updates devices-file entries in `device_id_add`, handling duplicate PVIDs, duplicate device IDs, existing entries for the same dev, and partition entries.
- Matches devices-file entries to dev-cache objects in `device_ids_match`, with stable ID types matched before `IDTYPE=devname`.
- Validates post-scan PVIDs and devnames in `device_ids_validate`, repairing wrong PVID/devname fields, stale WWIDs, duplicate devname entries, and misplaced devname matches.
- Handles duplicate serial-number ambiguity in `device_ids_check_serial` by reading PVIDs from all devices sharing suspect serials and rematching by PVID.
- Searches for missing PVIDs in `device_ids_search`, used for renamed devname devices, refresh after machine identity change, and `lvmdevices --refresh`.
- Provides flock-based shared/exclusive devices-file locking.

## Important Control Flow
The intended command sequence is documented in the file: read devices file, scan dev-cache, match IDs to devices, label-scan matched devices, then validate PVIDs against on-disk labels.

`_match_du_to_dev` is the core matcher. It rejects incompatible major numbers and wrong partition numbers, handles DM devname aliases, normalizes old underscore-heavy sysfs IDs, repairs old swapped DM ID types, caches negative and positive ID reads on `dev->ids`, and can match a sys_wwid entry against extra VPD/NVMe WWIDs if sysfs output has changed.

`device_ids_validate` treats stable ID entries as authoritative by ID and PVID as a validation field. For `IDTYPE=devname`, PVID is the authoritative identity because devnames can move. Wrongly matched devname devices are detached and may be removed from lvmcache.

`device_ids_search` builds a list of missing PVIDs and a filtered list of unmatched system devices, optionally skipping devices that have stable IDs in `search_for_devnames=auto` mode. It reads labels from candidates, detects duplicate PVIDs, updates matching `dev_use` entries with either new devnames or new preferred IDs, and returns newly found devices for label scanning.

## Dependencies
Depends on command context settings, dev-cache iteration, filters, label/PVID reads, lvmcache updates, DM UUID helpers, VPD parsing, NVMe WWID collection, CRC helpers, device-file config, flock locking, and sysfs access helpers.

## Risk Notes
- This file is a policy hotspot: changing preferred ID ordering or matching fallback behavior changes which devices LVM accepts.
- `IDTYPE=devname` is intentionally less trusted and repaired by PVID; stable IDs are mostly trusted but serials get special duplicate handling.
- Devices-file writes must preserve version/hash/backup/lock semantics to avoid races between commands.
- Refresh behavior can intentionally reassign PVID entries to devices with new IDs after host/product identity changes, but careless broad searching can select stale clones.
- Many caches store negative reads to avoid repeated sysfs probing; callers must clear/rebuild state when device identity can change.
