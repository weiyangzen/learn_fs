# File Research: sources/block-storage/linux-dm/drivers/md/md.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9804, source bytes 262137, report `Docs/researches/chunks/chunk_sources_block_storage_linux_dm_drivers_md_md_c_1_1_9804_57126c18ec71_research.md`
- chunk 2: lines 9805-9951, source bytes 3723, report `Docs/researches/chunks/chunk_sources_block_storage_linux_dm_drivers_md_md_c_2_9805_9951_21bffa5c4034_research.md`

## Chunk Research

### Chunk 1: lines 1-9804

# Chunk Research: sources/block-storage/linux-dm/drivers/md/md.c lines 1-9804

## Scope

This chunk covers almost all of the Linux MD RAID core in `drivers/md/md.c`: global MD framework state, request submission, suspend/quiesce handling, flush coalescing, mddev/rdev lifetime management, native metadata formats 0.90 and 1.x, sysfs and ioctl control planes, array start/stop, personality registration, `/proc/mdstat`, recovery/resync/reshape orchestration, bad-block handling, reboot/init support, and the first half of clustered superblock reload. The source tree `sources/block-storage/linux-dm` is included by `Docs/research_subset_a.md`.

## APIs and Entry Points

- Block-device entry points are collected in `md_fops`: `md_submit_bio()`, `md_open()`, `md_release()`, `md_ioctl()`, compat ioctl, `md_getgeo()`, `md_check_events()`, and `md_set_read_only()`.
- Exported MD-core APIs used by personalities and related code include `md_handle_request()`, `mddev_suspend()`, `mddev_resume()`, `md_flush_request()`, `mddev_init()`, `mddev_unlock()`, `md_find_rdev_nr_rcu()`, `md_find_rdev_rcu()`, `md_update_sb()`, `md_run()`, `md_start()`, `md_stop_writes()`, `md_stop()`, `md_wakeup_thread()`, `md_register_thread()`, `md_unregister_thread()`, `md_error()`, `md_done_sync()`, `md_write_start()`, `md_write_inc()`, `md_write_end()`, `md_submit_discard_bio()`, `acct_bioset_init()`, `acct_bioset_exit()`, `md_account_bio()`, `md_allow_write()`, `md_do_sync()`, `md_check_recovery()`, `md_reap_sync_thread()`, `md_wait_for_blocked_rdev()`, `md_finish_reshape()`, `rdev_set_badblocks()`, `rdev_clear_badblocks()`, and the beginning of `md_reload_sb()`.
- Personality/cluster registration APIs are `register_md_personality()`, `unregister_md_personality()`, `register_md_cluster_operations()`, `unregister_md_cluster_operations()`, `md_setup_cluster()`, and `md_cluster_stop()`.
- User-visible control planes include sysctl `/proc/sys/dev/raid/speed_limit_{min,max}`, sysfs `md` attributes under each md disk kobject, per-rdev sysfs attributes under `md/dev-*`, legacy md ioctls from `md_u.h`, and `/proc/mdstat`.
- Internal metadata format dispatch is through `struct super_type super_types[]`, currently native `0.90.0` and `md-1`, each with `load_super`, `validate_super`, `sync_super`, `rdev_size_change`, and `allow_new_offset`.

## Core Control Flow

Incoming bios enter `md_submit_bio()`, which rejects unconfigured arrays, broken write targets, and writes to hard read-only arrays, then splits the bio and calls `md_handle_request()`. `md_handle_request()` waits while the whole array or a write range is suspended, honors `REQ_NOWAIT` with would-block failure, increments `active_io`, calls the active personality `make_request()`, and retries if the personality returns false. This path coordinates with `mddev_suspend()`, which waits for `active_io` to drain, calls personality `quiesce(1)`, blocks superblock updates with `MD_ALLOW_SB_UPDATE`/`MD_UPDATING_SB`, cancels safemode, and enters a `memalloc_noio` section until `mddev_resume()`.

