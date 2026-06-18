# sources/distributed-fs/ceph-client/drivers/md/dm.c

## Purpose

`dm.c` is the generic device-mapper core driver. It registers the DM block major, creates and destroys mapped devices, owns gendisk/block-device operations, opens target devices, binds and swaps mapping tables, splits and maps bios to targets, handles completion/requeue/accounting, manages suspend/resume, exposes DAX and persistent reservation forwarding, and integrates zoned-device special handling.

## Important APIs, Types, and Functions

Major areas are module lifecycle (`dm_init`, `dm_exit`), device lifecycle (`dm_create`, `alloc_dev`, `dm_destroy`, `dm_get_md`, `dm_get`, `dm_put`), table binding (`__bind`, `__unbind`, `dm_swap_table`, `dm_setup_md_queue`), bio processing (`dm_submit_bio`, `dm_split_and_process_bio`, `__split_and_process_bio`, `__map_bio`, `clone_endio`, `dm_accept_partial_bio`, `dm_submit_bio_remap`), abnormal/flush operations (`__send_empty_flush`, `__process_abnormal_io`, `__send_zone_reset_all`), and suspend/resume (`dm_suspend`, `dm_resume`, internal variants). `struct mapped_device`, `struct dm_io`, and `struct dm_target_io` are defined in `dm-core.h` and implemented here.

## Control Flow

`dm_submit_bio()` obtains the live table under SRCU, queues bios during suspend, and otherwise calls `dm_split_and_process_bio()`. The splitter handles abnormal or zoned splitting, zone write plugging, NOWAIT allocation, preflush, `ZONE_RESET_ALL`, target-sized clone allocation, and remainder resubmission. `__map_bio()` invokes the target map method and interprets `DM_MAPIO_*` results. `clone_endio()` handles target end_io, zoned append completion, unsafe zoned requeue prevention, accounting, and final original bio completion.

Device setup allocates a gendisk and queue, initializes locks/workqueues/mempools/statistics, records the minor in an IDR, calculates queue limits, adds the disk, links holders, and initializes sysfs. Suspend blocks new I/O, flushes workqueues, optionally freezes filesystems and stops queues, waits for in-flight I/O, and calls target hooks. Resume calls target resume hooks, unblocks queued bios, restarts queues, and thaws.

## State and Persistence Behavior

DM core does not persist table definitions. Runtime state includes the minor IDR, mapped-device flags, live table pointer, holder/open counts, mempools, pending I/O counters, deferred/requeue lists, queue mode, uevents, geometry, stats, DAX object, and table-device references. Persistence semantics are mainly ordering and flush forwarding.

## Dependencies and Integration Points

It depends on DM internal headers, table/target/interface/sysfs/statistics code, block bio/gendisk/queue APIs, blk-mq, DAX, blk-crypto, SRCU/RCU, IDR, mempools, uevents, and zoned helpers from `dm-zone.c`. It exports block ops through `dm_blk_dops` and `dm_rq_blk_dops`.

## Risks and Test Signals

Subtle areas are split accounting, cloned bio lifetime, NOWAIT/polled paths, flush-with-data, duplicated bios, suspend/resume ordering, table reload mempools, and zoned write requeue prevention. Test create/remove, table swaps, normal and abnormal I/O, flushes, NOWAIT/polling, requeue, zoned splitting/reset-all, DAX, persistent reservations, deferred removal, and uevents.
