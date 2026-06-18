# File Research: sources/block-storage/util-linux/libblkid/src/devno.c

## Purpose
Resolves Linux device numbers to block-device paths or whole-disk identifiers, with sysfs as the primary source and `/dev` scanning as fallback.

## Main Components
- `blkid_strconcat()` builds simple concatenated paths.
- Directory-list helpers manage breadth-first fallback scans.
- `blkid__scan_dir()` scans a directory for a block device with a matching `st_rdev` and optionally queues subdirectories.
- `scandev_devno_to_devpath()` searches `/devices`, `/devfs`, and `/dev` breadth-first.
- `blkid_devno_to_devname()` uses `sysfs_devno_to_devpath()` first, then the `/dev` scan fallback.
- `blkid_devno_to_wholedisk()` delegates to sysfs to map partition or disk devno to whole-disk name/devno.
- `blkid_driver_has_major()` scans `/proc/devices` block-device section for a driver/major association.
- `TEST_PROGRAM` main resolves a supplied devno or major/minor pair.

## Dependencies and Interactions
Used by device scanning and public device-number APIs. It depends on sysfs helpers and path constants from util-linux.

## Research Notes
The fallback scanner avoids symlink directory recursion and skips hidden `/dev` service directories such as `.udev`, `.mount`, `.mdadm`, and `/dev/shm`.
