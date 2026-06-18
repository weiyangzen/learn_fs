# File Research: sources/block-storage/mdadm/Query.c

## Purpose
`Query.c` implements `mdadm --query`, a brief device classifier for md arrays and component devices.

## Behavior
`Query()` opens the given device, checks whether it is an active md array using sysfs first and md ioctls as fallback, prints array size/level/device/spare summary, then guesses and loads any member superblock to report component membership.

For component devices, it extracts superblock UUID and disk information, looks up active arrays by UUID in the mdadm map, and reports whether the device appears active, inactive, mismatched, or undetected.

## Integration Notes
It uses `sysfs_read()`, `md_get_array_info()`, `guess_super()`, metadata `load_super/getinfo_super/uuid_from_super`, map lookup by UUID, and md disk info ioctls. Version 0.90 md names are released with `put_md_name()`.

## Risks
The output is intentionally heuristic. A stale map entry, missing sysfs data, or inaccessible active md device can produce "undetected" or "mismatch" even when the superblock is valid.
