# File Research: sources/block-storage/lvm2/lib/device/dev-type.h

## Purpose
Declares the device type, partitioning, signature detection, signature wiping, topology, and filesystem-probing interfaces implemented by `dev-type.c` and sibling device modules.

## Main Types and Constants
- `NUMBER_OF_MAJORS` is fixed at 4096, matching the 12-bit major-number space used by this code.
- `PARTITION_SCSI_DEVICE` marks majors treated as SCSI-like.
- `struct dev_type_def` stores max partition count and flags per major.
- `struct dev_types` caches known major numbers for MD, blkext, DRBD, device-mapper, EMC PowerPath, VxDMP, DASD, loop, and the full per-major table.
- Signature type flags (`TYPE_LVM1_MEMBER`, `TYPE_LVM2_MEMBER`, `TYPE_DM_SNAPSHOT_COW`) control wipe exclusions/no-prompt behavior.

## Exported API Surface
The header exposes creation of `struct dev_types`, subsystem classification, raw signature recognizers, multipath and LV DM UUID helpers, partition checks, primary-device resolution, topology reads, blkid filesystem queries, and active-LV holder detection.

## Dependencies
Includes `device.h`, metadata exports, label APIs, and platform major/minor helpers. It forward-declares `struct fs_info` so blkid filesystem functions can be declared without including `filesystem.h`.

## Risk Notes
This header is broad cross-module API. Changing idempotency, return values, or units for helpers like `dev_get_primary_dev`, `dev_is_partitioned`, or topology functions affects filters, scanning, PV creation, and lvresize paths.
