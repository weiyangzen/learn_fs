# Group Research: group_511_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_u_e3b6daa23d9c

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_panic.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_panic.c

## Overview
`ufs_panic.c` implements UFS fix-on-failure handling. Instead of always escalating filesystem metadata failures to `CE_PANIC`, it can mark the superblock bad, queue a failure record, drive `lockfs` into an error lock, wait for repair activity, optionally unmount, and fall back to panic when recovery is unsafe or impossible.

## Main Responsibilities
- Provide `ufs_fault()` as the panic-path replacement used by UFS callers.
- Maintain the global `ufs_fix` queue of `ufs_failure_t` records.
- Initialize global and per-mount fix-on-failure state through `ufsfx_init()` and `ufsfx_mount()`.
- Track failure state transitions from initialization through queued, try-lock, locked, fixing, fixed, not-fixed, replica, unmount, or panic states.
- Coordinate with `lockfs`, fsck, the UFS hlock thread, and unmount paths.
- Publish poll wakeups for administrative visibility of error/fix state.
- Keep debug-only state names, error names, action names, and queue dumping helpers.

## Key Control Flow
- `ufs_fault_v()` first writes `FSBAD` directly to the superblock buffer, bypassing normal logging semantics, then triages the failure.
- `triage()` refuses recovery when the system is already panicking, the vnode/ufsvfs is missing, mount policy says `onerror=panic`, or accounting/swap usage would deadlock repair.
- Recoverable failures start the `ufsfx_thread_fix_failures` worker if needed, create a failure record with `init_failure()`, and append it with `queue_failure()`.
- `ufsfx_thread_fix_failures()` sleeps on `ufs_fix`, then repeatedly calls `ufsfx_do_failure_q()` until all nonterminal failure records are done or waiting.
- `ufsfx_do_failure_q()` walks the queue, calls the current state's handler, and computes the shortest retry delay needed by active failures.
- `sf_found_queue()` detects replica failures for a filesystem that already has an active failure and chooses panic, replica, or try-lock behavior based on mount flags and `fx_current`.
- `sf_found_trylck()` polls current lockfs status and calls `set_lockfs()` to establish `LOCKFS_ELOCK`.
- `sf_found_lock_fix_cmn()` watches for fsck start/completion by reading the on-disk superblock and lockfs comment, warning when repair is late.
- `sf_found_umount()` attempts `dounmount()` for `onerror=umount` filesystems after error locking.
- Terminal states clear `fx_current`, note success/failure, and schedule possible fix-thread shutdown.

## State and Locking
- `ufs_fix.uq_mutex` protects the global failure queue and worker state.
- Each `ufs_failure_t` has `uf_mutex`; state transitions require it.
- Per-filesystem `vfs_lock` is used opportunistically on panic paths, with counters for lock-violation races.
- Failure records retain defensive copies/pointers for mount name, ufsvfs, vfs, superblock buffer, lockfs state, and retry timings.
- `set_state()` validates allowed transitions against `state_desc[]` and invokes per-state callbacks before committing state.
- `panicstr` short-circuits recovery and moves records to not-fixed behavior.

## Notable Behaviors
- The most restrictive active policy wins: panic, lock-only, lock-and-unmount, or default repair.
- Secondary failures on a filesystem with an active failure become `UF_REPLICA`.
- `fsck_active()` identifies fsck by searching lockfs comments for the `"[pid:"` marker while the filesystem remains error-locked.
- Repair-completion timeout is scaled by filesystem size using `SecondsPerGig`.
- `ufsfx_unmount()` nulls live ufsvfs/vfs pointers in outstanding failure records so delayed processing does not dereference freed mount state.
- `ufsfx_unlockfs()` treats successful unlock during repair as fixed, passing through `UF_FIXING` when needed to preserve transition rules.

## Error Handling and Recovery Boundaries
- Nonrecoverable `lockfs` failures such as `EACCES`, `EPERM`, `EIO`, `EROFS`, or `EDEADLK` escalate to panic unless unmount is explicitly viable.
- Transient `EBUSY`/`EAGAIN` errors defer retry and may infer that repair has started.
- `EINVAL` while locking is treated as already unmounted/not fixed.
- Allocation or validation failures in `init_failure()` fall back to real panic.

## Research Notes
This file is a recovery controller, not a formatting wrapper around panics. Correctness depends on the failure state machine, lock ordering between `ufs_fix`, failure records, `vfs_lock`, and `ul_lock`, and careful avoidance of blocking or recursive repair work on panic-sensitive paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_panic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_snap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_snap.c

