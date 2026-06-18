# sources/distributed-fs/ceph-client/block/blk-core.c

## Purpose
`blk-core.c` is the central block-layer submission, queue lifetime, queue entry, plugging, polling, and accounting implementation. It is the path upper layers use through `submit_bio()` and the path stacking drivers use through `submit_bio_noacct()`. It also initializes global block infrastructure such as `kblockd`, request queue cache allocation, debugfs, operation/status string helpers, and block tracepoints.

## Important APIs, Types, and Functions
Important exported APIs include `blk_queue_flag_set()`, `blk_queue_flag_clear()`, `blk_op_str()`, `errno_to_blk_status()`, `blk_status_to_errno()`, `blk_status_to_str()`, `blk_sync_queue()`, `blk_set_pm_only()`, `blk_clear_pm_only()`, `blk_put_queue()`, `blk_get_queue()`, `submit_bio_noacct()`, `submit_bio()`, `bio_poll()`, `iocb_bio_iopoll()`, `bdev_start_io_acct()`, `bio_start_io_acct()`, `bdev_end_io_acct()`, `bio_end_io_acct_remapped()`, `blk_lld_busy()`, `kblockd_schedule_work()`, `kblockd_mod_delayed_work_on()`, `blk_start_plug()`, `blk_check_plugged()`, `blk_finish_plug()`, and `blk_io_schedule()`. Internal helpers validate read-only writes, end-of-device access, partitions, zone append constraints, atomic write sizing, queue entry, and recursive submission ordering.

## Control Flow
The normal caller path is `submit_bio()` -> `bio_set_ioprio()` -> `submit_bio_noacct()`. `submit_bio_noacct()` validates NOWAIT support, encryption support, fault injection, read-only writes, end-of-device access, partition remapping, flush/FUA reduction, operation capability, zoned constraints, discard/secure erase/write-zeroes support, and atomic write sizes. If throttling does not consume the bio, it calls `submit_bio_noacct_nocheck()`.

`submit_bio_noacct_nocheck()` traces enqueue, starts blk-cgroup accounting, and uses `current->bio_list` to avoid recursive stack growth from stacked devices. It dispatches to `__submit_bio_noacct_mq()` for mq-only queues or `__submit_bio_noacct()` for queues with a driver `submit_bio` method. `__submit_bio()` wraps each dispatch in a plug, enters the queue when needed, rejects unsupported polled bios, calls either `blk_mq_submit_bio()` or `disk->fops->submit_bio()`, then exits the queue.

Queue lifetime is managed by refcounts, `q_usage_counter`, freeze/death checks, and RCU freeing. `blk_queue_enter()` and `__bio_queue_enter()` wait on `mq_freeze_wq` unless NOWAIT is requested or the queue/disk is dying.

## State and Persistence
State is in `struct request_queue`, `struct block_device`, `struct bio`, per-task `current->bio_list` and `current->plug`, partition statistics, queue flags, queue refcounts, and global `blk_debugfs_root`/`kblockd_workqueue`. There is no persistent on-disk state; durability semantics are enforced by request flags such as `REQ_PREFLUSH` and `REQ_FUA`, and by queue feature checks.

## Dependencies and Integration Points
This file integrates with blk-mq, blk-cgroup throttling, partition stats, runtime PM, inline encryption, zoned block devices, fault injection, BPF/block tracepoints, debugfs, request queue freeze/quiesce, and stacked block drivers. It calls into device-specific `gendisk` file operations and request queue operations while enforcing common block-layer policy.

## Risks
Critical risks are ordering and lifetime bugs around queue freeze/death, recursive bio submission, `current->bio_list`, queue refcounting, and bio completion on errors. Capability checks must reject unsupported operations before drivers see them. Encryption support checks must remain synchronized with blk-crypto capability semantics. Partition remap and EOD checks are safety-critical because silent sector misaddressing would corrupt data. Plug flushing must avoid deadlocks during schedule/reclaim by flushing callbacks, mq lists, and cached requests.

## Test Signals
Useful signals include block tracepoints (`block_bio_queue`, remap, completion), fault-injection via `fail_make_request`, NOWAIT error paths, zoned append boundary tests, partition remap tests, read-only write warnings, flush/FUA feature matrix tests, polled I/O support tests, cgroup throttling interaction, and queue freeze/removal race tests. Unit-level assertions are mostly `WARN_ON_ONCE()`, `BUG_ON()`, lockdep maps, and compile-time `BUILD_BUG_ON()` checks.
