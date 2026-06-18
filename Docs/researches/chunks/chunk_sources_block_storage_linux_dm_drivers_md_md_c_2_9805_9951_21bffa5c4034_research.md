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