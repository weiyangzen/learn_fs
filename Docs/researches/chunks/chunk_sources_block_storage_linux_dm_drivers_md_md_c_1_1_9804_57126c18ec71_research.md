# Chunk Research: sources/block-storage/linux-dm/drivers/md/md.c lines 1-9804

## Scope

This chunk covers almost all of the Linux MD RAID core in `drivers/md/md.c`: global MD framework state, request submission, suspend/quiesce handling, flush coalescing, mddev/rdev lifetime management, native metadata formats 0.90 and 1.x, sysfs and ioctl control planes, array start/stop, personality registration, `/proc/mdstat`, recovery/resync/reshape orchestration, bad-block handling, reboot/init support, and the first half of clustered superblock reload. The source tree `sources/block-storage/linux-dm` is included by `Docs/research_subset_a.md`.

## APIs and Entry Points

- Block-device entry points are collected in `md_fops`: `md_submit_bio()`, `md_open()`, `md_release()`, `md_ioctl()`, compat ioctl, `md_getgeo()`, `md_check_events()`, and `md_set_read_only()`.
- Exported MD-core APIs used by personalities and related code include `md_handle_request()`, `mddev_suspend()`, `mddev_resume()`, `md_flush_request()`, `mddev_init()`, `mddev_unlock()`, `md_update_sb()`, `md_run()`, `md_start()`, `md_stop()`, `md_error()`, `md_write_start()`, `md_do_sync()`, `md_check_recovery()`, and `md_reap_sync_thread()`.
- Personality/cluster registration APIs are `register_md_personality()`, `unregister_md_personality()`, `register_md_cluster_operations()`, `unregister_md_cluster_operations()`, `md_setup_cluster()`, and `md_cluster_stop()`.
- User-visible control planes include sysctl `/proc/sys/dev/raid/speed_limit_{min,max}`, sysfs `md` and per-rdev attributes, legacy md ioctls, and `/proc/mdstat`.
- Metadata dispatch is through `struct super_type super_types[]`, currently native `0.90.0` and `md-1`.

## Core Control Flow

Incoming bios enter `md_submit_bio()`, which rejects unconfigured arrays, broken write targets, and hard read-only writes, then calls `md_handle_request()`. `md_handle_request()` waits for whole-array or write-range suspension, honors `REQ_NOWAIT`, increments `active_io`, calls personality `make_request()`, and retries if the personality returns false. This coordinates with `mddev_suspend()`, which drains active I/O, calls personality `quiesce(1)`, blocks superblock updates, cancels safemode, and enters `memalloc_noio` until `mddev_resume()`.

Flushes are coalesced by `md_flush_request()`: one bio becomes `mddev->flush_bio`, `submit_flushes()` issues `REQ_PREFLUSH` bios to each non-faulty active rdev, and `md_submit_flush_data()` completes empty flushes or strips `REQ_PREFLUSH` and re-enters request handling.

Array/device lifetime starts with `md_alloc()`/`mddev_alloc()`, while component devices are imported by `md_import_device()` and attached with `bind_rdev_to_array()`. Binding enforces duplicate, size, descriptor, max-device, read-only, and integrity constraints, creates sysfs state, links the block holder, and inserts the rdev with RCU.

Running an array with `md_run()` analyzes superblocks, loads the requested personality, checks metadata/data overlap, initializes biosets, calls `pers->run()`, creates or loads bitmaps, configures queue flags, registers redundancy sysfs files, links active rdevs, initializes safemode/in-sync state, and schedules recovery. `do_md_run()` then loads bitmap contents, performs clustered write allowance, calls optional `pers->start()`, exposes capacity, and sends notifications.

## Metadata and Persistence

The v0.90 path validates magic/version/checksum/UUID/event consistency, initializes legacy geometry and bitmap defaults, handles 0.91 reshape fields, maps disk state flags, and rewrites legacy disk tables with clean/dirty/event/checkpoint state. It caps redundant arrays at the metadata-addressable 4 TB component limit and forbids non-zero data-offset changes.

The v1.x path supports minor versions 0/1/2 placement, feature maps, data offsets, new offsets during reshape, bad-block logs, PPL/multiple-PPL metadata, journal roles, clustered metadata, replacement flags, and recovery offsets. It rejects unknown features, invalid padding, bad checksums, metadata/data overlap, incompatible RAID0 layout flags, and conflicting PPL/bitmap/journal combinations.

`md_update_sb()` is the central metadata commit path. It updates recovery offsets, handles non-persistent/external arrays, changes event counters, marks faults, calls `sync_super()`, writes superblock and bad-block pages, retries on failfast-triggered rewrite, coordinates clustered metadata updates, clears `MD_SB_CHANGE_*` only if no new changes raced in, wakes blocked rdevs, acknowledges badblocks, and notifies progress.

## Sysfs and Ioctl Surfaces

Per-rdev sysfs attributes expose and mutate `state`, corrected `errors`, `slot`, `offset`, `new_offset`, component `size`, `recovery_start`, bad blocks, and PPL sector/size. Store paths require `CAP_SYS_ADMIN` and usually run under `mddev_lock()`.

