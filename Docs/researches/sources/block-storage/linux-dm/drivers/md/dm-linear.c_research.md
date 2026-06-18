# File Research: sources/block-storage/linux-dm/drivers/md/dm-linear.c

## Purpose
Implements the simple Device Mapper `linear` target, which maps a contiguous logical range to a contiguous range on one underlying block device.

## Main Interfaces
- Target lifecycle: `linear_ctr()`, `linear_dtr()`.
- I/O mapping: `linear_map()`, `linear_map_bio()`, `linear_map_sector()`.
- Reporting/control: `linear_status()`, `linear_prepare_ioctl()`, `linear_iterate_devices()`.
- Zoned/DAX support: `linear_report_zones()`, `linear_dax_direct_access()`, `linear_dax_zero_page_range()`.
- Module hooks: `dm_linear_init()`, `dm_linear_exit()`.

## Control Flow
Construction parses `<dev_path> <offset>`, opens the underlying device with the table mode, stores the start sector, and advertises flush/discard/secure-erase/write-same/write-zeroes support pass-through counts. Mapping replaces the bio device and offsets the sector by `start + target_offset`, except for zero-sector bios unless they are zone-management operations.

## State And Synchronization
The target context is only `struct linear_c`, containing the underlying `dm_dev` and start sector. It relies on DM core table/device lifetime rules rather than internal locking.

## Integration Points
Passes through integrity and crypto capabilities via target feature flags, supports nowait, host-managed zoned devices, block ioctl pass-through when the mapping exactly covers the whole device, and DAX direct access/zeroing when filesystem DAX is enabled.

## Notable Behaviors
- `prepare_ioctl` only permits ioctl pass-through if the linear mapping starts at zero and length equals the underlying device size.
- `iterate_devices` exposes the exact underlying range for queue-limit stacking.
- IMA status emits device name and start sector.
- DAX page offsets are adjusted by the underlying block device start sector.

## Risks And Review Focus
- Sector arithmetic is intentionally minimal; constructor validation of start-sector parsing matters.
- Zone-management bios require sector remapping even if they carry no data sectors.
- Capability pass-through assumes the underlying device and table stacking code enforce detailed limits.
