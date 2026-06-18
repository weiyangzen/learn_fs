# File Research: sources/block-storage/cryptsetup/lib/utils_devpath.c

## Purpose
Resolves Linux block-device paths and sysfs-derived device properties.

## Key Responsibilities
- Looks up `/dev` paths from `major:minor` device ids using `/sys/dev/block` first and recursive `/dev` scanning as fallback.
- Avoids exposing internal dm kernel names like `dm-X` when a mapper path is available.
- Reads numeric and string sysfs attributes.
- Detects partition number, partition status, partition start offset, rotational/DAX/zoned status, and NOP-DIF integrity profile.
- Finds a partition device by matching start/size under a base device.
- Finds the base disk for a partition.
- Looks up dm UUIDs through `/dev/disk/by-id` and `/sys/block/*/dm/uuid`.

## Important Details
- Old `/dev` scanning skips noisy top-level dirs and limits recursion depth.
- Device path verification checks block type and exact `st_rdev`; if mismatched, it falls back to scanning.
- DM devices are excluded from kernel partition lookup paths.
- NOP-DIF detection checks `integrity/format` and tries `metadata_bytes`, then `integrity/tag_size`.

## Dependencies
Uses `internal.h`, dm helper declarations from `utils_dm.h`, sysfs, `/dev`, and Linux major/minor macros.
