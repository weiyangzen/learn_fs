# Group Research: Linux device-mapper core and MD autodetect, bitmap, cluster, faulty, linear, and multipath support

This group covers the Device Mapper core block-device implementation plus several MD components: boot-time array autodetection, persistent dirty-region bitmaps, clustered MD coordination, and deprecated MD personalities for faulty, linear, and multipath devices.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm.h

## Purpose
Defines internal Device Mapper declarations shared across DM core, table, target registry, ioctl interface, sysfs, target implementations, zoned support, request-based support, and mempool management.

## Main Interfaces
- Suspend/status flags: `DM_SUSPEND_LOCKFS_FLAG`, `DM_SUSPEND_NOFLUSH_FLAG`, `DM_STATUS_NOFLUSH_FLAG`.
- Table API declarations for target lookup, table sizing/restrictions, event callbacks, target suspend/resume hooks, queue mode, immutable target metadata, and table mempools.
- Target type helpers: `dm_target_bio_based()`, `dm_target_request_based()`, `dm_target_hybrid()`.
- Zoned declarations: `dm_set_zones_restrictions()`, `dm_zone_endio()`, `dm_blk_report_zones()`, `dm_is_zone_write()`, `dm_zone_map_bio()`, with stubs when zoned block support is disabled.
- Core mapped-device declarations for lifecycle, deletion, table devices, deferred removal, uevents, kobject lookup, open counts, and queue setup.
- Internal suspend/resume and mempool allocation declarations.

## Control Flow
This header does not implement control flow, but establishes the internal contracts used by `dm.c` and related DM files. It separates public device-mapper APIs from private cross-file entry points and makes compile-time zoned support conditional.

## State And Synchronization
Declares the functions that inspect mapped-device deletion/suspend/deferred-remove state and internal suspend state. It also exposes APIs whose implementations rely on mapped-device locks, SRCU table protection, kobject reference handling, and mempool lifetime rules.

## Integration Points
Used by DM core files, ioctl/control code, target table code, target registry code, zoned support, sysfs, request-based DM, and built-in targets such as linear and stripe.

## Notable Behaviors
- Target mode detection is callback-presence based: bio targets provide `map`, request targets provide `clone_and_map_rq`, and hybrids provide both.
- Zoned support compiles to conservative stubs without `CONFIG_BLK_DEV_ZONED`; zone mapping then kills bios by returning `DM_MAPIO_KILL`.
- Declares both `dm_internal_suspend_noflush()` and an older `dm_internal_suspend()` prototype, reflecting internal API compatibility concerns.

## Risks And Review Focus
- Because this is an internal header, prototype drift can break subtle lock or lifetime expectations across DM files.
- Callback-presence macros assume target types consistently initialize their operation tables.
- Conditional zoned stubs must match the behavior expected by core code when zoned support is unavailable.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-autodetect.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-autodetect.c

## Purpose
Implements built-in-kernel MD boot-time array setup and RAID autodetection for `raid=` and `md=` kernel command-line parameters.

## Main Interfaces
- Boot parameter parsers: `raid_setup()` for `raid=`, `md_setup()` for `md=`.
- Setup execution: `md_run_setup()`.
- Autodetect path: `autodetect_raid()` and `md_autostart_arrays()`.
- Explicit array assembly: `md_setup_drive()`.

## Control Flow
`md_setup()` records up to 256 requested MD arrays in `md_setup_args`, parsing optional partitionable-device syntax (`mdd`), MD minor, optional RAID level/chunk/fault fields for non-persistent linear or RAID0, and a comma-separated component-device list. It only stores the command-line intent; actual assembly waits until device probing has completed.

`md_run_setup()` first optionally waits for device probing and starts autodetected arrays unless `raid_noautodetect` is set. It then iterates recorded `md=` entries and calls `md_setup_drive()`. That function resolves component names to device numbers, opens the target MD block device, verifies it is backed by `md_fops`, locks the `mddev`, skips already configured arrays, optionally initializes non-persistent array info, adds each component with `md_add_new_disk()`, and calls `do_md_run()`.

