# File Research: sources/block-storage/util-linux/sys-utils/blkzone.c

## Scope

Implements `blkzone`, a command-line utility for zoned block devices. It reports zone metadata/capacity and performs zone reset/open/close/finish operations.

## Public And Internal APIs Covered

- Main command-line entry point.
- Commands: `report`, `capacity`, `reset`, `open`, `close`, `finish`.
- Device setup: `init_device()`.
- Zone size lookup: `blkdev_chunk_sectors()`.
- Reporting: `blkzone_report()`.
- Mutating actions: `blkzone_action()`.

## Control Flow And Behavior

- The first non-option argument selects a command.
- `init_device()` opens the target, verifies block-device type, reads total sectors and sector size.
- `blkdev_chunk_sectors()` maps the device to its whole-disk sysfs path and reads `queue/chunk_sectors`.
- `report` / `capacity` use `BLKREPORTZONE` in batches of 4096 zones:
  - `report` prints start, length, optional capacity, write pointer, reset/non-sequential flags, condition, and type.
  - `capacity` sums zone capacities and prints the total.
- Action commands validate offset alignment to zone size, compute range from `--count`, `--length`, or device size, clamp to device end, and issue the configured zone ioctl.
- `--count` and `--length` are mutually exclusive.

## Dependencies

- Linux zoned block API from `<linux/blkzoned.h>`, with fallback definitions for newer ioctls if headers lack them.
- Sysfs helpers for whole-disk mapping and `chunk_sectors`.
- util-linux block-device, option-exclusion, allocation, parsing, and i18n helpers.

## Risks And Invariants

- Offsets and lengths are expressed in 512-byte sectors, not bytes.
- Zone actions require zone-size alignment except the final range may end at device size.
- Zone condition/type arrays assume kernel enum values fit expected indexes.
- Capacity reporting adapts to whether `BLK_ZONE_REP_CAPACITY` is available.