Flushes are coalesced by `md_flush_request()`: one bio becomes `mddev->flush_bio`, `submit_flushes()` issues `REQ_PREFLUSH` bios to every non-faulty active rdev, and `md_submit_flush_data()` either completes an empty flush or strips `REQ_PREFLUSH` and re-enters `md_handle_request()`. The code explicitly clears `flush_bio` before re-entry to avoid suspend/deadlock cycles with other bios.

Array/device lifetime starts with `md_alloc()` and `mddev_alloc()`, which create `struct mddev`, allocate a `gendisk`, register the `md` kobject, and place the mddev on `all_mddevs`. Component devices are imported by `md_import_device()`, which allocates and initializes `struct md_rdev`, claims the block device, allocates a superblock page, optionally loads metadata, and returns an rdev ready for `bind_rdev_to_array()`. Binding enforces duplicate, size, descriptor-number, max-device, read-only, and integrity constraints, creates sysfs state, links the block holder, and adds the rdev with RCU list insertion.

Metadata assembly uses `analyze_sbs()` to identify the freshest usable component, validate the rest against it, discard inconsistent devices, and initialize `mddev` geometry/state. Running an array with `md_run()` loads the requested personality module, checks metadata/data overlap, initializes biosets, calls `pers->run()`, creates or loads bitmaps, configures queue flags, registers redundancy sysfs files for personalities with `sync_request`, links active rdevs as `rdN`, initializes safemode/in-sync state, and schedules recovery. `do_md_run()` then loads bitmap contents, performs clustered write allowance, calls optional `pers->start()`, exposes capacity, and sends uevents/sysfs notifications.

Stop/read-only transitions go through `md_set_readonly()`, `do_md_stop()`, `__md_stop_writes()`, `mddev_detach()`, and `__md_stop()`. They freeze recovery, interrupt and reap sync threads, flush bitmaps, write clean metadata when possible, quiesce personalities, unregister md threads, remove sysfs links/groups, release personality private state, export rdevs on full stop, clear mddev fields with `md_clean()`, and update capacity/events.

## Metadata and Persistence

The v0.90 path (`super_90_load()`, `super_90_validate()`, `super_90_sync()`) reads a 4 KiB-end superblock, validates magic/version/checksum/UUID/event consistency, initializes legacy geometry and bitmap defaults, handles 0.91 reshape fields, maps descriptor records to `Faulty`, `In_sync`, `WriteMostly`, and `FailFast`, and rewrites legacy disk tables with clean/dirty/event/checkpoint state. It caps redundant arrays at the metadata-addressable 4 TB component limit and forbids non-zero data-offset changes.

The v1.x path (`super_1_load()`, `super_1_validate()`, `super_1_sync()`) supports minor versions 0/1/2 placement, feature maps, data offsets, new offsets during reshape, bad-block logs, PPL/multiple-PPL metadata, journal roles, clustered metadata, replacement flags, and recovery offsets. It rejects unknown features, invalid padding, bad checksums, metadata/data overlap, incompatible RAID0 layout flags, and conflicting PPL/bitmap/journal combinations.

`md_update_sb()` is the central metadata commit path. It updates recovery offsets, handles non-persistent/external arrays, increments or rolls back event counters, marks faults as recorded, calls `sync_super()`, writes each in-memory superblock and bad-block page with `md_super_write()`, waits with `md_super_wait()`, retries on failfast-triggered rewrite, coordinates clustered `metadata_update_start/cancel/finish`, clears `MD_SB_CHANGE_*` flags only if no new changes raced in, wakes blocked rdevs, acknowledges badblocks, and notifies sync progress.

Superblock writes use `REQ_SYNC|REQ_PREFLUSH|REQ_FUA` and optional `MD_FAILFAST`; completion calls `md_error()` on failure and may set `MD_SB_NEED_REWRITE` plus `LastDev`. Synchronous page I/O is provided by `sync_page_io()`, which chooses metadata/data bdev and offset according to metadata operation and reshape direction.

## Sysfs and Ioctl Surfaces