## State And Synchronization
Boot-time state is stored in `__initdata` globals: `raid_noautodetect`, `raid_autopart`, `md_setup_args`, and `md_setup_ents`. Runtime MD state is protected by `mddev_lock()` while array info and disk membership are configured.

## Integration Points
Uses kernel boot `__setup()` parsing, `wait_for_device_probe()`, `name_to_dev_t()`, `init_stat()` for `/dev` path resolution, MD array management functions (`md_set_array_info()`, `md_add_new_disk()`, `do_md_run()`), and MD major/minor conventions including partitionable MD devices.

## Notable Behaviors
- `CONFIG_MD_AUTODETECT` controls the default for `raid_noautodetect`; without it autodetection is disabled by default.
- Duplicate `md=` definitions for the same minor and partitionable flag replace earlier definitions.
- Non-persistent `md=n,0,...` and `md=n,-1,...` paths synthesize array info for RAID0 or linear.
- Persistent-superblock arrays are started by supplying only the device list and letting MD inspect component metadata.
- The parser supports `raid=autodetect`, `raid=noautodetect`, `raid=partitionable`, and `raid=part`.

## Risks And Review Focus
- This code mutates the command-line device list in place by replacing commas with NULs.
- Device-name resolution combines `name_to_dev_t()` with `/dev` stat probing, so boot environment naming behavior is correctness-sensitive.
- Explicit setup skips arrays already autodetected, which can surprise boot configurations unless `raid=noautodetect` is used.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-autodetect.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-bitmap.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-bitmap.c

## Purpose
Implements MD write-intent bitmap support: persistent bitmap superblocks, bitmap file/internal storage I/O, in-memory dirty-region counters, write-start/write-end accounting, recovery synchronization, bitmap resizing, clustered bitmap slot copying, and bitmap sysfs controls.

## Main Interfaces
- Lifecycle: `md_bitmap_create()`, `md_bitmap_load()`, `md_bitmap_destroy()`, `md_bitmap_free()`, `md_bitmap_flush()`.
- Persistent metadata: `md_bitmap_read_sb()`, `md_bitmap_new_disk_sb()`, `md_bitmap_update_sb()`, `md_bitmap_print_sb()`.
- I/O tracking: `md_bitmap_startwrite()`, `md_bitmap_endwrite()`, `md_bitmap_unplug()`, `md_bitmap_daemon_work()`.
- Recovery tracking: `md_bitmap_start_sync()`, `md_bitmap_end_sync()`, `md_bitmap_close_sync()`, `md_bitmap_cond_end_sync()`, `md_bitmap_sync_with_cluster()`.
- Dirtying and resize: `md_bitmap_dirty_bits()`, `md_bitmap_resize()`, `md_bitmap_write_all()`.
- Cluster helpers: `get_bitmap_from_slot()`, `md_bitmap_copy_from_slot()`.
- Sysfs group: `md_bitmap_group` with `location`, `space`, `time_base`, `backlog`, `chunksize`, `metadata`, `can_clear`, and `max_backlog_used`.

## Control Flow
Bitmap creation allocates the `bitmap` object, initializes locks and wait queues, pins an optional backing file, reads or creates the bitmap superblock unless metadata is external, then calls `md_bitmap_resize()` to allocate in-memory counters and persistent filemap pages. Loading creates serial pools, optionally loads cluster slot bitmaps, marks old sync information clean, chooses a recovery start point, reads persistent bitmap bits into memory, clears stale state, schedules recovery, and updates the bitmap superblock.

Writes call `md_bitmap_startwrite()` before data I/O. For each affected chunk it allocates or hijacks a counter page, sets the persistent bitmap bit if the counter was clean, increments the in-memory counter, and records write-behind state if applicable. `md_bitmap_endwrite()` decrements counters, marks failed writes as resync-needed, updates `events_cleared` when safe, and marks pages pending for the daemon.

`md_bitmap_daemon_work()` periodically promotes pending pages to need-write, updates `events_cleared` in the superblock when needed, sweeps counters from `2` to `1` to `0`, clears persistent bits when safe, and writes cleanable pages. `md_bitmap_unplug()` writes dirty or need-write pages before underlying device queues are unplugged.

