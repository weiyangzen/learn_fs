# sources/distributed-fs/ceph-client/drivers/md/md.c lines 10021-11011

## Scope And Purpose

This chunk covers the final third of the Linux MD RAID core implementation in `drivers/md/md.c`. It starts in the middle of `rdev_addable()` and then handles generic spare removal/addition, recovery and resync thread orchestration, sync-thread cleanup, bad-block log updates, reboot shutdown handling, module initialization and exit, clustered superblock reload, early boot autodetection, and module parameters.

The code is the array-management backplane used by MD personalities such as raid1, raid5/6, raid10, multipath, linear, and raid0. Personality modules provide layout-specific callbacks (`hot_add_disk`, `hot_remove_disk`, `sync_request`, `spare_active`, reshape hooks, resize hooks), while this chunk decides when those callbacks are invoked, how recovery state bits are transitioned, when metadata is persisted, and how sysfs/proc/module lifecycle events are exposed.

This is not Ceph-specific logic despite living under the repository's `ceph-client` source tree mirror. It is generic kernel MD RAID code and integrates with block devices, sysfs/kernfs, workqueues, reboot notifiers, procfs, bitmap code, bad-block tracking, and clustered MD metadata.

## Important APIs, Types, And Functions

Spare and recovery-selection helpers:

- `rdev_addable(struct md_rdev *rdev)` decides whether an unassigned `md_rdev` may be handed to the active personality. The chunk begins in this function. It rejects candidate, already assigned, or faulty devices; permits journal disks; permits normal additions for read-write arrays; and, for read-only arrays, permits only re-add of a previously assigned role when the device is not marked `Bitmap_sync`.
- `md_spares_need_change(struct mddev *mddev)` performs an RCU scan of `mddev->disks` and returns true if any device is removable or addable.
- `remove_spares(struct mddev *mddev, struct md_rdev *this)` calls `mddev->pers->hot_remove_disk()` for removable devices, unlinks successful removals from sysfs, saves the old role in `saved_raid_disk`, sets `raid_disk = -1`, and notifies `degraded`.
- `remove_and_add_spares(struct mddev *mddev, struct md_rdev *this)` performs the paired remove/add pass. It avoids targeted removals while `MD_RECOVERY_RUNNING` is set, resets `recovery_offset` for non-journal additions, calls `mddev->pers->hot_add_disk()`, links successful additions into sysfs, emits an MD event, and sets `MD_SB_CHANGE_DEVS`.
- `md_choose_sync_action(struct mddev *mddev, int *spares)` chooses the next sync-class action: reshape first, then existing resync by `resync_offset`, then recovery after adding spares or lazy recover, then deferred user/requested sync actions.

Recovery orchestration:

- `md_start_sync(struct work_struct *ws)` is the `mddev->sync_work` workqueue function. It may temporarily suspend the array to change spares outside reshape, locks the array, removes/adds spares for read-only arrays, chooses a sync action for read-write arrays, flushes all bitmap pages before recovery with bitmap-backed spares, registers `md_do_sync` as `sync_thread`, wakes it, updates sysfs, and cleans state if no sync can run.
- `unregister_sync_thread(struct mddev *mddev)` decides whether a running sync thread is ready to be reaped. If `MD_RECOVERY_DONE` is not set it suppresses another `MD_RECOVERY_NEEDED`; otherwise it calls `md_reap_sync_thread()`.
- `md_should_do_recovery(struct mddev *mddev)` is the fast precheck used by `md_check_recovery()`. It returns true for pending/done recovery, metadata updates other than pure `MD_SB_CHANGE_PENDING`, safemode clean transitions, and immediate safe-mode shutdown synchronization.
- `md_check_recovery(struct mddev *mddev)` is exported and called by per-array management threads. It runs bitmap daemon work, reacts to signals by entering immediate safemode when applicable, performs metadata updates, handles read-only recovery cleanup, processes clustered removals, marks arrays in sync during safemode, reaps completed sync threads, and queues `md_start_sync()` when `MD_RECOVERY_NEEDED` can proceed and recovery is not frozen.
- `md_reap_sync_thread(struct mddev *mddev)` is exported and performs sync-thread teardown. It unregisters the thread, increments `sync_seq`, activates spares on successful non-requested recovery, clears stale `saved_raid_disk` values when no longer degraded, updates superblocks, finishes clustered resync locks, clears recovery action bits, propagates cluster reshape size changes, re-arms `MD_RECOVERY_NEEDED` for a final pass, emits sysfs notifications/events, optionally queues `event_work`, and wakes `resync_wait`.

