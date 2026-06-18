# File Research: sources/block-storage/lvm2/lib/device/dev-md.c

## Purpose
Detects Linux MD RAID components and derives MD stripe geometry from sysfs.

## Signature Detection
Native detection checks:
- MD v1.1 magic at offset 0.
- MD v1.2 magic at offset 4096.
- When `full` is set, MD v0.90 magic near the 64KiB-aligned end.
- MD v1.0 magic near 8KiB from the end.
- Intel IMSM signature near the end, adjusted for 4K logical block size.
- DDF headers at 512 bytes or 128KiB from the end, with CRC validation.

With udev support, `DEV_EXT_UDEV_BLKID_TYPE == linux_raid_member` is also accepted when external device info source is udev.

`dev_is_md_component()` marks `DEV_IS_MD_COMPONENT` on success and can return the found offset.

## Sysfs Geometry
The file reads MD sysfs attributes through `_md_sysfs_attribute_scanf()`:
- `chunk_size`
- `level`
- `raid_disks`
- `metadata_version`

`dev_md_stripe_width()` computes data-disk count by RAID level and returns stripe width in sectors. `dev_is_md_with_end_superblock()` identifies MD devices with metadata versions `1.0` or `0.90`.

## Integration
Used by filters and metadata placement code to avoid clobbering MD members and to align LVM data appropriately over MD devices.

## Risk Notes
- End-of-device checks are intentionally skipped unless `full` is requested to avoid extra IO on every command.
- IMSM logging reports the previous `sb_offset` value rather than the exact IMSM offset after detection.
- DDF validation depends on CRC interpretation in either endian form.
- Non-Linux builds return no MD detection/geometry.
