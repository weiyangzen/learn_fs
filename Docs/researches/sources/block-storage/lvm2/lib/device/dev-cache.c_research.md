# File Research: sources/block-storage/lvm2/lib/device/dev-cache.c

## Purpose
Implements LVM2's global device cache. It discovers block devices from `/dev` or udev, maintains aliases and preferred names, indexes devices by path and devno, supports optional active-DM-device caches, builds VGID/LVID holder indexes, and sets up devices-file/device-list filtering.

## Core State
The file uses one global `_cache` containing:
- Pool allocator and configured `dev_dir`.
- `names`: path string to `struct device`.
- `devices`: devno to `struct device`.
- `sysfs_only_devices`: temporary entries for devices seen in sysfs before `/dev`.
- `vgid_index` and `lvid_index`: LV holder indexes for devices used by LVs.
- Optional active DM caches: `dm_devs`, `dm_uuids`, `dm_devnos`.
- Preferred-name regex matcher.
- Scan directory/file lists and scan status.

## Device Creation And Alias Handling
`dev_init()` initializes nonzero defaults and embedded lists. `_dev_create()` allocates a device and records its `dev_t`.

`_add_alias()` inserts a path into a device alias list and optionally into the `names` radix tree. Preferred alias order is controlled first by configured `devices/preferred_names`, then by built-in path preference rules that de-prioritize `/dev/block`, `/dev/dm-*`, `/dev/disk`, and `/dev/mapper`, then by path depth, symlink preference, and ASCII order.

`_insert_dev()` handles all combinations of existing devno and existing path, including rehashing aliases when a path now refers to a different `dev_t`.

`dev_cache_failed_path()`, `_drop_all_aliases()`, and `dev_cache_verify_aliases()` remove stale aliases when device nodes disappear or are reused.

## Discovery And Indexing
`dev_cache_scan()` scans configured directories with locale forced to `C`. With udev support and configuration, `_insert_udev_dir()` enumerates block devices and devlinks from libudev. Without that, `_insert_dir()` recursively scans directories while skipping known non-block-device `/dev` subdirectories.

The VGID/LVID indexer examines sysfs holders under `/sys/dev/block/<major>:<minor>/holders`, resolves holder devices, checks DM UUIDs for LVM UUID format, skips internal same-VG holders, and stores lists keyed by VG UUID and LV UUID.

The sysfs-only path covers races where sysfs reports a newly created DM/LV device before `/dev` has a matching node.

## Active DM Device Cache
`dm_devs_cache_update()` calls `get_dm_active_devices()`, requires UUID support in the kernel DM device list, and builds radix indexes by devno and UUID. This avoids repeated individual DM ioctl calls. `dm_devs_cache_label_invalidate()` invalidates label scans for active LVM DM devices.

## Public Lookup And Iteration
- `dev_cache_get()` and `dev_cache_get_existing()` resolve path names, repair stale cache entries, optionally add new devices, and apply filters.
- `dev_cache_get_by_devt()` and `dev_cache_get_by_pvid()` find devices by devno or PVID.
- `dev_iter_create()` snapshots values from the devno radix tree; `dev_iter_get()` applies optional filters while iterating.
- `dev_name()` returns the preferred alias or the unknown-device sentinel.

## Devices File Setup
`setup_devices_file()`, `setup_devices()`, `setup_device()`, and `setup_devices_for_online_autoactivation()` coordinate `devices/use_devicesfile`, `--devicesfile`, `--devices`, dmeventd-specific devices files, devices-file locking, reading, delayed creation policy, and matching device IDs to dev-cache entries.

## Integration
This file is central to label scanning, filters, activation, dmeventd, device ID management, DM UUID lookups, sysfs/udev integration, and bcache/device IO setup.

## Risk Notes
- The cache is global mutable state and not internally synchronized.
- Device-node reuse is a recurring edge case; the file contains several defensive alias-drop paths and comments noting that LVs should ideally not use the same dev-cache paths as PV scanning.
- Preferred-name selection depends on filesystem state and symlink layout.
- Udev/sysfs races are explicitly handled but still complex.
- Devices-file behavior has many command-mode exceptions, especially around first-time creation by `pvcreate`/`vgcreate`.
