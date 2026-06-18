# sources/distributed-fs/ceph-client/include/uapi/linux/blkzoned.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blkzoned.h` exports the zoned block device ioctl ABI. The complete 211-line header was read. It defines zone types, zone conditions, report flags, zone descriptor and request structures, and ioctls for reporting, resetting, opening, closing, finishing, and querying zoned block-device geometry.

## Important APIs, Types, and Functions

There are no functions. Important enums are `blk_zone_type`, `blk_zone_cond`, and `blk_zone_report_flags`. Important structures are `struct blk_zone`, `struct blk_zone_report`, and `struct blk_zone_range`. Exported ioctls are `BLKREPORTZONE`, `BLKREPORTZONEV2`, `BLKRESETZONE`, `BLKGETZONESZ`, `BLKGETNRZONES`, `BLKOPENZONE`, `BLKCLOSEZONE`, and `BLKFINISHZONE`.

## Control Flow

The header has no executable flow. Userspace asks for zone descriptors with `BLKREPORTZONE` or `BLKREPORTZONEV2`, then uses the reported `start`, `len`, `capacity`, `wp`, `type`, and `cond` fields to plan sequential writes. Management operations pass `blk_zone_range` to reset write pointers, explicitly open zones, close zones, or mark zones full. Geometry queries return zone size and total zone count.

## State and Persistence Behavior

This ABI exposes and mutates persistent or device-managed zone state: write pointer position, open/closed/full/read-only/offline conditions, non-sequential resource usage, and reset recommendations. Cached reports can collapse implicit-open, explicit-open, and closed states into `BLK_ZONE_COND_ACTIVE`; regular reports should not use that synthetic condition. All sector fields use 512-byte units regardless of logical block size.

## Dependencies and Integration Points

Direct dependencies are `<linux/types.h>` and `<linux/ioctl.h>`. Integration points include the block layer zoned-device core, SCSI ZBC, ATA ZAC, NVMe ZNS, filesystems and databases that write sequentially to zones, and userspace management tools that choose between deprecated `BLKREPORTZONE` and flag-aware `BLKREPORTZONEV2`.

## Risks and Edge Cases

`struct blk_zone` is deliberately 64 bytes to match device standards; layout changes are ABI-sensitive. `struct blk_zone_report` uses a flexible array, so callers must allocate enough room for `nr_zones` descriptors and handle the output count. `BLKREPORTZONE` ignores input flags, while V2 uses flags as input and output; mixing those semantics can hide cached-report behavior. Range operations must be zone aligned. The `BLK_ZONE_COND_ACTIVE` and `BLK_ZONE_REP_CACHED` symbols are newer additions noted as Linux 6.19, so compatibility with older headers/kernels needs probing.

## Test Signals

Useful tests include zone report parsing with multiple descriptor counts, `BLKREPORTZONE` versus `BLKREPORTZONEV2` flag behavior, reset/open/close/finish operations on zoned loop or hardware devices, alignment and out-of-range error tests, verification that sector units are always 512 bytes, and compatibility tests against kernels that lack cached-report support.
