<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/genhd.c -->
# sources/distributed-fs/ceph-client/block/genhd.c

## Purpose
`genhd.c` owns generic disk (`struct gendisk`) lifecycle, capacity publication, major-number registration, disk/partition sysfs and procfs visibility, disk statistics, uevents, dynamic device-number allocation, and teardown for block devices.

## Important APIs, Types, and Functions
- Capacity and notification: `set_capacity()`, `set_capacity_and_notify()`, `invalidate_disk()`, `set_disk_ro()`, `inc_diskseq()`.
- Registration: `__register_blkdev()`, `unregister_blkdev()`, `blk_alloc_ext_minor()`, `blk_free_ext_minor()`, `device_add_disk()`, `add_disk_fwnode()`, `del_gendisk()`.
- Disk allocation: `__alloc_disk_node()`, `__blk_alloc_disk()`, `put_disk()`.
- Partition scan and event flow: `disk_scan_partitions()`, `add_disk_final()`, `disk_uevent()`, `blk_mark_disk_dead()`.
- User visibility: sysfs attribute show/store functions, `block_class`, `disk_type`, `/proc/partitions`, `/proc/diskstats`, and optional legacy autoload functions.

## Control Flow
Drivers allocate disks through `__blk_alloc_disk()` or `__alloc_disk_node()`, which initialize biosets, backing-dev info, `part0`, the xarray partition table, cgroup state, zone resources, queue ownership, class/type, diskseq, and queue kobject. `device_add_disk()` calls `add_disk_fwnode()`, which serializes against blk-mq hardware queue updates when needed, then calls `__add_disk()`.

`__add_disk()` validates queue/fops combinations, assigns explicit or extended dev_t numbers, suppresses uevents, adds the device, allocates disk events, creates deprecated `/sys/block` links, holder/slave directories, registers the queue, registers bdi and sysfs links for visible disks, and stores a dev_t for hidden disks. `add_disk_final()` creates `part0`, scans partitions for visible disks with capacity, enables uevents, emits `KOBJ_ADD`, applies bdi limits, starts disk events, and marks `GD_ADDED`.

Teardown flows through `del_gendisk()` and `__del_gendisk()`: prevent new opens, notify filesystems, mark dead, drop partitions, remove bdi links, unregister queues, delete holder/slave dirs, remove device/sysfs links, freeze/drain queues, cancel throttled bios/work, exit rq-qos and blk-mq queue state as appropriate.

## State and Persistence Behavior
The persistent device data is elsewhere; this file manages kernel-visible state. Important mutable state includes `disk->state` bits (`GD_ADDED`, `GD_DEAD`, `GD_OWNS_QUEUE`, `GD_READ_ONLY`), capacity in `part0`, dynamic dev_t allocation in `ext_devt_ida`, major-name hash tables, partition xarray references, diskseq, sysfs/procfs exported counters, and badblocks sysfs storage via `disk->bb`.

## Dependencies and Integration Points
It integrates with block queue registration, blk-mq, rq-qos, blk-cgroup, blk-throttle, disk events, bdi, device model, sysfs/procfs, uevents, badblocks, blktrace, partition scanning, md autodetect indirectly, and optional legacy module autoload. It exports core driver-facing APIs for adding/removing disks and changing capacity/read-only state.

## Risks and Edge Cases
Device teardown ordering is delicate: bdi unregister must precede dev_t reuse, queue drain/freezing must prevent new I/O, hidden disks need valid `bd_dev` without user-visible registration, and blk-mq tag-set locks avoid hardware-queue update races. Capacity changes suppress initial/empty uevent noise. Per-cpu stat aggregation can observe transient negative inflight counts and clamps them. Major allocation is legacy and name-limited.

## Test Signals
Signals include hotplug add/remove tests, udev event diskseq correlation, partition scan/rescan races, dynamic minor exhaustion, hidden disk behavior, blk-mq queue teardown under I/O, sysfs attribute correctness, `/proc/diskstats` format, read-only uevents, capacity resize notifications, badblocks sysfs operations, and lockdep around `open_mutex` and tag-set locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/genhd.c -->
