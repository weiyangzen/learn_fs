# sources/distributed-fs/ceph-client/drivers/md/md.c lines 1-10020

## Scope And Purpose

This chunk is the main body of the Linux MD core driver implementation through the beginning of spare-selection helpers. It defines the global MD module state, sysctl tunables, block-device operations, md device allocation and lifetime handling, rdev import/binding/removal, internal metadata formats, sysfs and ioctl control surfaces, bitmap and cluster integration hooks, array run/stop transitions, md kernel thread management, `/proc/mdstat` reporting, write accounting, flush/discard helpers, and the primary resync/recovery/reshape loop.

The code is not a RAID personality implementation by itself. Instead, it provides the shared framework that personalities such as raid0, raid1, raid5, raid10, linear, and dm-raid plug into through `struct md_personality`. The chunk owns array-level state transitions, metadata persistence, and user-visible control paths, while delegating layout-specific I/O, resize, reshape, recovery, error handling, and status formatting to the selected personality.

This is chunk 1 of 2 for `drivers/md/md.c`. It ends just after helper predicates used by spare removal/addition; the remaining recovery scheduler, reboot handling, autodetect teardown, and module init/exit paths continue in the next chunk.

## Important APIs, Types, And Functions

Global registration, tunables, and eventing:

- `action_name[]` maps `enum sync_action` values to sysfs strings for `sync_action`, `last_sync_action`, and recovery logs.
- `md_submodule` is an xarray registry for MD personalities, bitmap implementations, and cluster ops. `register_md_submodule()` and `unregister_md_submodule()` are the exported registration APIs.
- `/proc/sys/dev/raid/` sysctls are backed by `sysctl_speed_limit_min`, `sysctl_speed_limit_max`, and `sysctl_sync_io_depth`; `speed_min()`, `speed_max()`, and `sync_io_depth()` apply per-array overrides when present.
- Module parameters and globals include `start_readonly`, `create_on_open`, `legacy_async_del_gendisk`, `check_new_feature`, and `start_dirty_degraded`.
- `md_new_event()` increments `md_event_count` and wakes `md_event_waiters`, driving `poll()` behavior for `/proc/mdstat`.
- `all_mddevs` plus `all_mddevs_lock` is the global list of live md devices. `mddev_get()`, `mddev_put()`, and `mddev_put_locked()` protect deletion against open/sysfs/proc references.

I/O submission and suspension:

- `md_submit_bio()` is the `submit_bio` entry in `md_fops`. It rejects missing/broken personalities, splits bios to queue limits, enforces read-only write rejection, clears `REQ_NOMERGE`, and delegates to `md_handle_request()`.
- `md_handle_request()` gates normal I/O through suspend checks and the `active_io` percpu reference, then calls `mddev->pers->make_request()`. It handles `REQ_NOWAIT` suspension failures and retries when the personality asks for suspend preparation.
- `mddev_suspend()` kills the `active_io` percpu ref, waits for in-flight I/O to drain, wakes interrupted reshape waiters through `prepare_suspend`, increments the nested suspend count, and enters `memalloc_noio` context. `mddev_resume()`/`__mddev_resume()` reverse this and optionally mark recovery needed.
- `is_suspended()` blocks all I/O when `active_io` is dying and blocks writes inside the configured `suspend_lo`/`suspend_hi` sector range.
- `md_flush_request()` sends `REQ_PREFLUSH` bios to every non-faulty active rdev, chains completions through `md_end_flush()`, and then lets data I/O continue without the flush flag.

Device and rdev lifetime:

- `mddev_init()` initializes biosets, percpu refs, locks, wait queues, timers, work items, list heads, default reshape/resync fields, and bitmap defaults. `mddev_destroy()` frees those primitives.
- `mddev_alloc()` creates the in-memory `struct mddev`; `md_alloc()` allocates the gendisk, registers it with the block layer, initializes the md sysfs kobject, and adds the mddev to `all_mddevs`.
- `mddev_delayed_delete()`, `md_kobj_release()`, and `md_free_disk()` coordinate `kobject_put()`, `del_gendisk()`, `put_disk()`, and final `mddev_free()` cleanup. `legacy_async_del_gendisk` controls whether disk deletion occurs from md kobject release or earlier after stop.
- `md_rdev_init()`, `md_import_device()`, `bind_rdev_to_array()`, `md_kick_rdev_from_array()`, `export_rdev()`, and `export_array()` cover member-device allocation, block-device open, superblock import, kobject/sysfs registration, holder links, RCU list binding, removal, badblocks cleanup, and file release.
- `find_rdev()`, `md_find_rdev_rcu()`, and `md_find_rdev_nr_rcu()` locate member devices by `dev_t` or descriptor number.

Metadata handling:

- `struct super_type` abstracts metadata versions with `load_super`, `validate_super`, `sync_super`, `rdev_size_change`, and `allow_new_offset`.
- `super_types[]` contains version `0.90.0` and `md-1` handlers. `sync_super()` dispatches either an externally supplied `mddev->sync_super` or the built-in handler.
- Version 0.90 handlers are `super_90_load()`, `super_90_validate()`, `super_90_sync()`, `super_90_rdev_size_change()`, and `super_90_allow_new_offset()`. They parse the end-of-device 0.90 superblock, verify magic/version/checksum/UUID/event counters, map `mdp_disk_t` state bits into rdev flags, update old-format disk descriptors, and enforce the 4 TB metadata limit for redundant arrays.
- Version 1.x handlers are `super_1_load()`, `super_1_validate()`, `super_1_sync()`, `super_1_rdev_size_change()`, and `super_1_allow_new_offset()`. They handle 1.0/1.1/1.2 superblock placement, little-endian checksums, feature maps, bad-block logs, PPL/multiple-PPL metadata, journal roles, replacement flags, reshape/new-offset state, configurable logical block size, and freshness checks against the newest device.
- `read_disk_sb()`, `sync_page_io()`, `md_write_metadata()`, `super_written()`, and `md_super_wait()` implement metadata reads and asynchronous metadata writes, including superblocks, badblock pages, bitmap superblocks, flush/FUA semantics, pending write accounting, failfast retry signaling through `MD_SB_NEED_REWRITE`, and md error handling on failed metadata I/O.
- `md_update_sb()` is the central metadata persistence routine. It advances or rolls back the event counter, updates in-memory superblocks, writes metadata and changed badblock logs, coordinates clustered metadata locks, writes bitmap metadata, handles clean/dirty transitions, acknowledges badblocks, clears blocked flags, and repeats if the in-sync state or pending change bits changed mid-flight.

Bitmap, write-behind, and serialization:

- `mddev_set_bitmap_ops_nosysfs()`, `md_bitmap_create_nosysfs()`, `md_bitmap_create()`, `md_bitmap_destroy_nosysfs()`, `md_bitmap_destroy()`, and `md_bitmap_set_none()` bind bitmap submodule ops, create/load/destroy bitmap state, add/remove bitmap sysfs groups, and fall back to the on-disk bitmap version when mdadm did not set `bitmap_type`.
- `md_bitmap_get_id_from_sb()` reads a bitmap superblock from an in-sync device to select classic bitmap versus lockless bitmap ops when the default does not match disk metadata.
- `md_bitmap_start()` and `md_bitmap_end()` wrap write/discard accounting around cloned bios, calling bitmap ops after personality-specific sector translation.
- `mddev_create_serial_pool()` and `mddev_destroy_serial_pool()` manage per-rdev collision-check arrays and a mempool used for RAID1 write-behind serialization on multi-queue write-mostly devices. `serialize_policy_store()` exposes forced serialization through sysfs.

Sysfs control surfaces:

