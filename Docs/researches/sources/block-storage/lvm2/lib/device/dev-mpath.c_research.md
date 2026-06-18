# File Research: sources/block-storage/lvm2/lib/device/dev-mpath.c

## Purpose
Detects whether a device is a multipath component and extracts WWIDs from multipath devices.

## Initialization And Caches
`dev_mpath_init()` creates a pool and a hash table caching DM minor numbers as multipath or non-multipath. If configured, it also reads a multipath WWIDs file into `_wwid_hash_tab`.

The file can parse `/etc/multipath.conf` and `/etc/multipath/conf.d/*` blacklist and blacklist_exceptions `wwid` entries. Blacklisted WWIDs are removed from the WWID hash unless they appear in exceptions.

`dev_mpath_exit()` destroys all multipath detection caches.

## Detection Paths
`dev_is_mpath_component()` first restricts checks to SCSI or NVMe devices and resolves partitions to primary devices. It then tries:
- Sysfs holders: a component's holder is a DM device whose UUID begins with `mpath-`.
- The configured multipath WWIDs file, matching WWIDs read from device VPD/sysfs and omitting type prefixes for naa/eui/t10 IDs.
- Udev properties `ID_FS_TYPE=mpath_member` or `DM_MULTIPATH_DEVICE_PATH=1` when udev is the configured external info source.

When sysfs holder detection succeeds, the holder devno is returned through `holder_devno`.

## WWID Extraction
`dev_mpath_component_wwid()` walks a DM multipath device's sysfs `slaves` directory and reads the first component's `device/wwid`, normalizing spaces for `scsi_debug`, and duplicates the result into the command pool.

## Integration
Used by device filters to avoid using individual paths that are members of a multipath map, preventing duplicate PV visibility and unsafe writes.

## Risk Notes
- Multipath config parsing is deliberately narrow and only recognizes simple `wwid` entries in blacklist sections.
- Sysfs detection depends on `/dev/dm-*` holder nodes existing under `cmd->dev_dir`.
- Results are cached by DM minor, so device-minor reuse after topology changes depends on cache lifetime.
- WWID matching handles common type prefixes but can miss device-specific WWID formats.