Device state, reshape, and bad blocks:

- `md_wait_for_blocked_rdev(struct md_rdev *rdev, struct mddev *mddev)` notifies the rdev state sysfs node, waits up to five seconds for `rdev_blocked(rdev)` to clear, then drops the pending reference via `rdev_dec_pending()`.
- `md_finish_reshape(struct mddev *mddev)` updates every rdev's usable sector count and commits `new_data_offset` into `data_offset` after a personality reports reshape completion.
- `rdev_set_badblocks(struct md_rdev *rdev, sector_t s, int sectors, int is_new)` records bad sectors in the rdev bad-block log after translating from array-relative sectors to old or new data offset. It ignores faulty devices, fails the rdev through `md_error()` if the bad-block log cannot record the range, notifies external bad-block users when needed, marks clean/pending superblock changes, and wakes the array thread.
- `rdev_clear_badblocks(struct md_rdev *rdev, sector_t s, int sectors, int is_new)` clears a bad-block range after the same offset translation and notifies external bad-block sysfs state if relevant.

Module lifecycle and global lifecycle:

- `md_notify_reboot()` is a reboot notifier that walks `all_mddevs`, takes references safely under `all_mddevs_lock`, stops writes for active arrays, and forces persistent arrays into safemode `2` so metadata is synchronized promptly.
- `md_geninit()` creates `/proc/mdstat`.
- `md_init()` initializes bitmap and llbitmap support, allocates the `md_misc` workqueue, registers the legacy `md` major and dynamic `mdp` major, registers the reboot notifier and `dev/raid` sysctl table, then creates proc state.
- `md_exit()` unregisters block majors/notifiers/sysctl, wakes `mdstat` pollers until none remain, removes `/proc/mdstat`, exports and drops all arrays, then destroys `md_misc_wq` and bitmap support.
- `get_ro()` and `set_ro()` expose the `start_ro` module parameter around the global `start_readonly` setting.
- Module parameters exported here include `start_ro`, `start_dirty_degraded`, `new_array`, `create_on_open`, `legacy_async_del_gendisk`, and `check_new_feature`.

Clustered metadata reload and boot autodetect:

- `check_sb_changes(struct mddev *mddev, struct md_rdev *rdev)` interprets a freshly loaded v1 superblock from one clustered member. It applies remote size changes, role changes, candidate add failures, spare activation, remote faulty/journal roles, `raid_disks` changes, remote reshape start/finish, and finally updates `mddev->events`.
- `read_rdev(struct mddev *mddev, struct md_rdev *rdev)` swaps in a newly allocated superblock page, reloads it through the current `super_types[major_version].load_super()` operation, restores the old page on failure, updates `recovery_offset` when present, and calls `spare_active()` when a remote node finished recovery for a spare.
- `md_reload_sb(struct mddev *mddev, int nr)` is exported for cluster code. It locates an rdev by descriptor number, reloads that rdev, applies `check_sb_changes()`, then reloads all non-faulty rdevs to refresh recovery offsets.
- When built into the kernel rather than as a module, `md_autodetect_dev(dev_t dev)` queues devices discovered by partition scanning, and `md_autostart_arrays(int part)` imports those devices as v0.90-style rdevs, marks non-faulty devices `AutoDetected`, attaches them to `pending_raid_disks`, and calls `autorun_devices(part)`.

Important structures and state referenced by this chunk:

- `struct mddev`: central array object; fields used heavily here include `pers`, `disks`, `ro`, `recovery`, `sb_flags`, `reshape_position`, `resync_offset`, `sync_thread`, `thread`, `sync_work`, `bitmap_ops`, `safemode`, `in_sync`, `degraded`, `raid_disks`, `dev_sectors`, `events`, cluster fields, sysfs kernfs nodes, `sync_seq`, and the array locks/waitqueues.
- `struct md_rdev`: component device object; key fields include `flags`, `raid_disk`, `saved_raid_disk`, `desc_nr`, `recovery_offset`, `data_offset`, `new_data_offset`, `sectors`, `nr_pending`, `badblocks`, `sb_page`, and sysfs kernfs nodes.
- `enum recovery_flags`: `MD_RECOVERY_NEEDED`, `RUNNING`, `INTR`, `DONE`, `FROZEN`, `SYNC`, `REQUESTED`, `CHECK`, `RECOVER`, `RESHAPE`, `MD_RESYNCING_REMOTE`, and `LAZY_RECOVER` drive action selection and thread lifecycle.
- `enum mddev_sb_flags`: `MD_SB_CHANGE_DEVS`, `MD_SB_CHANGE_CLEAN`, `MD_SB_CHANGE_PENDING`, and `MD_SB_NEED_REWRITE` drive metadata persistence through `md_update_sb()`.