## Overview
`ufs_snap.c` implements UFS snapshot create/delete entry points around the generic `fssnap` copy-on-write facility. It validates privilege and filesystem state, pins backing-file vnodes, write-locks the filesystem while snapshot state is established, and seeds the snapshot candidate map from UFS allocation bitmaps.

## Main Responsibilities
- Create snapshots with `ufs_snap_create()`.
- Delete snapshots with `ufs_snap_delete()`.
- Convert user-provided backing file descriptors into held vnode arrays.
- Reject backing files located on the same filesystem being snapshotted.
- Establish a `LOCKFS_WLOCK` during snapshot setup.
- Compute chunk geometry and initialize fssnap metadata.
- Scan cylinder groups to mark chunks containing allocated fragments as copy-on-write candidates.

## Key Control Flow
- `ufs_snap_create()` requires `secpolicy_fs_config()`, rejects read-only filesystems, initializes backing vnodes, verifies the filesystem is unlocked, and write-locks it.
- Snapshot creation only proceeds when `fs_clean` is one of the active/stable/clean/logged states accepted by the code.
- Only one snapshot is allowed per `ufsvfs`; existing `vfs_snapshot` causes `EBUSY`.
- The snapshot chunk size is caller-provided or defaults to `fs_bsize * 4`; it must be at least one fragment and a multiple of fragment size.
- `fssnap_create()` allocates generic snapshot state, then `ufs_snap_find_candidates()` marks chunks containing allocated fragments.
- `fssnap_create_done()` returns the snapshot number, and success stores the snapshot handle in `ufsvfsp->vfs_snapshot`.
- All exits attempt to unlock the filesystem; errors after `fssnap_create()` delete the snapshot state.

## Backing File Handling
- `ufs_snap_init_backfile()` uses `getf()`/`releasef()` to resolve descriptors, holds each backing vnode with `VN_HOLD()`, and returns a NULL-terminated vnode array.
- `release_backing_vnodes()` releases held vnodes and frees the array.
- Backing files on the same mounted UFS instance are rejected to avoid recursive snapshot storage.

## Candidate Bitmap Scan
- `ufs_snap_find_candidates()` reads each cylinder group with `BREAD()`.
- It validates `CG_MAGIC`.
- It reads `cg_blksfree()`; in UFS, allocated fragments are represented by cleared bits.
- For each allocated fragment, it computes the snapshot chunk number and calls `fssnap_set_candidate()`, then skips to the next chunk.

## Error Handling
- User-visible `fiosnapp->error` values distinguish backing-file, lock, cleanliness, busy, chunk-size, create, bitmap, and unlock failures.
- Read-only filesystems return `EROFS`; missing snapshots on delete return `ENOENT`.
- Delete requires privilege and a read-write filesystem before calling `fssnap_delete()`.

## Research Notes
The important behavior is the atomic snapshot establishment under `LOCKFS_WLOCK` and the candidate-map seeding from allocated-fragment state. The file relies on generic fssnap strategy support and stores only one active snapshot handle in `ufsvfs`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_snap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_subr.c

## Overview
`ufs_subr.c` contains shared UFS support routines for mount-instance list management, global sync/update work, inode and indirect-block flushing, clean-state transitions, superblock/summary-info I/O, sticky-directory permission checks, and traditional UFS fragment/block bitmap helpers.

## Main Responsibilities
- Maintain the global `ufs_instances` list with `ufs_vfs_add()` and `ufs_vfs_remove()`.
- Clean delayed forced-unmount `ufsvfs` structures through `ufs_funmount_cleanup()`.
- Implement `ufs_update()` for global UFS sync processing.
- Flush inode data and metadata via `ufs_sync_inode()`, `ufs_syncip()`, `ufs_sync_indir()`, and `ufs_indirblk_sync()`.
- Decide when a filesystem can be marked stable through `ufs_checkclean()`.
- Mark logging filesystems as needing reclaim after unlink with `ufs_setreclaim()`.
- Mark filesystems dirty/active before metadata writes with `ufs_notclean()`.
- Write file blocks, inode blocks, superblocks, and cylinder group summary information.
- Provide fragment accounting and allocation bitmap helpers used by kernel and non-kernel UFS code.