Per-rdev sysfs attributes expose and mutate `state`, corrected `errors`, `slot`, `offset`, `new_offset`, component `size`, `recovery_start`, acknowledged/unacknowledged bad blocks, and PPL sector/size. Store paths require `CAP_SYS_ADMIN` via `rdev_attr_store()` and usually run under `mddev_lock()`. Important mutations include marking faulty, removing, write-mostly and serialization pool changes, blocked/unblocked handling, failfast, want/replacement, re-add, external bad-block list mode, slot hot-add/hot-remove, offset/new-offset reshape preparation, and size overlap checks for external metadata.

Array sysfs attributes expose and mutate level, layout, raid disk count, UUID, chunk size, recovery checkpoint, array state, metadata version, bitmap dirty-bit injection, component size, sync action/progress/speed limits, suspend ranges, reshape position/direction, array size, consistency policy, fail-last-dev, and RAID1 serialization policy. Many writes either refuse active arrays or delegate to personality callbacks such as `takeover`, `check_reshape`, `start_reshape`, `resize`, and `change_consistency_policy`.

`array_state_store()` maps textual states to core operations: `clear` stops and disassembles, `inactive` stops without export, `readonly` runs or converts to read-only, `read-auto` enables auto-write transition, `clean` tries to set in-sync, and `active` runs or restarts read/write. `write-pending`, `active-idle`, `broken`, and `suspended` are reported states but not directly settable here.

The ioctl path validates commands, gates mutating commands behind `CAP_SYS_ADMIN`, handles read-only query ioctls without `reconfig_mutex`, then serializes configuration through `mddev_lock()`. It supports legacy `SET_ARRAY_INFO`, `ADD_NEW_DISK`, `HOT_ADD_DISK`, `HOT_REMOVE_DISK`, `RUN_ARRAY`, `STOP_ARRAY`, `STOP_ARRAY_RO`, `RESTART_ARRAY_RW`, `SET_BITMAP_FILE`, `SET_DISK_FAULTY`, `GET_*`, and clustered disk NACK. It protects stop commands with `MD_CLOSING` and open-count checks.

## Recovery, Resync, and Write State

Writes use `md_write_start()`/`md_write_inc()`/`md_write_end()`. The first write to a clean or read-auto array transitions it dirty/read-write, sets `MD_SB_CHANGE_CLEAN|MD_SB_CHANGE_PENDING`, wakes the md thread, and waits until metadata records the dirty state when the array has superblocks. `writes_pending` is a `percpu_ref`; `set_in_sync()` switches it to atomic mode to verify quiescence before declaring the array clean and scheduling a clean superblock write.

`md_check_recovery()` is the periodic md-thread coordinator. It performs allowed superblock updates while suspended, runs bitmap daemon work, handles safemode, removes/adds spares on read-only arrays, processes clustered remove flags, tries to set clean state, commits metadata, reaps finished sync threads, decides whether to reshape/recover/resync, writes all bitmap pages before recovery with newly added spares, and queues `md_start_sync()` to create the dedicated resync thread.

`md_do_sync()` is the dedicated recovery/resync/reshape loop. It refuses read-only arrays, obtains clustered resync locks, serializes against conflicting arrays sharing physical disks unless `parallel_resync` is set, chooses the starting sector from requested range, checkpoint, reshape position, bitmap, or per-rdev recovery offset, then repeatedly calls `pers->sync_request()`. It tracks `recovery_active`, `curr_resync`, `curr_resync_completed`, speed marks, min/max sync windows, idle detection, and checkpoint updates. Completion or interruption updates `recovery_cp`, per-rdev recovery offsets, array capacity after grow-reshape, `MD_SB_CHANGE_*`, `MD_RECOVERY_DONE`, and wakes the parent md thread.

`md_reap_sync_thread()` unregisters the sync thread, activates spares through `pers->spare_active()` on successful recovery, calls `pers->finish_reshape()` when needed, clears saved raid-disk state when no longer degraded, commits metadata, releases clustered resync locks, clears recovery mode bits, updates clustered size after reshape, and schedules another recovery check. `remove_and_add_spares()` is the shared helper for removing failed/non-in-sync active rdevs once pending I/O drains and for trying personality hot-add on available spares.

## State and Synchronization

