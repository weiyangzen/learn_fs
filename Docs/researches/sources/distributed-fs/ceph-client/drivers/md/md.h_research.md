<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/md.h -->
# sources/distributed-fs/ceph-client/drivers/md/md.h

## Purpose
Defines the internal contract for the Linux MD RAID core. It is the shared header used by MD personalities, bitmap/cluster helpers, sysfs/control paths, and device-mapper RAID integration to describe component devices, arrays, recovery state, metadata persistence, and request handling entry points.

## Important APIs, Types, And Functions
The key device structure is `struct md_rdev`, which records a member block device, metadata location, data offsets, role numbers, bad-block log, pending I/O counters, read/write error state, replacement/journal/PPL metadata, and flags from `enum flag_bits`. Inline helpers such as `is_badblock()`, `rdev_has_badblock()`, `is_rdev_broken()`, `rdev_dec_pending()`, and `rdev_blocked()` centralize bad-block and failed-device state checks.

The central array structure is `struct mddev`. It contains the active personality, gendisk and optional dm gendisk, disk list, superblock versions, event counters, reshape geometry, sync-thread state, recovery flags, sysfs nodes, bitmap configuration, bio sets, cluster hooks, suspend and reconfiguration locks, safemode timer state, and metadata update accounting. `enum sync_action`, `enum recovery_flags`, `enum mddev_flags`, and `enum md_ro_state` define the state machines used by recovery, reshape, degraded operation, clean/dirty metadata transitions, and read-only behavior.

`struct md_personality` is the personality vtable: `make_request`, `run`, `start`, `free`, `status`, error handling, hot add/remove, sync/reshape callbacks, resize/size methods, quiesce, takeover, consistency policy changes, and bitmap-sector translation. Public prototypes expose core operations such as `md_run()`, `md_start()`, `md_stop()`, `md_handle_request()`, `md_update_sb()`, `md_do_sync()`, `md_check_recovery()`, `md_error()`, `md_flush_request()`, and stacking-limit helpers.

## Control Flow
Array setup flows through `md_alloc()`, `mddev_init()`, metadata import via ioctl/sysfs helpers, and `md_run()`/`md_start()` invoking the selected personality callbacks. Normal I/O enters through `md_handle_request()` and then the personality `make_request` method. Writes are bracketed by `md_write_start()`, `md_write_inc()`, and `md_write_end()` so safemode, bitmap, superblock, and pending-write state can remain coherent.

Recovery control is represented by `mddev->recovery`, `last_sync_action`, `curr_resync`, `sync_thread`, and helpers such as `md_sync_action()`, `md_check_recovery()`, `md_reap_sync_thread()`, `md_idle_sync_thread()`, and freeze/unfreeze wrappers. Reconfiguration paths should suspend I/O, take `reconfig_mutex` through helpers such as `mddev_suspend_and_lock()`, update array/member state, then unlock and resume.

## State And Persistence
Persistent MD state includes superblock format fields, event counters, clean/dirty transitions, reshape position, member role and data offsets, bad-block logs, bitmaps, PPL/journal state, and cluster metadata. The header documents lock responsibilities: `reconfig_mutex` protects configuration, `open_mutex` protects stop/open races, `lock` protects superblock and bitmap transition fields, and `active_io`/`writes_pending` gate suspend and safemode behavior.

## Dependencies And Integration Points
The header depends on block-layer, kobject/sysfs, badblocks, workqueue/timer, percpu-ref, bio-set, trace, and RAID userspace ABI headers. It integrates MD personalities (`linear`, `raid0`, `raid1`, `raid4/5/6`, `raid10`), clustered MD, bitmap implementations, device-mapper RAID, sysfs controls, ioctl/autostart paths, and queue-limit stacking.

## Risks
The major risk is state-machine drift: flags in `md_rdev`, `mddev->flags`, `sb_flags`, and `recovery` are tightly coupled to metadata writes, sysfs state, and personality callbacks. Lock-order violations can deadlock with block-device open paths or recovery threads. Incorrect event or reshape fields can make arrays assemble stale data after a crash. Bad-block and `Blocked`/`FaultRecorded` handling are data-integrity sensitive because writes may be blocked until metadata records a failure.

## Test Signals
Useful signals include MD personality build coverage, mdadm assemble/create/stop/grow tests, degraded and replacement disk tests, bad-block injection, check/repair/resync sysfs exercises, suspend/resume and safemode clean/dirty transitions, dm-raid stacking tests, and lockdep/KASAN/KCSAN coverage around reconfiguration and recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/md.h -->