## Sync and Clean-State Flow
- `ufs_update()` builds a temporary list of mounted UFS instances it can `vfs_lock()`, writes modified superblocks, scans inodes, flushes buffers, and then rechecks stable candidates.
- It avoids writing locked/inconsistent superblocks during panic and skips panicking/logging cases where metadata should not be forced out.
- `ufs_sync_inode()` applies cheap-sync filtering, panic filtering, deferred access-time policy, and then either delays inode update or flushes pages through `TRANS_SYNCIP()`.
- `ufs_syncip()` flushes vnode pages and then updates inode metadata according to full-sync versus data-sync semantics.
- `ufs_checkclean()` marks the filesystem `FSSTABLE` only when buffers and inodes are not busy and reclaim state allows it.

## Metadata and Summary Information
- `ufs_sbwrite()` updates `fs_time`, `fs_state`, `fs_clean`, and reclaim bits, logs the superblock delta, writes the superblock buffer, and preserves the in-core `fs_fmod` value.
- `ufs_getsummaryinfo()` either reads summary info from the summary-info area or reconstructs it from cylinder groups when `FS_SI_BAD`.
- `ufs_construct_si()` performs batched asynchronous reads of cylinder groups and copies each `cg_cs`.
- `ufs_putsummaryinfo()` writes summary info back when logging needs it and `vfs_nolog_si` permits delayed summary flushing.
- `still_mounted()` verifies that a stored check node still refers to an active instance before clean-state checking.

## Indirect Block Handling
- `ufs_sync_indir()` flushes all indirect blocks associated with a file, including single, double, and triple indirect levels.
- `ufs_indirblk_sync()` flushes the indirect path needed for a specific file offset.
- Both skip work when logging is enabled because allocation metadata is kept current by transactions.
- Debug-only `ufs_badblock()` and `ufs_indir_badblock()` can validate block-number ranges when the expensive tunable is enabled.

## Fragment and Block Helpers
- `fragacct()` updates fragment summary counts using `fragtbl`, `around`, and `inside` tables from `ufs_tables.c`.
- `isblock()`, `clrblock()`, `isclrblock()`, and `setblock()` manipulate free block maps for fragment sizes 1, 2, 4, and 8.
- `skpc()` scans past a repeated character and returns remaining length.

## Locking and Safety
- `ufsvfs_mutex` protects UFS instance lists.
- `ufs_scan_lock` avoids races among update, sync, and unmount inode scans.
- `vfs_lock()` pins a filesystem instance for update work.
- `vfs_lock`, `vfs_lockp`, `i_contents`, `i_tlock`, and `vfs_dqrwlock` are used according to the specific inode/superblock/quota operation.
- Forced-unmount cleanup intentionally delays freeing some `ufsvfs` objects to reduce races with lockfs users.

## Research Notes
This file is the common maintenance layer for UFS consistency. Its riskiest areas are global instance traversal without long-held list locks, clean-state decisions, summary-info reconstruction, and the split behavior between logging and non-logging filesystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_tables.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_tables.c

## Overview
`ufs_tables.c` defines static lookup tables used by UFS fragment allocation and accounting code. These tables encode bit patterns that help identify available fragments inside a filesystem block map.

## Main Responsibilities
- Provide `around[]` and `inside[]` masks used by `fragacct()` to detect fragment runs.
- Provide `fragtbl124[]` for fragment sizes 1, 2, and 4.
- Provide `fragtbl8[]` for fragment size 8.
- Export `fragtbl[MAXFRAG + 1]` to select the right fragment table by `fs_frag`.

## Data Semantics
- `around` and `inside` are used as pattern masks for expressions like `(map & around[size]) == inside[size]`.
- `fragtbl` maps a block bitmap pattern to bits indicating which fragment sizes are available.
- Entries for unsupported fragment counts are NULL.
- The comments preserve the original BSD/VAX `scanc` optimization context, but modern callers use the tables directly from C.

## Dependencies
- Consumed by `fragacct()` and UFS allocation logic that reasons about free fragments inside a block.
- Depends only on UFS constants such as `MAXFRAG` and the `uchar_t` type.

## Research Notes
This file is pure data. Any behavioral change here would affect low-level free-fragment accounting and allocation decisions across UFS.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_thread.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_thread.c

## Overview
`ufs_thread.c` implements reusable UFS queue/thread control plus the background workers that reclaim deleted inodes, shrink idle inode caches, scan for deleted inodes left by prior logging mounts, and hard-lock filesystems whose logs have errored.