## Control Flow And Runtime Behavior

The generic recovery loop is split between the array management thread and the `md_misc_wq` workqueue. `md_check_recovery()` runs in the per-array thread context and is the coordinator. It first services bitmap daemon work, converts pending signals into immediate safemode for internally managed metadata, and returns early unless `md_should_do_recovery()` sees actual work. When it gets the array reconfiguration lock, it handles read-only arrays specially, updates metadata when needed, reaps finished sync threads, and only then sets `MD_RECOVERY_RUNNING` and queues `md_start_sync()` if `MD_RECOVERY_NEEDED` was set and the array is not frozen.

`md_start_sync()` is the slow start path for sync-class work. Before taking `reconfig_mutex`, it may suspend the mddev if a spare topology change is required and no reshape is active; this prevents live IO from racing the personality's hot-add/hot-remove operations. For read-only arrays it only removes failed devices and re-adds already in-sync devices, then clears recovery state without creating a sync thread. For read-write arrays it calls `md_choose_sync_action()`, checks for a personality `sync_request` callback, flushes all bitmap pages when recovering with spares, registers a `md_do_sync` thread named either `reshape` or `resync`, resumes the array without re-setting `MD_RECOVERY_NEEDED`, wakes the thread, and updates user-visible state.

Action priority is intentionally strict. A live reshape (`reshape_position != MaxSector`) wins over all other actions and requires `pers->check_reshape()` to accept it. An interrupted or active resync (`resync_offset < MaxSector`) wins next and removes spares before setting `MD_RECOVERY_SYNC`. Only when neither reshape nor resync is pending does the code remove failed devices, add spares, and start `MD_RECOVERY_RECOVER`. User-requested `check`/`repair` style actions are delayed to `md_do_sync()` by leaving `MD_RECOVERY_SYNC` set without choosing recover or reshape in this helper.

Sync completion flows back through `MD_RECOVERY_DONE`. `md_do_sync()` sets that bit and wakes the mddev thread. The next `md_check_recovery()` sees `MD_RECOVERY_RUNNING` and calls `unregister_sync_thread()`. If the sync thread is still not done, the helper only clears `MD_RECOVERY_NEEDED`; if done, `md_reap_sync_thread()` unregisters the thread, persists metadata, activates spares on successful recovery, clears action bits, wakes waiters, and sets `MD_RECOVERY_NEEDED` again so the next pass can catch follow-up metadata or topology work.

Read-only arrays are deliberately constrained. `md_start_sync()` will not launch a sync thread when `!md_is_rdwr(mddev)`. `rdev_addable()` only permits journal devices or rdevs whose `saved_raid_disk` indicates a re-add and whose bitmap status does not imply they are too stale. `md_check_recovery()` clears `Blocked` flags on already in-sync internally managed read-only arrays, calls `md_reap_sync_thread()` with `MD_RECOVERY_INTR` set to complete spare activation bookkeeping, and may queue `md_start_sync()` only to perform spare add/remove changes.

Clustered MD integrates by reloading peer-written superblocks. `md_reload_sb()` reloads one descriptor-specified rdev and feeds it to `check_sb_changes()`. That routine uses superblock fields as the remote source of truth for array size, rdev roles, raid disk count, reshape status, recovery offsets, and event count. Role changes can cause local candidate removal, local spare activation through `remove_and_add_spares()`, local `md_error()` marking, and setting `MD_RECOVERY_NEEDED` so the ordinary management thread handles follow-up resync.

Bad-block updates are immediate metadata triggers. `rdev_set_badblocks()` translates the reported sector by `data_offset` or `new_data_offset`, records it through the generic badblocks API, and sets both `MD_SB_CHANGE_CLEAN` and `MD_SB_CHANGE_PENDING` in `mddev->sb_flags`. That forces the md thread to persist clean/active metadata state and prevents a bad-block record from sitting only in memory. If the bad-block table cannot accept the range, the code fails the rdev to avoid future reads from sectors known to be bad but not persistently recorded.