## State And Synchronization
In-memory counters live in `bitmap->counts.bp` and are protected by `bitmap->counts.lock`. Counter high bits represent resync-needed and resync-active; low bits count pending writes plus the persistent bit. Storage pages and per-page attributes track dirty, pending, and need-write states. `pending_writes` plus `write_wait` track bitmap page I/O. `overflow_wait` handles saturated counters. `behind_writes` and `behind_wait` track write-behind backlog.

`mddev->bitmap_info.mutex` serializes daemon work with destruction and bitmap load. Bitmap destruction disconnects `mddev->bitmap` under `mddev->lock`. Resizing active arrays quiesces the personality while replacing storage and counters.

## Integration Points
Uses MD core metadata (`mddev->events`, `sb_flags`, `recovery`, `recovery_cp`, `resync_max_sectors`), per-device superblock I/O (`md_super_write()`, `md_super_wait()`), personality quiesce hooks, md recovery threads, sysfs notifications, block tracing, optional clustered MD operations, and optional file-backed bitmaps via `bmap()` and buffer-head I/O.

## Notable Behaviors
- If no persistent bitmap storage exists, initialization marks all chunks dirty so full recovery occurs.
- If bitmap superblock events are stale relative to array events, the bitmap is marked stale and full recovery is forced.
- File-backed bitmaps pre-read and attach buffer heads so later writes bypass filesystem allocation paths.
- Internal bitmaps write near member superblocks and include alignment checks to avoid overwriting data or metadata.
- Allocation failure for an in-memory counter page can hijack the page pointer as two counters, except clustered RAID forbids hijack and requires preallocation.
- `can_clear` is false while `need_sync` is set and cannot be forced true while degraded.
- File-based bitmap resizing while active is rejected.

## Risks And Review Focus
- Bitmap correctness depends on ordering persistent bitmap-bit writes before corresponding data writes.
- Counter transitions among dirty, pending, resync-needed, and resync-active states are subtle and recovery-critical.
- Internal bitmap offset/alignment checks must prevent metadata/data overlap across external and native metadata layouts.
- Cluster slot offset math must match bitmap page allocation and superblock layout.
- Active resize replaces both filemap and counter arrays while preserving needed bits; rollback paths must not leak or corrupt state.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-bitmap.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-bitmap.h

## Purpose
Defines MD bitmap on-disk format, in-memory counter encoding, bitmap state flags, bitmap storage structures, and the bitmap API used by MD personalities, recovery code, and clustered MD.

## Main Interfaces
- Bitmap versions: `BITMAP_MAJOR_LO`, `BITMAP_MAJOR_HI`, `BITMAP_MAJOR_CLUSTERED`, `BITMAP_MAJOR_HOSTENDIAN`.
- Counter encoding: `bitmap_counter_t`, `NEEDED_MASK`, `RESYNC_MASK`, `COUNTER_MAX`, `NEEDED()`, `RESYNC()`, `COUNTER()`.
- Layout constants: `PAGE_BITS`, `PAGE_BIT_SHIFT`, `PAGE_COUNTER_RATIO`, `PAGE_COUNTER_SHIFT`, `PAGE_COUNTER_MASK`, `BITMAP_BLOCK_SHIFT`.
- On-disk superblock: `bitmap_super_t`.
- In-memory state: `struct bitmap_page`, `struct bitmap`, nested `bitmap_counts`, and `bitmap_storage`.
- Public bitmap functions for lifecycle, write tracking, sync tracking, resize, cluster slot copying, daemon work, and write-behind waiting.

## Control Flow
This header documents the counter state machine: a clean chunk has counter zero and a clear on-disk bit; dirtying sets the persistent bit and raises the counter; daemon sweeps can reduce counters and eventually clear persistent bits; resync-needed and resync-active high bits coordinate recovery.

## State And Synchronization
`struct bitmap` contains the `counts.lock` spinlock, pending write counters, wait queues, storage page map, flags, dirty-clean state, sysfs dirent references, and cluster slot number. The state bits include stale bitmap, bitmap write error, and host-endian legacy format.