## Main Responsibilities
- Provide generic `ufs_q` lifecycle helpers: init, start, exit, suspend, continue, and run.
- Process delayed inode deletion through `ufs_delete()`, `ufs_thread_delete()`, and drain helpers.
- Track unreclaimed delete-queue resources for `statvfs`.
- Maintain global idle inode queues and reclaim idle inodes under memory pressure or high-water conditions.
- Scan filesystems for deleted-but-not-reclaimed inodes with `ufs_thread_reclaim()`.
- Run the global hlock worker through `ufs_thread_hlock()`.
- Purge extended attribute directory contents during inode deletion.

## Generic Queue Protocol
- `ufs_thread_init()` initializes mutex, condition variable, low/high water marks, and thread pointer.
- `ufs_thread_start()` creates a kernel thread at `minclsyspri` if one is not already running.
- `ufs_thread_exit()` sets `UQ_EXIT`, wakes the worker, and joins by saved `t_did`.
- `ufs_thread_suspend()` requests `UQ_SUSPEND` and waits for `UQ_SUSPENDED`.
- `ufs_thread_run()` centralizes worker sleep, suspend, exit, and low-water processing behavior with CPR callbacks.

## Delete Queue Behavior
- `ufs_delete()` frees resources of an idle deleted inode: handles lockfs restrictions, removes extended attributes, truncates data, frees the inode, releases quota state, recycles the vnode, and closes the transaction.
- `ufs_thread_delete()` removes one inode at a time from the per-filesystem delete queue to keep suspend latency low.
- `ufs_delete_drain()` can remove a fixed count, all current entries, or continue until empty.
- `ufs_delete_drain_wait()` drains the queue and synchronizes with the delete thread to satisfy POSIX space-availability semantics after unlink/close.
- `ufs_delete_adjust_stats()` adds queued-but-unreclaimed blocks/files into `statvfs` free counts.

## Idle Inode Reclaim
- The idle subsystem splits idle inodes into hashed “junk” and “useful” queues.
- `ufs_thread_idle()` wakes when the global idle queue exceeds the low-water mark and frees roughly half.
- `ufs_inode_cache_reclaim()` wakes the idle thread when memory pressure occurs and the queue is above halfway.
- `ufs_idle_some()` selects idle inodes round-robin, holds them, removes them from idle state, and calls `ufs_idle_free()`.
- `ufs_idle_free()` flushes/invalidate pages, blocks iget through the inode hash lock, removes the inode from cache, releases quota/shadow state, and returns it to the inode cache.
- `ufs_idle_drain()` drains idle inodes for one vfs or all vfs instances.

## Reclaim and Hlock Workers
- `ufs_thread_reclaim()` scans on-disk dinodes, finds deleted inodes with nonzero mode, igets them, and releases them so normal inactive/delete processing reclaims space.
- On successful reclaim scan, it clears `FS_RECLAIMING` and writes the superblock.
- `ufs_thread_hlock()` waits on `ufs_hlock`, then repeatedly calls `ufs_trans_hlock()` until no retry is needed.
- `ufs_attr_purge()` walks an attribute directory, removes entries from DNLC, decrements link counts, and participates in remove transactions.

## Locking and Transactions
- Delete and reclaim paths coordinate with `lockfs`, `vfs_dqrwlock`, `i_contents`, `i_rwlock`, and quota locks.
- `T_DONTBLOCK` prevents recursive blocking in lockfs/transaction-sensitive contexts.
- Transaction macros wrap truncation, inode free, attribute removal, and commit synchronization.
- Idle freeing carefully uses vnode and inode hash locks to prevent new references while reclaiming.

## Research Notes
This file is the main asynchronous maintenance engine for UFS. The highest-risk areas are queue suspend/exit semantics during unmount, vnode reference invariants in idle reclaim, delayed-delete accounting, and transaction boundaries around inode deletion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_trans.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_trans.c

## Overview
`ufs_trans.c` contains UFS transaction/logging glue. It wraps superblock and inode updates in transaction reservations, pushes logged deltas for buffers, inodes, quotas, and summary info, maintains debug metadata maps, estimates log reservations for writes/truncates, splits large operations, and triggers hard locks when logging errors occur.

## Main Responsibilities
- Hard-lock filesystems with errored logs via `ufs_trans_hlock()`.
- Wake the hlock thread with `ufs_trans_onerror()`.
- Transaction-wrap superblock updates, inode updates, and superblock writes.
- Push logged deltas for summary info, delayed buffers, inodes, directory blocks, and quotas.
- Maintain debug-only metadata maps for static and dynamic metadata regions.
- Calculate log space needed for writes and truncates.
- Split oversized truncate/write operations into log-sized chunks.