Global state includes `pers_list` under `pers_lock`, `all_mddevs` under `all_mddevs_lock`, `pending_raid_disks`, `md_event_count`/`md_event_waiters`, three workqueues (`md_wq`, `md_misc_wq`, `md_rdev_misc_wq`), sysctl speed limits, cluster ops/module pointers, and `resync_wait`.

Per-array state is split across `reconfig_mutex` for configuration, `open_mutex` for open/stop races, `mddev->lock` for fast flags/counters, RCU for rdev list traversal, waitqueues `sb_wait` and `recovery_wait`, atomics for openers/active I/O/flushes/pending writes/recovery activity, safemode timers, work items, and kobject/sysfs dirent references. `mddev_unlock()` deliberately removes deferred sysfs groups outside `reconfig_mutex` to avoid sysfs lock inversion, then wakes md threads under `pers_lock` so thread pointers cannot disappear.

Per-rdev state includes descriptor and raid-disk slots, saved/new raid-disk values, data and new data offsets, recovery offset, superblock/badblock pages, sysfs dirent references, block-device holder state, pending I/O count, badblocks, corrected/read error counters, PPL metadata, and flags such as `Faulty`, `In_sync`, `Journal`, `WriteMostly`, `FailFast`, `Blocked`, `Replacement`, `Candidate`, `ExternalBbl`, and `CollisionCheck`.

Serialization support for RAID1 write-behind on multi-queue write-mostly devices is managed by `rdev_init_serial()`, `mddev_create_serial_pool()`, and `mddev_destroy_serial_pool()`. These allocate per-rdev serial buckets and a shared mempool under array suspension unless the caller already suspended the array.

## Dependencies

This chunk depends heavily on Linux block APIs (`bio`, `gendisk`, request flags, block-device claiming, queue limits, discard, integrity, partition stats), kernel object/sysfs/proc/sysctl infrastructure, waitqueues, workqueues, timers, RCU, kthreads, module loading/refcounts, reboot notifiers, badblocks, random UUID generation, blk trace events, and percpu refs. MD-local dependencies include `md.h`, `md-bitmap.h`, `md-cluster.h`, personality callbacks, clustered metadata callbacks, bitmap create/load/flush/daemon/status helpers, and metadata layout definitions from `linux/raid/md_p.h` and ioctl ABI from `linux/raid/md_u.h`.

## Risks and Edge Cases

- The request path relies on careful ordering between `active_io`, RCU, `mddev->suspended`, `MD_ALLOW_SB_UPDATE`, and personality `quiesce()`. A personality that mishandles `make_request()` retry or quiesce visibility can deadlock suspend or allow I/O through reconfiguration.
- `md_update_sb()` has complex retry and clustered coordination behavior. Incorrect flag clearing or event-counter handling can either lose metadata changes or force repeated rewrites.
- Many sysfs store paths mutate live array shape. They depend on `mddev_lock()`, `sysfs_active`, recovery bits, and personality validation; missing a busy check could permit reshape/level/size changes during recovery.
- Rdev removal is intentionally delayed through RCU and `md_rdev_misc_wq`; callers that expect immediate kobject destruction or reuse can race.
- Bad-block handling can force device failure when metadata cannot record unacknowledged blocks. External bad-block-list mode shifts responsibility to userspace and relies on sysfs notification.
- The recovery loop uses overloaded sentinel values in `curr_resync` (`0`, `1`, `2`, `3`, real sector). Consumers must interpret these consistently for `/proc/mdstat`, sysfs progress, and conflict waiting.
- `md_do_sync()` can wait indefinitely on user-controlled `resync_max`; it uses interruptible waits to avoid watchdog issues but forward progress still depends on userspace changing limits or interrupting recovery.
- Failfast superblock writes mark `LastDev` and trigger rewrites. This reduces risk of blocking on a bad path but can cause repeated metadata-write cycles if the underlying failure mode persists.
- Clustered paths assume `md_cluster_ops` remains valid while module references are held. Registration is protected by `pers_lock`, but individual callbacks must preserve cluster-wide metadata and bitmap lock ordering.
- `md_reload_sb()` begins at the chunk boundary without explicit RCU locking around `rdev_for_each_rcu()` in the visible code, so correctness depends on caller context or list traversal conventions outside this chunk.

