# File Research: sources/block-storage/linux-dm/drivers/md/dm.c

## Purpose
Implements the Device Mapper core mapped-device block driver: module initialization, minor allocation, mapped-device lifecycle, bio cloning and target dispatch, table binding/swapping, suspend/resume, event delivery, DAX forwarding, ioctl forwarding, persistent reservations, and block-device operations.

## Main Interfaces
- Module/device lifecycle: `dm_init()`, `dm_exit()`, `dm_create()`, `dm_destroy()`, `dm_destroy_immediate()`, `dm_get_md()`, `dm_get()`, `dm_put()`.
- Block operations: `dm_submit_bio()`, `dm_blk_open()`, `dm_blk_close()`, `dm_blk_ioctl()`, `dm_blk_getgeo()`.
- Table access and replacement: `dm_get_live_table()`, `dm_put_live_table()`, `dm_sync_table()`, `dm_swap_table()`, `__bind()`, `__unbind()`.
- I/O path: `alloc_io()`, `alloc_tio()`, `clone_bio()`, `__map_bio()`, `__split_and_process_bio()`, `clone_endio()`, `dm_io_dec_pending()`.
- Suspend/resume: `dm_suspend()`, `dm_resume()`, `dm_internal_suspend_noflush()`, `dm_internal_resume()`, fast internal suspend/resume variants.
- Device resources: `dm_get_table_device()`, `dm_put_table_device()`, `dm_alloc_md_mempools()`, `dm_free_md_mempools()`.
- Event and userspace notification: `dm_kobject_uevent()`, `dm_wait_event()`, `dm_uevent_add()`, `dm_issue_global_event()`.

## Control Flow
A bio submitted to a bio-based DM device obtains the live table under SRCU, checks suspend blocking, optionally applies queue splitting for abnormal operations, allocates a `dm_io`, finds the target for the current sector, clones or duplicates bios as required by flush/discard/write-same/write-zeroes/regular data handling, and calls the target `map()` method. Target return values decide whether DM submits the remapped bio, treats it as already submitted, kills it, or requeues it. Completion runs through `clone_endio()`, target `end_io()` callbacks, zoned endio handling, swap-bio throttling, and finally `dm_io_dec_pending()` to complete or requeue the original bio.

Table changes are done while suspended. `dm_swap_table()` validates the suspended state, calculates queue limits unless retaining limits for no-data-device tables, binds new mempools and queue restrictions, assigns `md->map` with RCU, then synchronizes readers before returning the old table for destruction.

Suspend first runs target presuspend hooks, optionally freezes the filesystem, sets `DMF_BLOCK_IO_FOR_SUSPEND`, synchronizes SRCU, stops request queues for request-based DM, flushes the deferred workqueue, and waits for in-flight bios or blk-mq requests. Resume calls target resume hooks, clears the block flag, flushes deferred bios, restarts request queues, and thaws the filesystem.

## State And Synchronization
Minor numbers and mapped-device lookup use `_minor_idr` protected by `_minor_lock`. Live table readers use `md->io_barrier` SRCU, with a fast RCU path for nonblocking limit inheritance. Device suspend state is encoded in `md->flags` bits such as `DMF_BLOCK_IO_FOR_SUSPEND`, `DMF_SUSPENDED`, `DMF_SUSPENDED_INTERNALLY`, `DMF_NOFLUSH_SUSPENDING`, `DMF_POST_SUSPENDING`, `DMF_DEFERRED_REMOVE`, `DMF_DELETING`, and `DMF_FREEING`.

Deferred bios are protected by `md->deferred_lock` and drained by `md->wq`. Table device references are protected by `table_devices_lock` and refcounted. Open counts and holders prevent deletion races. Swap I/O throttling uses `swap_bios_semaphore` plus `swap_bios_lock`. Suspend/resume is serialized by `suspend_lock`; queue mode by `type_lock`; uevent accumulation by `uevent_lock`.

## Integration Points
Integrates with DM target modules through `target_type` callbacks for `map`, `end_io`, `prepare_ioctl`, `iterate_devices`, DAX methods, suspend/resume hooks, and queue-limit setup. It initializes core DM subsystems including targets, linear/stripe targets, io, kcopyd, ioctl interface, statistics, uevents, zoned support, request-based DM, blk-crypto, sysfs, and IMA reset/measurement data. Block-layer integration includes gendisk registration, bio sets, blk-mq request queues, queue limits, DAX hosts, holder links, persistent reservation ops, and block trace remap events.

## Notable Behaviors
- Empty flushes are duplicated to every target that advertises flush bios; flushes with data reissue the data bio after preflush completion.
- Targets can call `dm_accept_partial_bio()` during `map()` to accept only part of a bio, causing the remainder to be split and submitted later.
- `REQ_NOWAIT` bios fail with would-block during suspend; readahead bios fail instead of being queued.
- Single-target ioctl forwarding retries `-ENOTCONN` unless a fatal signal is pending and requires `CAP_SYS_RAWIO` when a target reports subset access.
- DAX direct access and zero-page-range calls are routed to the live target covering the requested sector.
- Persistent reservation register is broadcast through `iterate_devices`; reserve/release/preempt/clear use the single-target ioctl-preparation path.
- Deferred remove is triggered when the final open reference closes and `DMF_DEFERRED_REMOVE` is set.

## Risks And Review Focus
- Suspend/resume correctness depends on precise ordering between target hooks, SRCU synchronization, queue stopping, deferred work flushing, and in-flight I/O waits.
- Bio clone lifetime is subtle because the first target I/O may be embedded in `dm_io`, while additional target I/Os are separate bioset allocations.
- Requeue during noflush suspend must not violate zoned sequential-write constraints.
- Table rebinding must keep queue limits, mempool front padding, immutable target metadata, and old table synchronization consistent.
- Ioctl and persistent reservation forwarding are intentionally limited to single-target mappings; relaxing that would need careful security and semantics work.