- `struct rdev_sysfs_entry`, `rdev_default_attrs[]`, `rdev_attr_show()`, and `rdev_attr_store()` implement per-member attributes under `md/dev-*`: `state`, `errors`, `slot`, `offset`, `new_offset`, `size`, `recovery_start`, `bad_blocks`, `unacknowledged_bad_blocks`, `ppl_sector`, and `ppl_size`.
- `state_store()` handles member actions such as `faulty`, `remove`, `writemostly`, `blocked`, `insync`, `failfast`, `write_error`, `want_replacement`, `replacement`, `re-add`, and `external_bbl`. It can suspend the array, update metadata, invoke clustered removal/gather paths, or trigger recovery.
- `slot_store()` assigns or removes a raid slot, calling personality hot-add/hot-remove hooks for active arrays and maintaining `rdN` sysfs links.
- Offset and size stores enforce reshape direction, metadata-space constraints, external-overlap checks, journal restrictions, and no-active-array conditions before updating rdev geometry.
- `struct md_sysfs_entry`, `md_default_attrs[]`, `md_redundancy_attrs[]`, `md_attr_show()`, and `md_attr_store()` implement md-level attributes including `level`, `new_level`, `bitmap_type`, `layout`, `raid_disks`, `uuid`, `chunk_size`, `component_size`, `resync_start`, `metadata_version`, `new_dev`, `safe_mode_delay`, `array_state`, `reshape_position`, `reshape_direction`, `array_size`, `max_read_errors`, `consistency_policy`, `fail_last_dev`, `serialize_policy`, `logical_block_size`, and redundancy-only sync attributes.
- `array_state_store()` maps string states `clear`, `inactive`, `readonly`, `read-auto`, `clean`, and `active` into stop, read-only, read-auto, restart, clean, or run operations.
- `action_store()` maps `sync_action` writes to freeze/idle/reshape/recover/check/repair/resync requests and uses `MD_RECOVERY_*` bits plus md thread wakeups to start or stop background work.
- `level_store()`, `layout_store()`, `raid_disks_store()`, and `chunk_size_store()` support online personality takeover or reshape checks when the active personality allows it.
- `metadata_store()`, `new_dev_store()`, `bitmap_store()`, `size_store()`, `array_size_store()`, `consistency_policy_store()`, and `lbs_store()` cover metadata type selection, sysfs device add, bitmap dirty-bit injection, component resize, exported array size override, consistency policy selection, and logical block size compatibility signaling.

Array run, stop, and configuration:

- `md_run()` validates member devices and metadata, loads a personality, checks metadata/data overlap, handles read-only members, runs the personality, creates bitmaps, creates write-behind serialization resources, adds redundancy sysfs attributes, links active rdevs, sets safemode defaults, persists metadata, and marks recovery needed.
- `do_md_run()` wraps `md_run()`, loads bitmap contents, calls clustered write enabling, starts personality post-run tasks through `md_start()`, wakes sync work, publishes capacity, clears `MD_NOT_READY`, and sends uevents/sysfs notifications.
- `restart_array()` transitions an existing readonly/read-auto array to read-write, rejecting missing journals and read-only members.
- `md_set_readonly()`, `do_md_stop()`, `md_stop_writes()`, `md_stop()`, `__md_stop_writes()`, `__md_stop()`, `mddev_detach()`, and `md_clean()` freeze recovery, stop sync threads, quiesce personalities, flush bitmaps, mark metadata clean, detach threads/queues, destroy bitmaps, free personality private state, export rdevs, clear array configuration, and update capacity/events.
- `md_set_array_info()` handles both new array creation and assembly metadata-version selection. `update_array_info()`, `update_size()`, and `update_raid_disks()` implement controlled online changes with personality `resize` and `check_reshape` hooks.
- `md_add_new_disk()`, `hot_add_disk()`, `hot_remove_disk()`, and `set_bitmap_file()` provide ioctl-era control paths for assembling arrays, adding spares, removing devices, adding journal devices, clustered disk add acknowledgements, and deprecated file-backed bitmaps.

Block-device, ioctl, and proc interfaces:

- `md_fops` exposes `.submit_bio`, `.open`, `.release`, `.ioctl`, optional `.compat_ioctl`, `.getgeo`, `.check_events`, `.set_read_only`, and `.free_disk`.
- `md_ioctl_valid()`, `md_ioctl_need_suspend()`, `__md_set_array_info()`, and `md_ioctl()` implement legacy ioctl authorization and dispatch for `RAID_VERSION`, `GET_ARRAY_INFO`, `GET_DISK_INFO`, `SET_DISK_FAULTY`, `GET_BITMAP_FILE`, `SET_ARRAY_INFO`, `RESTART_ARRAY_RW`, `STOP_ARRAY`, `STOP_ARRAY_RO`, `HOT_REMOVE_DISK`, `ADD_NEW_DISK`, `CLUSTERED_DISK_NACK`, `HOT_ADD_DISK`, `RUN_ARRAY`, and `SET_BITMAP_FILE`.
- `md_open()` and `md_release()` maintain `openers`, reject `MD_CLOSING`, and hold mddev references. `mddev_set_closing_and_sync_blockdev()` prevents concurrent open/write while stopping or switching read-only.
- `/proc/mdstat` is implemented by `md_seq_ops`, `md_seq_show()`, `status_personalities()`, `status_unused()`, `status_resync()`, `md_bitmap_status()`, and `mdstat_poll()`. It reports personalities, active/inactive arrays, rdev roles and flags, metadata type, personality status, bitmap status, recovery progress, estimated finish, and event-driven poll readiness.

Threading, recovery, and write accounting:

- `md_register_thread()`, `md_unregister_thread()`, `md_thread()`, `__md_wakeup_thread()`, and `md_wakeup_thread_directly()` manage per-array kernel threads with wait queues, timeout-driven wakeups, RCU-protected thread pointers, and kthread stop/park behavior.
- `md_error()` delegates failures to the personality `error_handler`, marks recovery interruption/need bits, notifies sysfs, queues event work, and emits mdstat events.
- `md_write_start()`, `md_write_inc()`, `md_write_end()`, and `md_allow_write()` manage dirty-state transitions, read-auto promotion, `writes_pending`, safemode timers, metadata clean/dirty persistence, and write blocking until dirty metadata has reached disk.
- `md_account_bio()`, `md_clone_bio()`, `md_end_clone_io()`, `md_submit_discard_bio()`, and bitmap start/end helpers provide clone-based I/O accounting, active I/O references, stats accounting, discard chaining, and completion propagation to original bios.
- `md_sync_action()`, `md_get_active_sync_action()`, `md_sync_action_by_name()`, `md_sync_action_name()`, `stop_sync_thread()`, `md_idle_sync_thread()`, `md_frozen_sync_thread()`, `md_unfrozen_sync_thread()`, and `mddev_start_reshape()` define recovery state-machine selection and sysfs control semantics.
- `md_do_sync()` is the main background sync/recover/check/repair/reshape loop. It coordinates with clustered resync locks, avoids simultaneous resync on arrays sharing physical disks, initializes progress counters, calls `pers->sync_request()` across the selected sector range, honors bitmap skip ranges and resync min/max bounds, throttles by speed limits and foreground I/O idleness, periodically checkpoints progress into metadata state, waits for outstanding recovery I/O, finishes reshape/recovery bookkeeping, and marks `MD_RECOVERY_DONE`.
- `md_done_sync()` and `md_sync_error()` are exported helpers for personalities to account completed sync sectors or request interruption.

Queue limits, clustering, and autodetect:

- `md_init_stacking_limits()`, `mddev_stack_rdev_limits()`, `mddev_stack_new_rdev()`, and `mddev_update_io_opt()` stack queue limits, integrity profiles, logical block size constraints, write cache/FUA/NOWAIT features, and reshape-driven optimal I/O size.
- `get_cluster_ops()`, `put_cluster_ops()`, `md_setup_cluster()`, and `md_cluster_stop()` load and reference the md-cluster submodule and call its `join`/`leave` methods.
- Non-module boot autodetect code in this chunk imports pending 0.90 rdevs, groups them by superblock UUID, allocates the requested md unit, binds candidates, starts arrays, and exports unused candidates.

## Control Flow And Runtime Behavior