Array sysfs attributes expose and mutate level, layout, raid disk count, UUID, chunk size, recovery checkpoint, array state, metadata version, bitmap dirty-bit injection, component size, sync action/progress/speed limits, suspend ranges, reshape position/direction, array size, consistency policy, fail-last-dev, and RAID1 serialization policy.

The ioctl path validates commands, gates mutating operations behind `CAP_SYS_ADMIN`, handles query ioctls without `reconfig_mutex`, then serializes configuration through `mddev_lock()`. It supports legacy array setup, disk add/remove, run/stop/read-only transitions, bitmap file management, fault injection, queries, and clustered disk NACK.

## Recovery, Resync, and Write State

Writes use `md_write_start()`/`md_write_inc()`/`md_write_end()`. The first write to a clean or read-auto array transitions it dirty/read-write, sets `MD_SB_CHANGE_CLEAN|MD_SB_CHANGE_PENDING`, wakes the md thread, and waits until metadata records the dirty state when superblocks exist.

`md_check_recovery()` is the periodic md-thread coordinator. It performs allowed superblock updates while suspended, runs bitmap daemon work, handles safemode, removes/adds spares, processes clustered remove flags, commits metadata, reaps finished sync threads, decides whether to reshape/recover/resync, writes bitmap pages before recovery with new spares, and queues `md_start_sync()`.

`md_do_sync()` is the dedicated recovery/resync/reshape loop. It refuses read-only arrays, obtains clustered resync locks, serializes against conflicting arrays sharing physical disks unless `parallel_resync` is set, chooses a start sector, repeatedly calls `pers->sync_request()`, tracks progress/speed/checkpoints, applies min/max sync windows, updates recovery offsets and capacity, sets `MD_RECOVERY_DONE`, and wakes the parent md thread.

## State and Synchronization

Global state includes `pers_list` under `pers_lock`, `all_mddevs` under `all_mddevs_lock`, `pending_raid_disks`, `md_event_count`/`md_event_waiters`, MD workqueues, sysctl speed limits, cluster ops/module pointers, and `resync_wait`.

Per-array state uses `reconfig_mutex`, `open_mutex`, `mddev->lock`, RCU rdev traversal, `sb_wait`, `recovery_wait`, atomic counters, safemode timers, work items, and sysfs dirent references. `mddev_unlock()` removes deferred sysfs groups outside `reconfig_mutex` to avoid sysfs lock inversion, then wakes md threads under `pers_lock`.

Per-rdev state includes descriptor/raid slots, saved/new raid-disk values, data offsets, recovery offset, superblock/badblock pages, sysfs references, block-device holder state, pending I/O count, badblocks, corrected/read error counters, PPL metadata, and flags such as `Faulty`, `In_sync`, `Journal`, `WriteMostly`, `FailFast`, `Blocked`, `Replacement`, `Candidate`, `ExternalBbl`, and `CollisionCheck`.

## Dependencies

This chunk depends on Linux block APIs, kobject/sysfs/proc/sysctl infrastructure, waitqueues, workqueues, timers, RCU, kthreads, module refcounts/loading, reboot notifiers, badblocks, random UUID generation, blk trace events, and percpu refs. MD-local dependencies include `md.h`, `md-bitmap.h`, `md-cluster.h`, personality callbacks, clustered metadata callbacks, bitmap helpers, metadata layouts from `linux/raid/md_p.h`, and ioctl ABI from `linux/raid/md_u.h`.

## Risks and Edge Cases

- Request submission relies on careful ordering between `active_io`, RCU, `mddev->suspended`, superblock-update flags, and personality `quiesce()`.
- `md_update_sb()` has complex retry and clustered coordination; wrong flag/event handling can lose metadata changes or force repeated rewrites.
- Sysfs store paths mutate live array shape and rely on busy checks, recovery bits, and personality validation.
- Rdev removal is delayed through RCU and `md_rdev_misc_wq`; immediate reuse expectations can race.
- Bad-block handling can force device failure when metadata cannot record unacknowledged blocks.
- `md_do_sync()` uses overloaded sentinel values in `curr_resync` and can wait indefinitely on user-controlled `resync_max`.
- Clustered paths assume `md_cluster_ops` remains valid while module references are held and callback ordering is correct.
- `md_reload_sb()` begins at the chunk boundary without an explicit visible RCU read lock around `rdev_for_each_rcu()`.

## Cross-Chunk References

- Lines 9805-9951 continue `md_reload_sb()` after the missing-rdev branch, export it, then define built-in-kernel autodetect/autostart, module teardown, module parameters, and aliases.
- Chunk 2 consumes state and helpers defined here: `read_rdev()`, `check_sb_changes()`, `md_import_device()`, `pending_raid_disks`, `autorun_devices()`, `export_array()`, `for_each_mddev()`, `md_event_waiters`, `md_unloading`, `mdp_major`, `raid_table_header`, and `start_readonly`.
- Personality modules in other `drivers/md/*` files depend on the exported lifecycle, write tracking, recovery, accounting, bad-block, and registration APIs defined in this chunk.
- `md-cluster.c` and `md-cluster.h` provide clustered callback implementations referenced throughout this chunk.