Module lifetime is boot/module scoped. `md_init()` establishes shared facilities before arrays exist: bitmap submodules, workqueue, block majors, reboot notifier, sysctl table, and `/proc/mdstat`. `md_exit()` reverses the externally visible registrations first, wakes any mdstat pollers so unload cannot hang behind `poll()`, then exports all mddevs under reference protection and destroys the shared workqueue after mddev destruction work has had a chance to run.

## State And Persistence Behavior

Array recovery state is encoded in `mddev->recovery` bits. This chunk sets, clears, and orders those bits carefully because sysfs `sync_action`, the md thread, the workqueue starter, and the sync thread all observe them. `MD_RECOVERY_RUNNING` is set before `MD_RECOVERY_NEEDED` is cleared to avoid transient user-visible idle states. `MD_RECOVERY_DONE` is consumed only by the management thread, and `MD_RECOVERY_NEEDED` is set again after reaping to force a final consistency pass.

Metadata persistence is driven by `mddev->sb_flags`. Spare removal/addition sets `MD_SB_CHANGE_DEVS`; bad-block additions set `MD_SB_CHANGE_CLEAN` and `MD_SB_CHANGE_PENDING`; `md_do_sync()` completion before this chunk set pending/device changes, and `md_reap_sync_thread()` calls `md_update_sb(mddev, 1)`. `md_check_recovery()` calls `md_update_sb(mddev, 0)` whenever non-pending-only superblock flags exist on a read-write array. The code treats pure `MD_SB_CHANGE_PENDING` as a clean-to-active transition that does not itself require generic recovery action.

Spare identity persistence uses `rdev->saved_raid_disk`. When a removable active rdev is hot-removed successfully, its old `raid_disk` role is saved and `raid_disk` becomes `-1`. That saved role allows a read-only re-add without forcing a normal recovery. Once the array is no longer degraded, `md_reap_sync_thread()` clears all `saved_raid_disk` values because stale role hints could otherwise drive incorrect re-add behavior later.

Bad-block persistence lives in `rdev->badblocks` and, for external bad-block metadata, external userspace/metadata handlers are signaled through sysfs notifications. `rdev_set_badblocks()` does not record new bad blocks for already faulty rdevs to avoid unnecessary metadata churn and possible deadlock with external metadata managers trying to remove the device. Clearing bad blocks updates memory state and sysfs notifications but does not set the same superblock flags in this chunk.

Clustered persistence uses on-disk v1 superblock fields as the cross-node state carrier. `check_sb_changes()` reads `size`, `dev_roles`, `feature_map`, `recovery_offset`, `raid_disks`, `reshape_position`, and `events` from the freshly loaded page. Local state is reconciled to those fields and `mddev->events` is advanced to the remote value only after all role/reshape/size changes are processed.

Module-global state includes `md_misc_wq`, `mdp_major`, `raid_table_header`, `md_notifier`, `md_unloading`, `all_mddevs`, the boot-only `all_detected_devices` list, and module parameters. `md_exit()` must clear or unregister externally reachable state before destroying internal facilities; otherwise mdstat pollers, block-device opens, or reboot notifier callbacks could race teardown.

## Dependencies And Integration Points

Personality callbacks are central. This chunk depends on `struct md_personality` methods including:

- `hot_remove_disk()` and `hot_add_disk()` for topology changes.
- `check_reshape()`, `start_reshape()`, `finish_reshape()`, and `update_reshape_pos()` for reshape negotiation and cluster reconciliation.
- `sync_request()` for actual resync/recover/check/repair IO.
- `spare_active()` for committing recovered spares into active roles.
- `resize()` for remote size changes in clustered arrays.

The generic MD core around this chunk provides `md_do_sync()`, `md_register_thread()`, `md_unregister_thread()`, `md_wakeup_thread()`, `md_update_sb()`, `md_error()`, `md_kick_rdev_from_array()`, `mddev_suspend()`, `__mddev_resume()`, `mddev_lock_nointr()`, `mddev_trylock()`, `mddev_unlock()`, `set_in_sync()`, `sysfs_link_rdev()`, `sysfs_unlink_rdev()`, `md_new_event()`, `export_array()`, `md_import_device()`, and `autorun_devices()`.