## Cross-Chunk References

- Lines 9805-9951 continue `md_reload_sb()` after the missing-rdev branch, export it, then define built-in-kernel autodetect/autostart, module teardown, module parameters, and aliases.
- Chunk 2 consumes state and helpers defined here: `read_rdev()`, `check_sb_changes()`, `md_import_device()`, `pending_raid_disks`, `autorun_devices()`, `export_array()`, `for_each_mddev()`, `md_event_waiters`, `md_unloading`, `mdp_major`, `raid_table_header`, and `start_readonly`.
- Personality modules in other `drivers/md/*` files depend on the exported lifecycle, write tracking, recovery, accounting, bad-block, and registration APIs defined in this chunk.
- `md-cluster.c` and `md-cluster.h` provide the clustered callback implementation referenced throughout this chunk for metadata update, bitmap gathering/locking, disk add/remove acknowledgment, resync locking, and remote superblock reload behavior.

### Chunk 2: lines 9805-9951

# Chunk Research: sources/block-storage/linux-dm/drivers/md/md.c lines 9805-9951

## Scope

This chunk covers the end of `md_reload_sb()`, the built-in-kernel-only RAID autodetection queue and autostart path, MD module teardown, init/exit registration, module parameters, and module metadata. The code belongs to the Linux MD RAID framework in the `sources/block-storage/linux-dm` source tree, which is in `Docs/research_subset_a.md`.

## APIs and Entry Points

- `md_reload_sb(struct mddev *mddev, int nr)` is exported with `EXPORT_SYMBOL(md_reload_sb)`. It finds an `md_rdev` by descriptor number, reloads the selected device superblock with `read_rdev()`, applies metadata change handling through `check_sb_changes()`, then rereads all non-faulty component devices so `recovery_offset` state is refreshed.
- `md_autodetect_dev(dev_t dev)` is available only when `!MODULE`. It records a detected block device number into a private boot-time list for later array autodetection.
- `md_autostart_arrays(int part)` is also `!MODULE` only. It consumes the detected-device list, imports each candidate as a v0.90 MD component through `md_import_device(dev, 0, 90)`, tags valid devices with `AutoDetected`, moves them to `pending_raid_disks`, and then calls `autorun_devices(part)`.
- `md_exit(void)` is the `module_exit()` teardown function. It unregisters block majors, reboot/sysctl hooks, wakes `/proc/mdstat` pollers, removes procfs state, exports/clears all arrays, and destroys MD workqueues.
- `get_ro()` and `set_ro()` implement the `start_ro` module parameter around the global `start_readonly` value.
- Module parameters exposed here are `start_ro`, `start_dirty_degraded`, `new_array`, and `create_on_open`; module metadata declares GPL license, description, alias `md`, and the MD block major alias.

## Control Flow

`md_reload_sb()` continues from the previous chunk's selected-rdev lookup. If no matching descriptor exists, it logs a warning and returns. On a matching device, it calls `read_rdev()` and stops silently on a negative error. Successful reload invokes `check_sb_changes()`, then loops over all RCU-visible rdevs on the array and calls `read_rdev()` for every non-`Faulty` component. This second pass intentionally refreshes recovery-position state across the full array, not just the changed member.

The boot autodetection path is a two-stage queue. `md_autodetect_dev()` allocates a `detected_devices_node`, stores the `dev_t`, and appends it to `all_detected_devices` under `detected_devices_mutex`. `md_autostart_arrays()` locks the same list, pops one node at a time, frees the node, drops the mutex while importing the block device, then reacquires the mutex before checking the result and continuing. Imported, non-faulty rdevs are marked `AutoDetected` and linked into the global `pending_raid_disks` list; after the detected list is drained or `i_scanned` reaches `INT_MAX`, `autorun_devices(part)` groups pending rdevs by superblock UUID/minor and starts arrays.

