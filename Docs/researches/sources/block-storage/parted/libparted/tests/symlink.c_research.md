# File Research: sources/block-storage/parted/libparted/tests/symlink.c

## Purpose

`symlink.c` tests that libparted preserves `/dev/mapper/...` paths instead of canonicalizing them to `/dev/dm-*`, avoiding operations on stale device-mapper targets after symlink retargeting.

## Main Responsibilities

- Creates a temporary disk image.
- Creates a temporary path under `/dev/mapper`.
- Replaces that temp path with a symlink to the first disk image.
- Gets a `PedDevice` through the `/dev/mapper` symlink.
- Creates a second temporary disk image.
- Retargets the `/dev/mapper` symlink to the second disk image.
- Calls `ped_disk_clobber(dev)`.
- Passes if the operation uses the remembered `/dev/mapper` path and therefore follows the updated symlink.

## Dependencies and Interactions

The shell wrapper requires root because it creates symlinks under `/dev/mapper`.

## Notable Details

The file documents the historical failure mode in detail: older behavior canonicalized `/dev/mapper/foo` to `/dev/dm-N`, and later LVM changes could make the `PedDevice` point at the wrong underlying device.