Normal data I/O starts at `md_submit_bio()`. The bio is validated against array presence, broken-state, queue limits, and read-only mode. `md_handle_request()` then blocks or fails the bio if the mddev is suspended, obtains a live `active_io` reference, calls the personality `make_request()`, and drops the reference. If the personality cannot accept the bio because suspend/reconfiguration is in progress, the core retries after waiting or returns false for dm-raid suspend preparation.

Array suspension is intentionally separate from `reconfig_mutex`. `mddev_suspend()` asserts the reconfiguration mutex is not held, kills `active_io`, wakes reshape waiters if needed, waits for all normal I/O references to drain, increments the suspend nesting counter, and enters no-I/O reclaim scope. This lets sysfs/ioctl paths change geometry, rdev state, or suspend ranges without racing in-flight requests. Resume decrements nesting, resurrects `active_io` when the outer suspend ends, wakes waiters, and can mark recovery needed.

Metadata updates flow through bit flags in `mddev->sb_flags`. Writers set `MD_SB_CHANGE_CLEAN`, `MD_SB_CHANGE_DEVS`, and/or `MD_SB_CHANGE_PENDING`; `md_update_sb()` consumes them under `mddev->lock`, updates event counters and per-rdev in-memory superblocks, writes superblocks/badblock logs/bitmap metadata, waits for completion, and repeats if pending bits or in-sync state changed. For clustered arrays, metadata update begin/cancel/finish calls surround the update and `does_sb_need_changing()` can skip a no-op after a remote node updated metadata.

The clean/dirty transition is driven by writes and safemode. `md_write_start()` promotes `MD_AUTO_READ` to `MD_RDWR`, increments `writes_pending`, marks a clean array dirty, sets metadata pending bits, wakes the md thread, and waits for the dirty superblock state before allowing writes when internal metadata exists. `md_write_end()` drops `writes_pending` and arms the safemode timer. `set_in_sync()` can later switch the array clean only after `writes_pending` drains.

Starting an array is a staged operation. Sysfs `array_state=active` or ioctl `RUN_ARRAY` calls `do_md_run()`, which invokes `md_run()` to analyze superblocks if needed, select a personality, check member geometry, run the personality, create bitmap/serialization resources, publish redundancy sysfs attributes, link active rdevs, update superblocks, and mark recovery needed. `do_md_run()` then loads bitmap contents, calls post-run personality startup, wakes sync work, sets capacity, emits uevents, and clears `MD_NOT_READY`.

Stopping and read-only transitions freeze background work first. `do_md_stop()` sets `MD_RECOVERY_FROZEN`, stops the sync thread, rejects the stop if sysfs removal or recovery is still active, flushes/marks metadata clean, detaches personality state, optionally removes redundancy attributes, unlinks rdev role symlinks, drops capacity, and on full clear exports all rdevs and resets mddev fields. `md_set_readonly()` follows a similar freeze, stop-sync, clean-metadata path but keeps the array assembled and flips the gendisk read-only state.

User configuration reaches the same primitives through two surfaces. Modern sysfs attributes call per-attribute store functions under mddev references and often suspend plus lock for destructive operations. Legacy ioctls validate admin capability, optionally set `MD_CLOSING`, choose suspend-and-lock for member/bitmap/config changes, and call the same add/remove/run/stop/update helpers. Both paths notify sysfs and mdstat through `md_new_event()` and `sysfs_notify_dirent_safe()`.

The resync thread starts from `md_start_sync()` in a work item outside this chunk's end boundary, but this chunk contains the action selection and main loop. `md_do_sync()` derives the current action from `MD_RECOVERY_*` bits and existing reshape/recovery offsets, coordinates with clustered locks, delays if another mddev shares underlying disks unless `parallel_resync` is set, chooses the sector start and max range, then repeatedly calls `pers->sync_request()`. It updates progress fields used by sysfs and `/proc/mdstat`, throttles to speed limits using foreground I/O idleness, checkpoints metadata periodically, and completes with action-specific cleanup in `md_finish_sync()`.

