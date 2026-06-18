# sources/distributed-fs/ceph-client/block/blk-sysfs.c

## Purpose

`blk-sysfs.c` exposes request queue attributes under each disk's `queue/` sysfs directory and coordinates queue registration/unregistration with sysfs, debugfs, scheduler, crypto, independent access ranges, and writeback throttling. It is the user-visible control and inspection surface for many `queue_limits` and blk-mq runtime knobs.

## Important APIs, Types, And Functions

`struct queue_sysfs_entry` describes an attribute and either direct show/store callbacks or limit-aware show/store callbacks. Attribute callbacks cover `nr_requests`, `async_depth`, `read_ahead_kb`, max sectors/segments/discard/write-zeroes/zone append/atomic write sizes, block sizes, zone state, nomerges, rq affinity, polling, I/O timeout, write cache, rotational, iostats, stable writes, add_random, DAX/FUA display, passthrough stats, and WBT latency when enabled. The main kobject hooks are `queue_attr_show()`, `queue_attr_store()`, `queue_attr_visible()`, `blk_mq_queue_attr_visible()`, `blk_queue_ktype`, `blk_register_queue()`, and `blk_unregister_queue()`.

## Control Flow

Show callbacks either read queue fields directly or, for limit attributes, run under `q->limits_lock`. Limit store callbacks use `queue_limits_start_update()`, mutate the candidate limits, then call `queue_limits_commit_update_frozen()` so validation and copying happen while the queue is frozen. Direct stores use their own synchronization: `nr_requests` uses the tag-set `update_nr_hwq_lock`, freezes the queue, and updates scheduler or hardware tags; `async_depth` freezes and locks the elevator; `zoned_qd1_writes` freezes and quiesces; `rq_affinity` updates atomic flags; `io_timeout` stores jiffies; WBT latency uses `disk->rqos_state_mutex`.

Queue registration creates `queue` kobject under the disk device, registers blk-mq sysfs hctxs, creates debugfs directories, registers blk-mq debugfs, sets default zoned QD1 writes for rotational zoned mq devices, registers independent access ranges and crypto sysfs, sets the default elevator, marks the queue registered, enables default WBT, sends uevents, and switches `q_usage_counter` to percpu mode after init. Unregistration clears the registered flag, removes mq sysfs hctxs and crypto sysfs before mutable queue data disappears, unregisters access ranges, sends remove uevent, deletes the kobject, removes the elevator, and tears down debugfs.

## State And Persistence Behavior

Sysfs writes mutate in-memory queue limits, queue flags, request depth, async scheduler depth, read-ahead pages, timeout, WBT latency, and debugfs/sysfs registration state. Changes persist only for the lifetime of the queue unless a driver/userspace reapplies them. Registration state is tracked by `QUEUE_FLAG_REGISTERED` and `QUEUE_FLAG_INIT_DONE`.

## Dependencies And Integration Points

The file integrates with queue limits from `blk-settings.c`, blk-mq sysfs/debugfs helpers, elevator switching, WBT/rq-qos, blk-cgroup throttling headers, blktrace shutdown, crypto sysfs, independent access ranges, kobjects, and uevents. It is the bridge between userspace controls and the lower block core.

## Risks And Edge Cases

Lock ordering is critical. `queue_requests_store()` uses `down_write_trylock()` to avoid kernfs active-reference deadlocks during disk deletion. Limit stores must cancel updates on parse failure and commit frozen to avoid live I/O seeing inconsistent limits. Visibility callbacks hide zoned-only and mq-only attributes when unsupported. `queue_poll_store()` accepts but ignores writes for supported queues and rejects unsupported polling. Registration error paths must unwind debugfs, hctx sysfs, independent access ranges, crypto sysfs, and kobjects in the right order. Unregister must remove sysfs before queue internals can be modified or destroyed.

## Test Signals

Signals include sysfs read/write tests for every mutable attribute, invalid input parsing, queue deletion racing with sysfs writes, mq vs bio queue visibility, zoned attribute visibility, WBT latency updates, debugfs cleanup, scheduler default setup/removal, uevent ordering, and lockdep while changing `nr_requests`, limits, and zoned QD1 writes under active I/O.
