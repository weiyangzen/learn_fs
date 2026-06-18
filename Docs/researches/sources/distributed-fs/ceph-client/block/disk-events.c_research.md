# sources/distributed-fs/ceph-client/block/disk-events.c

Purpose: monitors disk events such as media change and eject request, provides sysfs controls for supported events and polling interval, emits uevents, and coordinates synchronous event clearing with asynchronous polling work.

Important APIs and functions: private `struct disk_events` stores the disk, lock, block depth, pending and clearing masks, poll interval, and delayed work. Public functions are `disk_block_events()`, `disk_unblock_events()`, `disk_flush_events()`, `disk_check_media_change()`, `disk_force_media_change()`, `disk_alloc_events()`, `disk_add_events()`, `disk_del_events()`, and `disk_release_events()`. Sysfs attributes are `events`, `events_async`, and `events_poll_msecs`; the module parameter is `block.events_dfl_poll_msecs`.

Control flow: disk allocation creates an initially blocked `disk_events`. Adding the disk links it to the global list and unblocks, optionally scheduling immediate work. Work calls the driver's `check_events()` with a clearing mask, accumulates new pending bits, reschedules polling if enabled, increments disk sequence for media changes, and emits uevents when configured. Synchronous media checks block background work, merge outstanding clearing masks, call the driver, unblock, and return pending bits to the caller.

State and persistence: per-disk state tracks pending events already reported, clearing requests, nested block count, and poll interval. Global state tracks all event-enabled disks and the default polling interval. State is runtime-only; sysfs/module parameters change live behavior.

Dependencies and integration points: depends on gendisk event flags, driver `fops->check_events`, system freezable power-efficient workqueue, kobject uevents, disk sequence counters, block device invalidation through `bdev_mark_dead()`, open mutex conventions for flushing masks, and disk lifecycle hooks.

Risks and test signals: races between `disk_flush_events()` and `disk_clear_events()`, balanced block/unblock nesting, delayed work cancellation, and uevent suppression by flags are key. Test removable media change, eject request, polling disabled/default/device-specific intervals, concurrent sysfs poll writes, disk deletion while work is pending, forced media change invalidation, and partition rescan flagging.