`/proc/mdstat` reporting is event driven but lock-aware. The seq iterator holds `all_mddevs_lock` while selecting mddevs, obtains an mddev reference, drops the global lock while formatting array details, holds `bitmap_info.mutex` to prevent bitmap teardown during status, and reacquires the global lock before continuing. Pollers compare their stored event count to `md_event_count`.

## State And Persistence Behavior

Persistent on-disk state is maintained through MD superblocks, bitmap superblocks/bits, bad-block logs, PPL/journal metadata fields, and event counters. Version 0.90 metadata stores array shape, disk descriptors, event counters, recovery checkpoint, bitmap-present flag, and limited reshape state near the end of the device. Version 1.x metadata stores richer feature bits, device roles, bad-block log descriptors, journal/PPL fields, recovery offset, reshape/new-offset details, and logical block size.

In-memory array state is centered on `struct mddev`: selected personality, rdev list, gendisk, array/device sizes, raid geometry, metadata version, UUID, event counter, dirty/clean state, reshape fields, recovery flags, current sync progress, bitmap info, cluster ops, sysfs kernfs nodes, openers/active refs, safemode timer, work items, and queue/bioset resources. `md_clean()` resets most of these fields on final stop while preserving only closing semantics needed for deletion mode.

Member state is centered on `struct md_rdev`: block-device handles, descriptor and raid slot numbers, data/superblock offsets, sectors, badblocks, PPL fields, superblock pages, pending I/O count, corrected/read error counters, journal/replacement/write-mostly/failfast/faulty/in-sync flags, and per-rdev sysfs nodes. Removal detaches the rdev from the RCU list, unlinks holders/sysfs links, clears badblocks and serialization resources, then delays kobject deletion until after `reconfig_mutex` is released.

Runtime state changes are protected by a mix of locks and references. `all_mddevs_lock` protects the global mddev list and active reference acquisition; `reconfig_mutex` serializes configuration changes; `suspend_mutex` serializes nested suspend/resume; `open_mutex` protects openers and closing transitions; `mddev->lock` protects clean/dirty, recovery, and selected geometry state; `active_io` and `writes_pending` percpu refs coordinate normal I/O and dirty-state detection; RCU protects rdev and md thread pointer traversal.

Bitmap state can be internal metadata-backed, file-backed, lockless, clustered, or absent depending on `bitmap_id`, `bitmap_ops`, `bitmap_info.file`, `bitmap_info.offset`, and feature detection. The core persists bitmap superblock updates before rdev superblock writes and flushes bitmap dirty bits on stop. `bitmap_type` is persistent only through later superblock updates when the relevant metadata feature bits are written.

State notification is explicit. Most meaningful changes call `md_new_event()` for mdstat pollers and `sysfs_notify_dirent_safe()` for array state, rdev state, sync action, sync completed, degraded, and level attributes. Capacity changes call `set_capacity_and_notify()`, and array creation/run/stop sends kobject uevents.

## Dependencies And Integration Points

Kernel subsystems used here include the block layer (`gendisk`, `bio`, queue limits, holder links, discard helpers, integrity stacking, disk events), sysfs/kobject/kernfs, procfs/seq_file/poll, module and parameter APIs, sysctl, kthreads and wait queues, workqueues and timers, RCU, spinlocks/mutexes, percpu refs, badblocks, file and bdev open APIs, compat ioctl conversion, random UUID generation, and reboot/autodetect support.

Internal MD dependencies include `md.h`, `md-bitmap.h`, `md-cluster.h`, the md public uapi headers `md_p.h` and `md_u.h`, and detection support from `linux/raid/detect.h`. The code calls many helpers/macros defined outside this chunk, including `mddev_lock()`, `mddev_suspend_and_lock()`, `mddev_unlock_and_resume()`, `sysfs_link_rdev()`, `sysfs_unlink_rdev()`, `mdname()`, `md_is_rdwr()`, `mddev_is_dm()`, `mddev_is_clustered()`, bitmap operation methods, cluster operation methods, and personality callbacks.

