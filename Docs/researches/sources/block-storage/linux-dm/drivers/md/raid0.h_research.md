# File Research: sources/block-storage/linux-dm/drivers/md/raid0.h

## Purpose
Defines private RAID0 layout structures and the two supported multi-zone layout identifiers used by `raid0.c`.

## Main Interfaces
- `struct strip_zone`: logical end sector, component zone start sector, and number of devices in the zone.
- `enum r0layout`: `RAID0_ORIG_LAYOUT` and `RAID0_ALT_MULTIZONE_LAYOUT`.
- `struct r0conf`: zone array, flattened zone/device pointer table, zone count, and active layout.

## Control Flow
No executable control flow. The declarations support RAID0 zone construction and request mapping.

## State And Synchronization
`r0conf` is the personality-private state stored in `mddev->private`. It has no RCU head or internal lock; active configurations are expected to remain stable for the personality lifetime.

## Integration Points
Included by `raid0.c`; uses MD-local `struct md_rdev` pointers through the flattened `devlist`.

## Notable Behaviors
- The header documents the Linux 3.14 multi-zone layout compatibility issue and gives both layout modes stable numeric values.
- `devlist` is indexed as `zone_index * raid_disks + disk_index`, with only the first `strip_zone[zone].nb_dev` entries meaningful for each zone.

## Risks And Review Focus
- Structure changes must preserve the mapping assumptions in `map_sector()`, `dump_zones()`, and `raid0_handle_discard()`.
- The layout enum values are persisted/used as externally selected compatibility choices, so renumbering would be unsafe.