## Transaction Wrappers
- `ufs_trans_sbupdate()` wraps `sbupdate()` unless already in `T_DONTBLOCK`; it avoids logging work during panic on trans filesystems.
- `ufs_trans_iupdat()` wraps `ufs_iupdat()` under `i_contents` reader lock.
- `ufs_trans_sbwrite()` wraps `ufs_sbwrite()` under `vfs_lock`.
- `ufs_trans_itrunc()` runs non-logging truncates directly, but for logging filesystems reserves space, sets `T_DONTBLOCK`, and may loop over partial truncates.
- `ufs_trans_write()` performs chunked writes, ending and starting transactions between chunks while preserving the caller’s final end-of-transaction responsibility.

## Delta Push Paths
- `ufs_trans_push_si()` logs cylinder-group summary info from `fs_csp`.
- `ufs_trans_push_buf()` writes delayed-write buffers if still present, otherwise returns `ENOENT`.
- `ufs_trans_push_inode()` igets an inode and writes it if modified.
- `ufs_trans_dir()` maps a directory offset to a disk block and declares a `DT_DIR` delta.
- `ufs_trans_quota()` marks a dquot as participating in a transaction, takes an extra reference, and declares a quota delta.
- `ufs_trans_push_quota()` logs the quota record or cleans up on quota transaction cancellation/error.
- `ufs_trans_dqrele()` wraps dquot release in a quota transaction.

## Hard-Lock Error Handling
- `ufs_trans_hlock()` scans `ufs_instances`, marks errored trans filesystems as `UT_HLOCKING`, then attempts `LOCKFS_HLOCK`.
- If a filesystem is already error-locked and the fix-failure queue has active entries, it wakes `ufs_fix`.
- After each attempt, it restores `vfs_validfs` to `UT_MOUNTED` and retries as needed for busy or conflicting lockfs state.

## Log Reservation Logic
- `ufs_log_amt()` estimates log bytes for writes/truncates from cylinder group metadata, inode size, indirect block deltas, and estimated cylinder group count.
- `ufs_trans_trunc_resv()` computes truncation reservation and chunk size when a truncate would exceed `ufs_trans_max_resv`.
- `ufs_trans_write_resv()` limits write reservations by `ufs_trans_max_resid`, prefaults user pages before opening a transaction, and reports chunking needs.

## Debug Metadata Map
- Under `DEBUG`, `ufs_trans_mata_mount()` records static metadata regions: superblock, cylinder groups, inode tables, and existing metadata in inodes.
- `ufs_trans_mata_iget()` classifies directory, shadow, attribute-directory, quota, and indirect blocks as metadata.
- Allocation/free helpers add or remove metadata map regions.

## Locking and Safety
- Uses `ufsvfs_mutex` for global instance traversal.
- Uses `vfs_dqrwlock` for inode/quota access around iget and dquot operations.
- Uses dquot locks to protect `DQ_TRANS`, modification flags, and reference counts.
- Uses `T_DONTBLOCK` to prevent nested blocking transaction behavior.
- Explicitly avoids transaction logging during panic for active logging filesystems.

## Research Notes
This file is the adapter between ordinary UFS metadata operations and the logging subsystem. Correctness depends on accurate reservation estimates, matching dquot reference/flag cleanup, and not opening transactions in contexts where lockfs or panic handling cannot tolerate blocking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_vfsops.c

## Overview
`ufs_vfsops.c` implements the UFS VFS module wrapper and filesystem lifecycle operations: mount, remount, root mount/unmount, unmount, root lookup, statvfs, sync, vget, syncfs, and VFS/vnode operation registration. It is the central integration point between UFS on-disk state, mount options, logging, lockfs, quotas, snapshots, background threads, and the illumos VFS framework.

## Main Responsibilities
- Register the UFS filesystem module and VFS operations.
- Parse and apply UFS mount options including logging, largefiles, direct I/O, xattrs, noatime/deferred atime, and onerror policy.
- Validate mount devices and UFS superblock magic/version/geometry.
- Mount ordinary filesystems and the root filesystem.
- Remount read-only root or mounted filesystems read-write.
- Initialize `ufsvfs`, root inode, lockfs state, summary info, logging state, and background workers.
- Unmount cleanly or forcibly with lockfs coordination.
- Report filesystem statistics and adjust for delayed delete accounting.
- Sync all UFS filesystems or a single mounted instance.
- Resolve file handles for NFS-style `VFS_VGET`.