Personality integration is the main extension point. The selected `struct md_personality` supplies `make_request`, `run`, `start`, `free`, `status`, `size`, `resize`, `sync_request`, `error_handler`, `hot_add_disk`, `hot_remove_disk`, `quiesce`, `prepare_suspend`, `takeover`, `check_reshape`, `start_reshape`, `finish_reshape`, `bitmap_sector`, and `change_consistency_policy` hooks. The MD core enforces common sequencing and metadata rules around those hooks.

dm-raid integration is handled with conditional behavior. Several paths skip gendisk queue-limit updates or sysfs bitmap groups for dm-backed mddevs; `md_handle_request()` can return false to let dm prepare suspend; `md_run()` preserves dm recovery state until resume; `do_md_run()` avoids some disk-capacity behavior for clustered/dm cases; and `md_stop()` is exported for dm-raid.

Cluster integration is optional and dynamic. `md_setup_cluster()` loads `md-cluster`, calls `join`, disables safemode delay, and later paths call cluster ops for metadata updates, disk add/remove acknowledgements, bitmap locks, size updates, resync locks, and remote-progress reporting.

Userspace integration is broad: `/sys/block/md*/md/*`, `/sys/block/md*/md/dev-*/*`, `/proc/mdstat`, legacy ioctls used by mdadm, module parameters such as `new_array`, and boot-time autodetection all enter this code. The comments also show compatibility constraints with older mdadm and older kernels, especially around `create_on_open`, asynchronous `del_gendisk`, bitmap version selection, and logical block size metadata.

## Risks And Edge Cases

- `mddev_suspend()` must not run with `reconfig_mutex` held. Violating this ordering can deadlock because normal I/O and metadata update paths may need reconfiguration progress to drain.
- `md_update_sb()` has several retry paths. Failfast metadata write errors can set `MD_SB_NEED_REWRITE`; concurrent clean/dirty changes can force a repeat; clustered metadata can be canceled if a remote update made the local write unnecessary.
- Event counter management deliberately sometimes decrements instead of increments for clean transitions when `can_decrease_events` allows it. Incorrect changes here can make stale disks look current or cause unnecessary resync.
- Freshness checks are subtle. Version 1.x assembly may consult the freshest superblock for an rdev's role when the rdev's event counter is one behind, specifically to avoid accepting a disk that was marked faulty just before a crash.
- 0.90 metadata cannot represent non-zero data offsets, large redundant devices beyond its limit, or all reshape details. The `allow_new_offset` and size-change handlers reject cases that newer metadata may allow.
- Sysfs store functions often perform multi-step operations after breaking active protection or after dropping `reconfig_mutex` to avoid kernfs deadlocks. Moving sysfs removal under the wrong lock can deadlock with concurrent attribute access.
- `state_store("remove")`, `slot_store("none")`, `hot_remove_disk()`, and `remove_and_add_spares()` interact through personality hot-remove hooks and raid slot state. Removing a device with pending I/O, unrecorded fault state, or active journal role is intentionally blocked.
- `md_rdev_overlaps()` is only a best-effort guard for external metadata overlap mistakes. The comment acknowledges it is not a hard race-proof guarantee against concurrent userspace changes.
- `bitmap_type` and bitmap creation fallback depend on reading bitmap superblocks from an in-sync device. If no readable in-sync device exists, bitmap ops may remain mismatched and array start can fail.
- File-backed bitmap support is deprecated and requires a writable regular file with a single writer. The path is protected but still carries operational risk compared with internal bitmaps.
- `md_allow_write()` waits for dirty metadata before allocations that might recurse into block I/O. Calling write paths without marking the array dirty first can deadlock or allow writes before metadata records the dirty state.
- `md_do_sync()` throttling depends on I/O accounting and partition-level statistics. If accounting is unavailable or misleading, foreground I/O friendliness may be inaccurate.
- Shared-physical-disk resync avoidance compares member `bd_disk` pointers and uses mddev address ordering to yield. The algorithm prevents common contention but can delay recovery unexpectedly when arrays share disks; `sync_force_parallel` bypasses it.
- Logical block size support has forward-compatibility warnings. Arrays assembled from old kernels may have zero stored LBS, and writing current LBS intentionally makes the array incompatible with older kernels lacking the feature.
- `legacy_async_del_gendisk` changes deletion timing and `MD_CLOSING` clearing behavior. Mixed userspace expectations around old mdadm behavior are explicitly called out by warning text.