Bitmap integration appears in three places: `md_check_recovery()` calls `bitmap_ops->daemon_work`, `md_start_sync()` flushes all bitmap pages before recovery with newly added spares, and `check_sb_changes()` asks bitmap code to update its superblock view after remote resize.

Sysfs and procfs are the user-visible integration surface. This chunk notifies `sysfs_degraded`, `sysfs_action`, `sysfs_completed`, rdev `sysfs_state`, `sysfs_badblocks`, and `sysfs_unack_badblocks`. It creates `/proc/mdstat` at init and removes it at exit. `md_new_event()` wakes md event/poll users after topology or sync state changes.

Cluster integration depends on `mddev_is_clustered()`, rdev `ClusterRemove` and `Candidate` flags, `mddev->cluster_ops->resync_finish()`, `resync_status_get()`, and `update_size()`. Remote superblock reload is exported as `md_reload_sb()`.

Kernel subsystem dependencies include workqueues (`md_misc_wq`), RCU rdev iteration, spinlocks and mutexes, waitqueues, reboot notifiers, sysctl registration, block major registration, procfs, module parameters, badblocks API, endian helpers for v1 superblocks, page allocation/refcounting for superblock pages, and built-in boot autodetection when `MODULE` is not defined.

## Risks And Edge Cases

- The chunk starts mid-`rdev_addable()`, so final per-file research should merge this with the preceding lines that establish the local `mddev` pointer and early null check.
- `remove_and_add_spares()` refuses targeted removals while `MD_RECOVERY_RUNNING` is set, but untargeted startup can still remove failed devices as part of action selection. Personality callbacks must be safe under the mddev reconfiguration lock and array suspension rules.
- `md_start_sync()` intentionally resumes suspended arrays with `__mddev_resume(mddev, false)` because it was already triggered by `MD_RECOVERY_NEEDED`. Accidentally switching to a resume path that re-sets recovery-needed can reintroduce repeated queueing loops like the bug referenced in the source comment.
- `md_choose_sync_action()` prioritizes reshape above all else. Any personality `check_reshape()` bug or missing callback can block other recovery work even when spares are available.
- `md_reap_sync_thread()` sets `MD_RECOVERY_NEEDED` after clearing action bits. Consumers must tolerate this final double-check pass and avoid interpreting it as proof that a new full sync is required.
- `md_should_do_recovery()` ignores pure `MD_SB_CHANGE_PENDING`, treating it as an in-progress clean-to-active transition. Bugs that leave other superblock flags unset could delay metadata persistence until another trigger.
- Read-only array handling calls `md_reap_sync_thread()` even when there is "no thread" to run personality spare-active cleanup. Changes to `md_reap_sync_thread()` must preserve that implicit no-thread cleanup contract or read-only re-add behavior can regress.
- `rdev_set_badblocks()` returns success for faulty rdevs without recording the range. This avoids external metadata deadlocks but means callers must not use the return value alone as evidence that a new persistent bad-block entry exists.
- If `badblocks_set()` fails, the rdev is failed immediately through `md_error()`. Systems with exhausted bad-block tables can therefore degrade arrays aggressively rather than risk unsafe reads.
- `read_rdev()` temporarily replaces `rdev->sb_page`. Its failure path must restore the old page and `sb_loaded` exactly; leaks or stale page pointers would corrupt future metadata updates.
- `check_sb_changes()` trusts remote superblock role values enough to call local `md_error()` and activate spares. Cluster split-brain or stale superblock reads could cause local topology churn, so cluster locking and event ordering outside this chunk are critical.
- `md_notify_reboot()` uses `mddev_trylock()`. Arrays it cannot lock during reboot notifier execution may not get `__md_stop_writes()` or safemode `2` from this pass.
- `md_exit()` waits for mdstat pollers using exponential sleep without an explicit maximum in the loop. It relies on wakeups and pollers exiting after `md_unloading` is set.
- `md_exit()` destroys `md_misc_wq` but this chunk's `md_init()` failure cleanup also destroys it on partial setup. Error labels must stay aligned with initialization order.
- `md_init()` calls `md_llbitmap_exit()` on workqueue allocation failure or later bitmap/registration failure paths, but `md_exit()` only calls `md_bitmap_exit()` in this chunk. The final merged report should verify whether `md_bitmap_exit()` also covers llbitmap teardown or whether this mirror differs from upstream expectations.
- Boot autodetect imports devices with superblock format `90` and skips faulty rdevs without freeing them in the visible snippet. The merge lane should inspect surrounding import/autorun ownership to confirm lifetime handling for skipped faulty autodetected devices.