## Mount and Remount Flow
- `ufs_mount()` checks mount privilege, validates the mount point, copies `ufs_args`, resolves the special vnode or lofi backing vnode, checks access, prevents duplicate device mounts, handles tape read-only policy, and delegates to `mountfs()`.
- `ufs_mountroot()` handles root init, root remount, and root unmount; root unmount flushes logs/summary info when possible and closes the root device.
- `mountfs()` opens the device for root init, invalidates block-device pages, reads and validates the superblock, allocates `ufsvfs`, links it into `ufs_instances`, initializes delete/reclaim queues, snarfes logging state, copies the superblock into a native-sized buffer, reads summary info, initializes lockfs, gets the root inode, computes geometry/cache tunables, starts delete/reclaim threads when needed, writes mount-time superblock state, and initializes fix-on-panic policy.
- `remountfs()` updates mount options, rejects read-only remount-to-readonly, quiesces the filesystem, rereads and validates the superblock, restarts log rolling, restores summary info, switches to read-write state, starts workers, and writes the superblock.

## Unmount Flow
- `ufs_unmount()` supports forced unmount by marking `VFS_UNMOUNTED`, suspending delete work, hard-locking/quiescing/flushing through lockfs, and then continuing cleanup.
- It rejects unmount if lockfs counts, falloc counts, or soft locks indicate active users.
- Normal unmount flushes pending operations; hard/error-locked unmount skips some inode-cache checks.
- It deletes snapshots during hard/error-locked forced unmounts, otherwise snapshots make unmount fail with `EBUSY`.
- It closes quotas, invalidates dquots, drains delete and idle queues, invalidates/removes all cached inodes, flushes shadow inode cache, exits worker threads, writes final clean/log state, commits outstanding transactions, releases logging state, updates fix-on-panic bookkeeping, frees summary info, closes device vnode, removes the instance, and either frees or defers freeing `ufsvfs`.
- On unmount failure, it reopens operations, resumes workers, marks the filesystem mounted again, triggers transaction error handling, and may force summary-info logging for `/usr`.

## Sync and Stat Operations
- `ufs_statvfs()` validates the superblock, reports block/file counts, adjusts free space for delayed delete queue entries on logging filesystems, computes available blocks after minfree, and fills base type, flags, and name length.
- `ufs_sync()` handles global sync via `ufs_update()` or single-filesystem sync: write modified superblock, scan inodes, flush buffers, and commit async transactions.
- `sbupdate()` writes summary information and the superblock for non-logging filesystems, or delegates to `ufs_sbwrite()` for logging filesystems.
- `ufs_syncfs()` maps syncfs to `ufs_fioffs()` and rejects nonzero flags.

## VGET and Root
- `ufs_root()` returns a held root vnode or `EIO` after forced unmount.
- `ufs_vget()` rejects unmounted filesystems, trims the idle queue before lockfs entry when needed, uses lockfs begin/end around `ufs_iget()`, and validates generation, mode, and link count before returning a vnode.
- Deleted, freed, stale, or generation-mismatched handles return `EINVAL`.

## Module Registration
- `_init()` creates thread-specific-data keys for lockfs and snapshot throttling, then installs the filesystem module.
- `_fini()` returns `EBUSY`, making the module effectively non-unloadable.
- `ufsinit()` registers VFS ops, vnode ops, stores the filesystem type, and initializes inode support.

## Locking and Safety
- Mount and unmount require VFS locks at key lifecycle boundaries.
- `ufsvfs_mutex` protects global instance list operations.
- `ufs_scan_lock` prevents races among inode scans, sync, and unmount.
- `ul_lock`, `ufs_quiesce_pend`, and lockfs state coordinate quiesce/freeze/thaw behavior.
- Forced-unmount handling can defer freeing `ufsvfs` to avoid sleepers in lockfs code dereferencing freed state.
- Mount failure cleanup removes partially cached root inodes and waits briefly for stray references before marking stale and leaking rather than freeing unsafely.

## Research Notes
This is the highest-level UFS integration file. Its main correctness risks are lifecycle races during failed mount and forced unmount, log replay/summary-info state transitions, worker-thread coordination, snapshot ownership during unmount, and consistency between mount options and superblock clean/log flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_vfsops.c -->