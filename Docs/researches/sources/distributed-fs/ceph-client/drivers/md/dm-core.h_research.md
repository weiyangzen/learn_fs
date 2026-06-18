# sources/distributed-fs/ceph-client/drivers/md/dm-core.h

## Purpose
`dm-core.h` is an internal device-mapper header shared by core implementation files such as `dm.c`, `dm-rq.c`, and `dm-table.c`. It defines the private in-memory structures for mapped devices, tables, target I/O clones, original I/O tracking, and core flags. It is explicitly not an API for device-mapper targets to dereference directly.

## Important APIs, Types, And Functions
`struct mapped_device` contains suspend and table-device locks, the live table RCU pointer, queue type and request queue, holder/open counters, immutable-target fields, disk and DAX devices, pending I/O accounting, deferred and requeue work, event state, blk-mq tag set, statistics, internal suspend count, swap-bio throttling, mempools, kobject completion holder, SRCU I/O barrier, and optional zoned/IMA state. Flag bits include suspend/free/delete/no-flush/internal-suspend/post-suspend/emulated-zone-append/queue-stopped states.

`struct dm_table` contains the mapped device, queue mode, btree-style target index arrays, target array, immutable target type, integrity/singleton/flush-bypass booleans, open mode, devices list, event callback, mempools, and optional inline encryption profile. `struct dm_target_io` is embedded before each cloned bio and records clone flags, target bio number, original `dm_io`, target pointer, length pointer, old sector, and the clone bio. `struct dm_io` represents the original bio and embeds the first `dm_target_io`; it tracks accounting flags, status, original bio, mapped sector range, I/O count, and linked-list state for requeue.

Inline helpers include `dm_get_size`, `dm_get_stats`, `dm_emulate_zone_append`, `dm_table_get_target`, `dm_tio_flagged`, `dm_tio_set_flag`, `dm_tio_is_normal`, `dm_io_flagged`, `dm_io_set_flag`, `dm_get_completion_from_kobject`, and `dm_message_test_buffer_overflow`. External declarations include static keys for stats, swap bios, and zoned support; `dm_io_rewind`; `__dm_get_module_param`; global event state; and `dm_issue_global_event`.

## Control Flow And Integration Role
The header supports core mapping flow rather than implementing it directly. A submitted original bio is represented by `struct dm_io`; one or more `struct dm_target_io` clones point back to it and carry target-specific clone state. The table indexes sectors to targets. The mapped device maintains the active table behind RCU/SRCU and suspend locks, owns queues and deferred work, and emits events when table or target state changes. The flag helpers are used by core code to distinguish normal clone bios from duplicate bios and to track original bio accounting/splitting/statistics.

## State And Persistence Behavior
All structures here are volatile kernel state. Persistence is handled by specific targets or metadata libraries, not by the core header. The important state behavior is concurrency and lifetime: `mapped_device.map` must be dereferenced through the documented live-table helpers or under suspend locking; `pending_io`, `io_barrier`, deferred lists, and suspend flags coordinate table switching and suspension; kobject completion supports lifetime teardown; event counters and queues support userspace notification.

## Dependencies And Integration Points
The header includes block-mq, blk-crypto, jump labels, block trace events, `dm.h`, and `dm-ima.h`. It is consumed by device-mapper core source files and indirectly shapes how targets like `dm-cache-target.c` and `dm-clone-target.c` interact with core hooks. The cache target's per-bio data and target-bio-number logic rely on the core's cloned-bio model, and both cache and clone status/message paths feed into the buffer and event mechanisms declared here.

## Risks And Edge Cases
Because this is private core state, accidental target dereference of `mapped_device` or `dm_table` internals would be a layering violation and may break under core changes. Clone/original bio layout constants (`DM_TARGET_IO_BIO_OFFSET`, `DM_IO_BIO_OFFSET`) are sensitive to structure layout. Suspend, queue-stopped, internal suspend, and no-flush bits must remain consistent or bios can be lost, requeued incorrectly, or issued across a suspended table. Zoned emulation and optional inline encryption add configuration-dependent paths that need static-key and queue-state correctness.

## Test Signals
Core tests should watch suspend/resume with deferred bios, table replacement under I/O, request-based and bio-based target modes, clone splitting and requeue, stats accounting static-key toggles, global event notification, queue stopped/resumed transitions, zoned queue behavior, and message buffer overflow handling. Target-level tests for cache and clone indirectly exercise `dm_target_io` clone numbering, per-bio data allocation, flush/discard target counts, and end-I/O accounting.