## Test And Validation Signals

- Build with MD core, relevant RAID personalities, bitmap variants, cluster support, compat ioctl support, and badblocks enabled. Compile-time issues should catch missing callbacks, changed enum values, and queue-limit API drift.
- Create arrays through both sysfs `new_array`/`new_dev`/`array_state` and legacy ioctl/mdadm paths, covering metadata `0.90`, `1.0`, `1.1`, `1.2`, `none`, and `external:*`.
- Exercise normal reads/writes through md block devices, including `MD_RDONLY`, `MD_AUTO_READ`, transition to `MD_RDWR`, `REQ_NOWAIT` during suspend, flush-only bios, discard bios, and queue-limit splitting.
- Validate suspend/resume by writing `suspend_lo`/`suspend_hi`, changing member geometry, and ensuring writes in-range block while reads and out-of-range writes behave as expected.
- Force metadata writes, failfast metadata I/O errors, badblock log changes, bitmap superblock updates, and clustered metadata update begin/cancel/finish paths; verify event counters, `MD_SB_CHANGE_*` flags, and rdev `sb_events`.
- Test rdev sysfs attributes: mark faulty, remove spare/faulty devices, toggle write-mostly/failfast/write-error/want-replacement, re-add a bitmap-synced device, update slot, offset/new_offset/size, recovery_start, PPL fields, and badblock acknowledgements.
- Test md sysfs attributes: `array_state`, `sync_action`, `metadata_version`, `level` takeover, `layout`, `raid_disks`, `chunk_size`, `component_size`, `array_size`, `bitmap_type`, `bitmap_set_bits`, `consistency_policy`, `serialize_policy`, `logical_block_size`, and sync speed/min/max controls.
- Exercise `RUN_ARRAY`, `STOP_ARRAY`, `STOP_ARRAY_RO`, `RESTART_ARRAY_RW`, `ADD_NEW_DISK`, `HOT_ADD_DISK`, `HOT_REMOVE_DISK`, `SET_DISK_FAULTY`, `SET_ARRAY_INFO`, and `SET_BITMAP_FILE` ioctl paths, including CAP_SYS_ADMIN rejection.
- Verify `/proc/mdstat` content and poll behavior for inactive arrays, active arrays, degraded arrays, bitmap-backed arrays, sync/recovery/check/repair/reshape progress, delayed/remote/pending states, and unused autodetected devices.
- Inject member read/write errors through personalities and confirm `md_error()` updates rdev sysfs state, recovery bits, event work, mdstat events, and broken-array behavior for non-redundant levels.
- Run recovery/resync/check/repair/reshape with and without bitmaps, with `resync_min`/`resync_max`, with shared underlying disks, with `sync_force_parallel`, and under foreground I/O load to validate throttling and checkpoint updates.
- Test clustered arrays for disk add/remove acknowledgements, bitmap lock-all behavior during bitmap removal, metadata update locking, remote resync reporting, and size update notifications.
- Validate teardown under openers, sysfs activity, read-only devices, bitmap files, active recovery, and both `legacy_async_del_gendisk` modes.

## Cross-Chunk Notes

This chunk stops at the first spare-state helper group (`rdev_removeable()`, `rdev_is_spare()`, and the start of `rdev_addable()`). The next chunk continues spare removal/addition, sync action selection work scheduling, recovery checks, reshape finalization, badblock setters, reboot notification, module initialization, autodetect replay, and module exit. The final merged per-file research should connect this chunk's `MD_RECOVERY_NEEDED`/`sync_work` setup and rdev spare predicates to the later `remove_and_add_spares()`, `md_choose_sync_action()`, `md_start_sync()`, and `md_check_recovery()` implementations.