## Integration Points
Included by MD bitmap implementation and clustered MD. Exposes API used by MD make-request paths, recovery paths, sysfs status, and cluster bitmap transfer.

## Notable Behaviors
- `bitmap_super_t` is fixed at 256 bytes and includes UUID, events, events-cleared, sync size, state, chunk size, daemon sleep, write-behind, reserved sectors, cluster node count, and cluster name.
- Version 3 is host-endian and non-portable; version 4 is little-endian; version 5 is clustered.
- The header explicitly documents pointer hijacking as an emergency low-memory counter fallback.

## Risks And Review Focus
- Any change to `bitmap_super_t` must preserve on-disk compatibility and the 256-byte size assumption.
- Counter-bit definitions limit usable write counters to 14 bits; overflow handling depends on `COUNTER_MAX`.
- Users of the API must respect locking and lifecycle assumptions because the structure fields are exposed internally.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-cluster.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-cluster.c

## Purpose
Implements clustered MD coordination using DLM lockspaces and lock value blocks: cluster join/leave, message broadcast, bitmap ownership and recovery, metadata-update serialization, resync range coordination, capacity changes, and clustered disk add/remove/readd operations.

## Main Interfaces
- Cluster lifecycle: `join()`, `leave()`, `slot_number()`, `load_bitmaps()`.
- Metadata protocol: `metadata_update_start()`, `metadata_update_finish()`, `metadata_update_cancel()`.
- Resync protocol: `resync_start()`, `resync_finish()`, `resync_info_update()`, `resync_info_get()`, `area_resyncing()`.
- Disk membership: `add_new_disk()`, `add_new_disk_cancel()`, `new_disk_ack()`, `remove_disk()`, `gather_bitmaps()`.
- Bitmap/capacity helpers: `resize_bitmaps()`, `lock_all_bitmaps()`, `unlock_all_bitmaps()`, `update_size()`.
- Registered operation table: `cluster_ops`.

## Control Flow
Joining allocates `md_cluster_info`, creates a DLM lockspace named from the array UUID and cluster name, waits for slot assignment, creates receive and lock resources (`message`, `token`, `no-new-dev`, `ack`, per-slot `bitmapNNNN`, and `resync`), establishes initial CR/EX locks, and locks the local bitmap slot in PW mode.

Messages are sent by locking the communication token, taking the message lock in EX, copying a `cluster_msg` into its LVB, downconverting message lock state, forcing ACK lock conversion so peer BAST callbacks wake receivers, then restoring ACK and message locks. Receivers read the message LVB under the receive mutex and dispatch by type: metadata updated, resyncing, new disk, remove, re-add, bitmap needs sync, capacity change, or bitmap resize.

Node failure recovery is driven by DLM slot callbacks. Failed slots are recorded in `recovery_map`; a recovery thread locks the failed slot bitmap, copies dirty ranges into the local bitmap, clears suspend ranges, adjusts `recovery_cp`, and wakes MD recovery as needed.

## State And Synchronization
`md_cluster_info` owns DLM resources, receive mutex, suspend spinlock, wait queues, recovery map, local slot number, and state bits such as waiting-for-newdisk, suspend-read-balancing, begin-join, send-lock, send-locked-already, already-in-cluster, pending-recv-event, and holding-md-mutex-for-recvd.

DLM lock resources store lockspace, LVB, name, flags, synchronous wait queue, BAST callback, current mode, and `mddev` backpointer. `recv_mutex` serializes receive processing with token-protected sends. `suspend_lock` protects remote resync suspend ranges.

## Integration Points
Uses Linux DLM (`dlm_new_lockspace()`, `dlm_lock()`, `dlm_unlock()`, lockspace recovery callbacks), MD core locking and recovery, MD bitmap slot helpers, MD metadata reload/update, personality quiesce/resize/size callbacks, kobject uevents for new-device notification, and `register_md_cluster_operations()`.

