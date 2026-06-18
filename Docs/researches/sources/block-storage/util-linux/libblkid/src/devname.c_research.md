# File Research: sources/block-storage/util-linux/libblkid/src/devname.c

## Purpose
Finds or creates cache entries by device path and implements whole-system device probing for cache population.

## Main Components
- `blkid_get_dev()` searches cache by exact path, then canonicalized path, optionally creates a new cache device, and optionally verifies it.
- `is_dm_leaf()` checks `/sys/block/<name>/holders` to prioritize leaf device-mapper nodes.
- `probe_one()` maps kernel/sysfs partition names and device numbers to usable `/dev` paths, verifies/adds cache entries, and assigns priorities for DM/MD/LVM/UBI/removable devices.
- Legacy LVM `/proc/lvm/VGs` helpers discover LVM logical volumes.
- `ubi_probe_all()` scans `/dev`, `/devfs`, and `/devices` for UBI character volumes.
- `sysfs_probe_all()` scans `/sys/block`, filters empty/nonpartitionable removable devices, probes partitions or whole disks, and removes cached whole-disk entries when partitions exist.
- `probe_all()` coordinates cache read, LVM/UBI/sysfs scans, probe-interval throttling, and cache flush.
- Public functions: `blkid_probe_all()`, `blkid_probe_all_new()`, and `blkid_probe_all_removable()`.
- `TEST_PROGRAM` main exercises full and removable probing.

## Dependencies and Interactions
Integrates cache/device verification, device-number lookup from `devno.c`, sysfs helpers, canonicalization helpers, and low-level probing. It is the scan fallback used when evaluating labels/UUIDs without relying solely on udev symlinks.

## Research Notes
The scan intentionally mimics `/proc/partitions` behavior using sysfs and skips certain removable devices unless explicitly requested. Existing cache entries are verified and stale duplicates with matching type/label/UUID are removed.
