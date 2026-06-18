<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/core.c -->
# sources/distributed-fs/ceph-client/block/partitions/core.c

## Purpose
`core.c` orchestrates partition table probing, partition block-device creation/removal/resizing, partition sysfs/uevent attributes, rescan behavior, and sector reads for parser implementations.

## Important APIs, Types, and Functions
- Probe list: `check_part[]` orders enabled parser functions.
- Parser lifecycle: `allocate_partitions()`, `free_partitions()`, `check_partition()`, `read_part_sector()`.
- Partition device lifecycle: `add_partition()`, `drop_partition()`, `bdev_add_partition()`, `bdev_del_partition()`, `bdev_resize_partition()`.
- Rescan flow: `blk_add_partitions()`, `blk_add_partition()`, `bdev_disk_changed()`.
- Sysfs/device model: `part_type`, partition attributes (`partition`, `start`, `size`, `ro`, alignment/discard alignment, stats, inflight), and uevent variables `PARTN`, `PARTNAME`, `PARTUUID`.

## Control Flow
`check_partition()` allocates a `parsed_partitions`, initializes a one-page diagnostic buffer, and walks `check_part[]` in order. Before each parser attempt it clears the parts array. Negative parser results are saved as read errors but do not stop probing. A positive parser returns the filled state; no parser plus beyond-end access can become `-ENOSPC`.

`blk_add_partitions()` checks scan eligibility, invokes `check_partition()`, handles native-capacity retry for beyond-EOD reads, rejects host-managed zoned bdev partitioning, emits a disk change uevent, then creates each nonzero parsed partition. `blk_add_partition()` validates partition start/size against capacity, optionally unlocks native capacity and retries, clamps broken overlong partitions to disk end, calls `add_partition()`, and triggers MD autodetect for RAID-flagged partitions.

`bdev_disk_changed()` runs under `disk->open_mutex`, rejects live partitions, syncs and invalidates `part0`, drops existing partitions, optionally zeros capacity for media invalidation, and rescans if capacity remains. Manual add/delete/resize helpers enforce live disk state, no partition support flags, no overlaps, and no openers for deletion.

## State and Persistence Behavior
The file manages in-memory partition devices in `disk->part_tbl`, `block_device` fields (`bd_start_sect`, sector count, read-only flag, meta info), sysfs devices, uevents, inode hash visibility, and access-beyond-EOD state. It does not write partition tables; it reflects parser results into kernel block-device state.

## Dependencies and Integration Points
It integrates with every parser, gendisk/device model, xarray partition table, bdev allocation/hash/invalidation, sysfs, blk trace attributes, MD autodetect, native capacity unlock driver callback, zoned block restrictions, and generic page-cache sector reads.

## Risks and Edge Cases
Parser order is security and compatibility sensitive because false positives stop probing. `add_partition()` has several lifetime steps: get disk device reference, allocate bdev, assign devt, copy metadata, suppress uevent until holder dir exists, insert xarray, and bdev hash. Errors must unwind devt, kobjects, devices, and references. Rescan rejects open partitions; failure to do so would invalidate live devices. Beyond-EOD handling may unlock native capacity and retry.

## Test Signals
Run partition parser image tests, hot rescan while partitions are open, BLKPG add/delete/resize tests, overlap checks, host-managed zoned disk scans, native-capacity unlock scenarios, sysfs/uevent metadata tests, MD RAID flag autodetect, fault-injection for allocation/device_add failures, and folio leak tests for `read_part_sector()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/core.c -->