## Test Signals

Build and static analysis:

- Compile MD core with common RAID personalities enabled as built-in and as modules, including bitmap, badblocks, sysfs, procfs, and clustered MD configurations.
- Run sparse/lockdep-style checks around `mddev->reconfig_mutex`, `mddev->lock`, `all_mddevs_lock`, RCU rdev iteration, `mddev_trylock()` paths, and workqueue callbacks.
- Validate init/exit error labels with fault injection for `md_bitmap_init()`, `md_llbitmap_init()`, `alloc_workqueue()`, `__register_blkdev(MD_MAJOR)`, dynamic `mdp` major registration, sysctl/proc creation, and module unload.

Recovery and spare tests:

- Add and remove spares on read-write raid1/raid5/raid10 arrays and verify `sysfs` links, `degraded`, `sync_action`, `sync_completed`, md events, and superblock event counts.
- Re-add a previously removed device to a read-only array and confirm only eligible `saved_raid_disk` devices are accepted, with bitmap-stale devices rejected.
- Force failed active devices with pending IO and with `Blocked` set to verify `rdev_removeable()` and `remove_spares()` do not remove unsafe rdevs before pending/blocking state clears.
- Exercise reshape, resync, recover, lazy recover, check, and repair requests together to verify priority in `md_choose_sync_action()` and no accidental sync-thread start while frozen.
- Interrupt and complete a sync thread, then verify `MD_RECOVERY_DONE`, `md_reap_sync_thread()`, spare activation, `saved_raid_disk` clearing, `sync_seq` increment, final `MD_RECOVERY_NEEDED` pass, and sysfs notifications.

Bad-block and blocked-rdev tests:

- Inject bad-block additions on normal, faulty, external-BBL, and table-full rdevs; verify offset translation by old/new data offset, sysfs notifications, superblock flags, md thread wakeup, and failure through `md_error()` when the table cannot record.
- Clear bad blocks for internal and external-BBL rdevs and verify `sysfs_badblocks` notification behavior.
- Hold an rdev in blocked state and verify `md_wait_for_blocked_rdev()` emits state notification, waits no longer than the timeout, and drops the pending reference.

Clustered MD tests:

- Simulate remote resize through v1 superblock `size` changes and verify personality `resize()` plus bitmap superblock update.
- Simulate remote role changes for candidates, activated spares, faulty roles, journal roles, and `ClusterRemove`; verify local candidate removal, `remove_and_add_spares()`, `md_error()`, `MD_RECOVERY_NEEDED`, and md thread wakeups.
- Simulate remote reshape start and finish with `MD_RESYNCING_REMOTE` set; verify `reshape_position`, `update_reshape_pos()`, and `start_reshape()` calls.
- Reload all non-faulty rdevs after one descriptor reload and confirm recovery offsets are refreshed across the array.

Lifecycle and boot tests:

- Verify reboot notifier behavior for lockable and busy arrays: stopped writes, safemode `2` for persistent arrays, no deadlock under `all_mddevs_lock`, and correct refcount release.
- Boot with autodetected v0.90 RAID partitions and confirm `md_autodetect_dev()` queueing, `AutoDetected` flagging, `pending_raid_disks` population, and `autorun_devices(part)` behavior.
- Poll `/proc/mdstat` during module unload and confirm `md_unloading` wakeups let pollers leave and unload completes.
- Exercise module parameters `start_ro`, `start_dirty_degraded`, `new_array`, `create_on_open`, `legacy_async_del_gendisk`, and `check_new_feature` through sysfs/module loading where applicable.

## Cross-Chunk Notes

The preceding chunk contains the start of `rdev_addable()` plus definitions of `rdev_removeable()`, `rdev_is_spare()`, `md_do_sync()`, and sync-position logic that feed directly into this chunk's recovery selection. The final per-file report should connect those helpers with `md_start_sync()` and `md_reap_sync_thread()`.

Earlier `md.c` chunks define `md_update_sb()`, `sync_sbs()`, `md_error()`, `md_import_device()`, `autorun_devices()`, sysfs attributes, IO accounting, `md_run()`, stop/read-only transitions, ioctl handling, block-device operations, `/proc/mdstat` support, and cluster setup. Those definitions provide the persistence, userspace, and lifecycle context for this chunk's exported functions.
