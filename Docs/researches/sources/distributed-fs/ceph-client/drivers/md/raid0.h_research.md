# sources/distributed-fs/ceph-client/drivers/md/raid0.h

## Purpose
`raid0.h` defines the private in-memory layout structures used by the MD RAID0 personality. It captures how the array is divided into strip zones for uneven component sizes and records which historical multizone layout interpretation is active.

## Important APIs, Types, And Functions
`struct strip_zone` describes one contiguous array range: `zone_end` is the array-sector end boundary, `dev_start` is the starting offset on each participating real device, `nb_dev` is the number of devices in the zone, and `disk_shift` stores the first disk position for original-layout multizone rotation. `enum r0layout` defines `RAID0_ORIG_LAYOUT` and `RAID0_ALT_MULTIZONE_LAYOUT`. `struct r0conf` owns the `strip_zone` array, the flattened `md_rdev **devlist`, the number of zones, and the selected layout.

## Control Flow
The header contains no executable control flow. `raid0.c` fills `r0conf` during `create_strip_zones()`, consults it from `find_zone()`, `map_sector()`, normal request handling, discard handling, and frees it from `raid0_free()`.

## State And Persistence
These structures are in-memory only. They are reconstructed from MD metadata and member-device sizes at array run or takeover time. The layout enum reflects an on-disk/assembly compatibility decision, but this header itself does not persist data.

## Dependencies And Integration Points
The types rely on `sector_t` and `struct md_rdev` from MD/block-layer headers included before this private header. `raid0.c` is the direct consumer, and MD core indirectly depends on these definitions through `mddev->private` for RAID0 arrays.

## Risks
The header's fields encode the mapping contract. Changing field meaning, `RAID0_ORIG_LAYOUT`/`RAID0_ALT_MULTIZONE_LAYOUT` values, or the flattened `devlist` interpretation would break compatibility with existing arrays and the mapper in `raid0.c`. `disk_shift` only matters for original multizone layout, so code using it must preserve the "first zone layouts are identical" rule.

## Test Signals
Header coverage is indirect through RAID0 build, module load, assembly of equal-size and uneven-size arrays, and mapping/discard tests that exercise zone boundaries and both layout enum values.