## Notable Behaviors
- DLM slot numbers are one-based, while clustered MD bitmap slots are zero-based.
- Local bitmap ownership is represented by a persistent PW lock on `bitmapNNNN`.
- Remote resync ranges are stored in the bitmap lock LVB and broadcast with `RESYNCING` messages.
- Peers can mark overlapping read areas as resyncing, temporarily suspending read balancing.
- Adding a disk broadcasts the device UUID and raid slot, then uses `no-new-dev` locking to verify peers can see the device.
- Capacity updates are two-phase: metadata update, peer bitmap sync-size verification, then capacity-change broadcast; failure attempts to revert.
- Leaving with dirty or interrupted recovery broadcasts `BITMAP_NEEDS_SYNC` so another node can continue.

## Risks And Review Focus
- Send/receive locking is delicate: token, ACK, message, receive mutex, and MD reconfig mutex interactions can deadlock if ordering changes.
- Error handling in DLM lock conversion paths must avoid leaving message or ACK locks stuck.
- Cluster bitmap slot copying directly affects recovery correctness after node failure.
- Resize and capacity-change protocols assume peers update bitmap superblocks and report matching sync sizes before capacity is exposed.
- New-disk coordination depends on userspace acknowledging kobject events within a timeout.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-cluster.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-cluster.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-cluster.h

## Purpose
Declares the clustered MD operation table used by MD core to call optional cluster support.

## Main Interfaces
`struct md_cluster_operations` contains callbacks for:
- Cluster lifecycle: `join`, `leave`, `slot_number`.
- Resync tracking: `resync_info_update`, `resync_info_get`, `resync_start`, `resync_finish`, `area_resyncing`.
- Metadata serialization: `metadata_update_start`, `metadata_update_finish`, `metadata_update_cancel`.
- Disk membership: `add_new_disk`, `add_new_disk_cancel`, `new_disk_ack`, `remove_disk`.
- Bitmap coordination: `load_bitmaps`, `gather_bitmaps`, `resize_bitmaps`, `lock_all_bitmaps`, `unlock_all_bitmaps`.
- Capacity changes: `update_size`.

## Control Flow
This file only declares the callback contract. Runtime behavior is supplied by `md-cluster.c` when the module registers its `cluster_ops`.

## State And Synchronization
No state is defined here. The callback contract implies callers must be prepared for cluster-wide locking, DLM-backed synchronization, and MD reconfig/recovery interactions.

## Integration Points
Included by MD core and clustered MD implementation to bridge generic MD code with optional cluster-specific behavior.

## Notable Behaviors
- The API explicitly separates metadata update start/finish/cancel so callers can hold cluster communication locks across MD superblock updates.
- Bitmap and capacity operations are part of the same cluster contract as disk membership, reflecting that recovery state is distributed.

## Risks And Review Focus
- Callback callers must know whether the MD reconfig mutex or other MD locks are held for each operation.
- Adding callbacks requires updates to both clustered and non-clustered call sites or stubs.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-cluster.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-faulty.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-faulty.c

## Purpose
Implements the deprecated MD `faulty` personality, a fault-injection array mode that intentionally fails selected read or write requests for testing.

## Main Interfaces
- Request handling: `faulty_make_request()`, `faulty_fail()`.
- Fault control: `faulty_reshape()` via layout/new_layout.
- Status and sizing: `faulty_status()`, `faulty_size()`.
- Lifecycle: `faulty_run()`, `faulty_free()`.
- Registered personality: `faulty_personality`.

## Control Flow
`faulty_run()` rejects bitmaps, allocates `faulty_conf`, initializes counters and periods, records the underlying rdev, stacks limits, sets array size, then applies the initial layout through `faulty_reshape()`.

`faulty_make_request()` checks write or read modes. Transient modes fail every Nth request or once. Persistent modes add the current sector to the fault table and then fail matching future I/O. `WriteAll` fails writes immediately without submitting them. Other failures clone the original bio, send the clone to the underlying device, and install `faulty_fail()` as completion so the original bio receives an error after the lower device completes.

## State And Synchronization
`faulty_conf` stores per-mode periods, atomic counters, up to 50 persistent fault sectors, per-sector modes, and the single backing rdev. Mode counters are atomic, but persistent fault array updates are simple in-memory mutations intended for this testing personality.

