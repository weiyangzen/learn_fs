# sources/distributed-fs/ceph-client/include/linux/blkdev.h

## Purpose
`blkdev.h` is the main block-device interface header. It defines disk metadata, queue limits/features, request queue state, block device operations, queue/disk registration APIs, queue limit update helpers, zoned block helpers, plugging, discard/zeroout helpers, bdev open/claim/sync/freeze APIs, I/O accounting, and atomic-write capability helpers.

## Important APIs, Types, And Functions
Top-level constants include `BLKCG_MAX_POLS`, `DISK_MAX_PARTS`, `DISK_NAME_LEN`, partition metadata lengths, disk capability flags (`GENHD_FL_*`), disk events and event flags, integrity checksum types, and block open modes (`BLK_OPEN_*`). `struct gendisk` stores major/minor info, name, events, partition table, part0 bdev, fops, queue, private data, split bioset, flags/state bits (`GD_*`), open mutex/partition count, bdi/sysfs objects, optional zoned fields, cdrom info, badblocks, lockdep, disk sequence, open mode, independent access ranges, and rq-qos mutex. Helpers include `disk_openers()`, `disk_has_partscan()`, `dev_to_disk()`, `disk_to_dev()`, `disk_devt()`, and `blk_validate_block_size()`.

Queue features include write cache, FUA, rotational, add-random, I/O stats, stable writes, synchronous completion, nowait, DAX, polling, zoned, P2PDMA, skip tagset quiesce, atomic writes, and bcache stripe behavior. `struct queue_limits` records feature/flag bits, segment and boundary masks, sector and segment limits, block sizes and topology, discard/secure erase/write zeroes limits, zone append and write granularity, atomic write limits, stream limits, zone resource limits, DMA alignment/padding, and integrity profile.

`struct request_queue` stores driver data, elevator, mq ops, per-cpu software queues, flags, timeouts, depth, refcounts, hardware queue array, usage counter, merge state, queue lock, disk pointer, kobjects, limits, PM state, pm-only count, stats, rq-qos, id, nr_requests, crypto profile, timeout work, cgroup data, requeue state, tracing, flush queue/list, elevator/sysfs/limits locks, unused hctx list, freeze state/locks/waitqueue, tag set, debugfs entries, and RCU head.

`struct block_device_operations` defines driver callbacks: `submit_bio()`, `poll_bio()`, `open()`, `release()`, ioctl/compat ioctl, event checking, native capacity unlock, geometry, read-only change, disk free, swap notification, zone reporting, devnode, unique ID, owner, persistent reservation ops, and alternative GPT sector.

## Control Flow And State
Disk lifecycle flows through allocation (`blk_alloc_disk()` or blk-mq allocation), queue setup, `add_disk()`/`device_add_disk()`, queue registration, I/O submission, media change and capacity updates, then `del_gendisk()` and `put_disk()`. Queue limit updates use `queue_limits_start_update()` to lock and snapshot limits, then `queue_limits_commit_update()`/`queue_limits_commit_update_frozen()` or `queue_limits_cancel_update()`. Queue entry/exit protects active I/O while reconfiguration and zoned metadata updates occur.

I/O helper flow includes `submit_bio_noacct()`, bio splitting to limits, polling, plugging via `blk_start_plug()`/`blk_finish_plug()`, discard/secure erase/zeroout issuing, block-size validation, sync/invalidate/freeze/thaw, and I/O accounting start/end. Zoned helpers compute zone numbers, check straddling, decide when zone write plugging is required, and expose zone capacity/alignment. Atomic-write helpers check queue limits and partition start alignment before advertising min/max units.

State is persistent in `gendisk`, `block_device`, and `request_queue`. Many fields are protected by explicit locks: `open_mutex`, `limits_lock`, `elevator_lock`, `sysfs_lock`, `queue_lock`, freeze locks/waitqueues, cgroup mutex, and debugfs mutex. Feature and queue flags are accessed through bit helpers and limit fields.

## Dependencies And Integration Points
The header includes core kernel list, timer, workqueue, wait, bio, GFP, device number, RCU, percpu refcount, zoned block, scheduler, sbitmap, uuid, xarray, file, and lockdep headers. It integrates with `blk_types.h`, `blk-mq.h`, request queues, elevators, cgroups, rq-qos, tracing, inline crypto, integrity, zoned devices, filesystems/superblocks, partition scanning, sysfs/debugfs, PM, and device-mapper or stacking drivers.

## Risks And Test Signals
Risks include queue limit races, stale capacity/partition state, improper bdev claiming, incorrect feature inheritance in stacked devices, deadlocks between freeze and elevator/limits locks, zone write plugging omissions, unsafe racy feature disable helpers, request queue lifetime/refcount bugs, and config-gated fields used unguarded. Test signals should include disk add/remove, partition scanning suppression, queue limit validation/stacking, block-size changes, discard/zeroout paths, zoned writes and zone management, freeze/thaw/sync, bdev open/claim conflicts, PM-only mode, inline crypto registration, cgroup policy bitmaps, and atomic-write alignment on whole disks vs partitions.