`md_exit()` runs teardown in registration-reverse order for global entry points first: `unregister_blkdev(MD_MAJOR, "md")`, `unregister_blkdev(mdp_major, "mdp")`, `unregister_reboot_notifier()`, and `unregister_sysctl_table()`. It then sets `md_unloading`, wakes any active waiters on `md_event_waiters` with exponential sleep between wakeups, removes `/proc/mdstat`, walks every mddev via `for_each_mddev()`, calls `export_array()`, clears `ctime` and `hold_active`, and finally destroys `md_rdev_misc_wq`, `md_misc_wq`, and `md_wq`.

## State and Synchronization

- `detected_devices_mutex` protects the boot-only `all_detected_devices` list. The import path deliberately releases this mutex around `md_import_device()` because importing can allocate, open block devices, and read superblocks.
- `all_detected_devices` owns temporary `detected_devices_node` allocations until `md_autostart_arrays()` removes and frees them.
- `pending_raid_disks` is a file-global staging list declared earlier. This chunk appends imported autodetected rdevs through their `same_set` list node; `autorun_devices()` later consumes the list.
- `Faulty` suppresses both reload rereads and autodetected array staging. `AutoDetected` records that an rdev came from the boot autodetection path.
- `md_unloading` changes `/proc/mdstat` polling behavior; `mdstat_poll()` returns readable/error/priority events immediately when unload begins, allowing `md_exit()` to wait until `md_event_waiters` is no longer active.
- `for_each_mddev()` takes and drops references while iterating the global mddev list. The comment in `md_exit()` relies on that macro's final `mddev_put()` to schedule destruction once the array has been exported and made inactive.

## Dependencies

This chunk depends on core kernel infrastructure: linked lists, mutexes, waitqueues, procfs removal, sysctl/reboot notifier registration, block-device major registration, module parameters, workqueues, allocation/freeing, bit flags, and logging. MD-local dependencies include `read_rdev()`, `check_sb_changes()`, `md_import_device()`, `autorun_devices()`, `export_array()`, `for_each_mddev()`, `pending_raid_disks`, `md_event_waiters`, `start_readonly`, `start_dirty_degraded`, `add_named_array()`, `create_on_open`, and the three MD workqueues created by `md_init()`.

## Risks and Edge Cases

- `md_reload_sb()` uses `rdev_for_each_rcu()` but this slice does not show an explicit RCU read-side lock. Correctness depends on caller context or macro/local conventions established outside the chunk.
- Errors from the second `read_rdev()` pass in `md_reload_sb()` are ignored. That keeps the refresh best-effort but can leave some non-faulty devices with stale recovery metadata if reread fails.
- `md_autodetect_dev()` silently drops devices on allocation failure. At boot this means a device may simply not be considered for legacy autodetect.
- `md_autostart_arrays()` frees the detected node before importing the device and never requeues failed imports. Devices returning `ERR_PTR()` or marked `Faulty` are skipped permanently for this autodetect pass.
- The autodetect import hard-codes superblock format `0.90`, matching the legacy kernel autodetect mechanism. Newer metadata formats depend on userspace assembly paths rather than this boot scanner.
- The scan counter guard `i_scanned < INT_MAX` prevents integer overflow in pathological list growth but also means any further queued devices would remain on `all_detected_devices`.
- `md_exit()` doubles `delay` without an upper bound while waiters remain active. This is acceptable only if waiters actually drain; a stuck waiter can stretch unload latency significantly.

## Cross-Chunk References

- The preceding lines define `read_rdev()` behavior and the first part of `md_reload_sb()`, including superblock reload, recovery-offset extraction, and spare activation when another node completed recovery.
- Earlier file state defines `md_event_waiters`, `md_new_event()`, `all_mddevs`, and `for_each_mddev()`, which explain the unload waiter loop and mddev reference behavior.
- Earlier import code defines `md_import_device()`, including block-device locking, superblock loading, and fault handling used by `md_autostart_arrays()`.
- Earlier autorun code defines `pending_raid_disks` and `autorun_devices()`, which consume the rdevs staged in this chunk.
- Earlier init code `md_init()` creates the workqueues, registers the `md`/`mdp` block devices, reboot notifier, sysctl table, and `/proc/mdstat`; `md_exit()` reverses those registrations here.