## Integration Points
Registers as an MD personality at `LEVEL_FAULTY` with aliases for faulty MD levels. Uses MD core helpers for bitmap rejection, disk limit stacking, array sizing, and personality registration.

## Notable Behaviors
- Supported modes include write transient, read transient, write persistent, read persistent, write all, and read fixable.
- `ReadFixable` read failures are cleared by a write to the same sector.
- `ClearErrors` clears mode counters and periods; `ClearFaults` drops persistent sector faults.
- Multiple persistent modes on one sector can combine into internal `AllPersist`.
- The module description marks the personality deprecated.

## Risks And Review Focus
- Fault table capacity is fixed at 50 sectors; excess persistent faults are ignored.
- The request is still sent to the backing device for most failure modes, so this is failure simulation rather than media write suppression except for `WriteAll`.
- Persistent-fault mutation has minimal synchronization and should remain test-only.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-faulty.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-linear.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-linear.c

## Purpose
Implements the deprecated MD `linear` personality, concatenating component devices into a single logical address space.

## Main Interfaces
- Mapping: `which_dev()`, `linear_make_request()`.
- Configuration: `linear_conf()`, `linear_run()`, `linear_add()`, `linear_free()`.
- Size/status: `linear_size()`, `linear_status()`, `linear_quiesce()`.
- Registered personality: `linear_personality`.

## Control Flow
`linear_conf()` builds a `linear_conf` with one `dev_info` per raid disk, validates raid-disk numbering, optionally rounds rdev sizes down to `chunk_sectors`, stacks queue limits, records discard support, computes cumulative end sectors, and stores a stable copy of `raid_disks`.

`linear_make_request()` handles flushes through MD flush logic, binary-searches the component containing the bio sector, validates bounds and broken-device state, splits bios that cross component boundaries, remaps the bio sector to the component’s `data_offset`, ignores discards on devices without discard support, traces the remap, applies write-same/write-zeroes checks, and submits the bio to the component.

`linear_add()` supports growing the array by replacing the private configuration with a newly allocated one under MD suspend/resume, incrementing `raid_disks`, updating capacity, and freeing the old config with RCU.

## State And Synchronization
`mddev->private` points to `linear_conf`. Config replacement uses `rcu_assign_pointer()` and `kfree_rcu()` because old readers can still walk the old disk array. Array-wide changes are bracketed by `mddev_suspend()` and `mddev_resume()`.

## Integration Points
Uses MD core personality registration, no-bitmap validation, disk limit stacking, integrity registration, flush handling, capacity updates, block remap tracing, and write-same/write-zeroes checks.

## Notable Behaviors
- Logical mapping is cumulative and found via binary search over `end_sector`.
- Any component supporting discard enables discard at the MD queue; per-bio discard is silently completed if the chosen component lacks discard.
- Hot-add requires the new rdev’s saved raid disk to equal the current number of raid disks.
- The status output reports chunk-sector rounding in KiB.

## Risks And Review Focus
- Boundary splitting must ensure the original remainder is submitted after the split bio and with correct chaining.
- Discard support is coarse at queue level but per-device at submission, which can make discard behavior uneven.
- Config replacement relies on all readers honoring RCU lifetime assumptions.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-linear.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-linear.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-linear.h

## Purpose
Defines private data structures for the MD linear personality.

## Main Interfaces
- `struct dev_info`: component `md_rdev` pointer plus cumulative `end_sector`.
- `struct linear_conf`: RCU head, total `array_sectors`, copied `raid_disks`, and flexible `disks[]` array.

## Control Flow
No executable control flow. The layout supports fast binary-search mapping in `md-linear.c`.

## State And Synchronization
`linear_conf` includes `struct rcu_head` so old configurations can be freed after RCU grace periods when hot-add swaps in a new mapping.

## Integration Points
Included only by the linear personality implementation.

## Notable Behaviors
- `raid_disks` is intentionally copied into the configuration so readers can iterate the flexible array safely even if `mddev->raid_disks` changes during hot-add.

## Risks And Review Focus
- Any structure changes must preserve the flexible-array allocation pattern used by `struct_size(conf, disks, raid_disks)`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-linear.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-multipath.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-multipath.c

## Purpose
Implements the deprecated MD `multipath` personality, routing I/O over one of several equivalent block-device paths and retrying failed non-readahead I/O on another path.

## Main Interfaces
- Path selection and request handling: `multipath_map()`, `multipath_make_request()`, `multipath_end_request()`, `multipath_end_bh_io()`.
- Retry handling: `multipath_reschedule_retry()`, `multipathd()`.
- Error and membership: `multipath_error()`, `multipath_add_disk()`, `multipath_remove_disk()`.
- Lifecycle/status/size: `multipath_run()`, `multipath_free()`, `multipath_status()`, `multipath_size()`.
- Registered personality: `multipath_personality`.

## Control Flow
`multipath_run()` validates level and no-bitmap state, allocates `mpconf` and the path array, records valid rdevs, counts working paths, sets degraded count, initializes a mempool of retry buffers, starts the `multipathd` thread, sets size, and registers integrity.

`multipath_make_request()` handles flushes through MD flush logic, allocates a `multipath_bh`, selects the first in-sync non-faulty path under RCU while incrementing `nr_pending`, clones the bio into the embedded bio, remaps it by the selected rdev’s data offset, sets failfast transport, and submits it.

On completion, successful bios complete the master bio and free the mempool object. Failed non-readahead bios call `md_error()`, log the sector, and place the request on `retry_list`; readahead failures complete as errors. `multipathd()` drains retry entries, selects another path, remaps the embedded bio again, and resubmits or reports unrecoverable failure.

## State And Synchronization
`mpconf` stores the path array, raid disk count, device lock, retry list, and mempool. Path pointer reads use RCU. `device_lock` protects degraded updates and retry-list manipulation. Rdev pending counts prevent hot-remove while I/O is active.

## Integration Points
Uses MD core flush handling, error handling, recovery checks, integrity registration, thread registration, hot add/remove hooks, disk limit stacking, write-same/write-zeroes checks, and MD personality registration.

## Notable Behaviors
- Path selection is simple first-available selection; comments mention future read balancing but none is implemented.
- Only non-readahead failed I/O is retried.
- `multipath_error()` refuses to disable the last remaining path.
- Hot-remove refuses operational paths or paths with pending I/O unless removal is synchronized.
- Hot-add installs the rdev with RCU assignment and decrements degraded count.

## Risks And Review Focus
- Retry bio reinitialization copies the master bio back into the embedded bio; preserving completion/private fields afterward is critical.
- Failure and removal paths depend on `nr_pending` and RCU ordering to avoid use-after-free.
- The personality is deprecated and much simpler than DM multipath; assumptions should not be generalized to modern multipath behavior.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-multipath.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-multipath.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/md-multipath.h

## Purpose
Defines private structures for the deprecated MD multipath personality.

## Main Interfaces
- `struct multipath_info`: one path entry containing an `md_rdev` pointer.
- `struct mpconf`: MD backpointer, path array, raid disk count, device lock, retry list, and retry-object mempool.
- `struct multipath_bh`: per-I/O retry context containing MD pointer, master bio pointer, embedded cloned bio, selected path, and retry-list node.

## Control Flow
No executable control flow. The structures support request cloning, completion, and retry scheduling in `md-multipath.c`.

## State And Synchronization
`mpconf->device_lock` protects retry-list updates and degraded/path state changes. The path array is read with RCU in the implementation. `multipath_bh` objects are allocated from a mempool to guarantee retry context availability under I/O pressure.

## Integration Points
Included by the multipath personality implementation and tied to MD core `md_rdev`, `mddev`, and block-layer `bio` structures.

## Notable Behaviors
- The embedded bio in `multipath_bh` avoids separate bio allocation for retries after the initial mempool object has been obtained.
- `master_bio` is kept so final completion reports status to the original upper-layer bio.

## Risks And Review Focus
- Structure lifetime is coupled to mempool allocation/free in completion paths; missing completion or double completion would leak or double-free retry contexts.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md-multipath.h -->