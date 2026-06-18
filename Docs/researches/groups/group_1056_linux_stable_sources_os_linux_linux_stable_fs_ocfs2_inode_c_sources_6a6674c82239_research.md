# Group Research: group_1056_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_inode_c_sources_6a6674c82239

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable` is included in subset A.

Read coverage: complete read of all listed files, 8,899 total source lines.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/inode.c

Purpose: implements OCFS2 inode cache lookup, on-disk dinode validation, VFS inode population/refresh, inode dirtying, eviction/delete/wipe paths, orphan-aware deletion, filecheck validation/repair reads, and inode-backed metadata-cache operations.

Read coverage: complete file read, 1,815 lines.

Key structures and state:
- `struct ocfs2_find_inode_args` carries block number, VFS inode number, iget flags, and system-file type into `iget5_locked()`.
- `OCFS2_I(inode)` state managed here includes `ip_blkno`, cluster-lock resources, `ip_clusters`, `ip_attr`, `ip_dyn_features`, orphan/recovery flags, metadata cache, extent map, local allocation reservation, and JBD2 inode fsync transaction ids.
- `OCFS2_FI_FLAG_*` controls special iget behavior for system files, orphan recovery, and filecheck check/fix paths.
- Inode lifecycle flags such as `OCFS2_INODE_SYSTEM_FILE`, `OCFS2_INODE_DELETED`, `OCFS2_INODE_MAYBE_ORPHANED`, `OCFS2_INODE_SKIP_ORPHAN_DIR`, and `OCFS2_INODE_DIO_ORPHAN_ENTRY` steer deletion and recovery.

Major logic:
- `ocfs2_iget()` validates input block numbers, uses `iget5_locked()` with OCFS2-specific find/init callbacks, reads new inodes from disk, rejects bad inodes, and initializes fsync/datasync transaction ids from the current JBD2 transaction state.
- `ocfs2_init_locked_inode()` sets `i_ino`, `ip_blkno`, and lockdep classes for system-file inodes and quota allocation semaphores.
- `ocfs2_populate_inode()` copies dinode mode, owner, size, timestamps, link count, cluster count, attributes, dynamic features, device id, file operations, inode operations, address-space operations, and OCFS2 lock resources into the VFS inode.
- `ocfs2_read_locked_inode()` optionally takes open/meta cluster locks for non-system inodes, chooses normal or filecheck read/repair validation, handles system-file generation compatibility, writes repaired dirty non-JBD buffers when needed, and marks failures as bad inodes.
- `ocfs2_mark_inode_dirty()` journals dinode access, writes mutable VFS inode state back to the dinode, dirties the metadata buffer, and records fsync transaction ids.
- `ocfs2_refresh_inode()` refreshes in-memory inode fields from a dinode under `ip_lock`.
- `ocfs2_validate_inode_block()` validates metadata ECC, link/mode sanity, dinode signature, block number, valid flag, filesystem generation, suballocator slot, inline-data bounds, chain-list layout, and refcount-root presence.
- Filecheck helpers translate validation failures into `OCFS2_FILECHECK_ERR_*` codes and can repair limited fields: `i_blkno`, filesystem generation, extent-list next-free count, and metadata ECC.
- Delete path starts in `ocfs2_evict_inode()`, then `ocfs2_delete_inode()` blocks signals, takes NFS sync and inode cluster locks, checks DIO orphan state, asks the cluster whether wiping is safe via open-lock trylock, truncates page cache, and calls `ocfs2_wipe_inode()`.
- `ocfs2_wipe_inode()` serializes with orphan recovery, locks the orphan directory when needed, truncates data, removes directory index trees, xattrs, refcount trees, and finally frees the dinode through the inode allocator.
- `ocfs2_clear_inode()` checkpoints outstanding metadata unless the inode was successfully deleted, drops locks and reservations, verifies no pending I/O markers/unwritten extents/cache entries remain, clears inode-private state, and releases the JBD2 inode.

Important entry points:
- Lookup/load: `ocfs2_ilookup()`, `ocfs2_iget()`, `ocfs2_read_inode_block()`, `ocfs2_read_inode_block_full()`.
- VFS state sync: `ocfs2_populate_inode()`, `ocfs2_refresh_inode()`, `ocfs2_mark_inode_dirty()`, `ocfs2_inode_revalidate()`.
- Lifecycle: `ocfs2_evict_inode()`, `ocfs2_sync_blockdev()`.
- Validation/cache: `ocfs2_validate_inode_block()`, `ocfs2_inode_caching_ops`.

Concurrency and lifetime:
- Cluster meta/open locks protect trusted dinode reads and deletion decisions; some system/recovery paths intentionally avoid locks to prevent mount-time and orphan-recovery deadlocks.
- `ip_lock` protects in-memory OCFS2 inode fields mirrored into dinodes.
- Delete uses NFS sync locks, inode cluster locks, orphan-dir locks, open-lock conversion, and orphan-recovery state bits to prevent two nodes from truncating or freeing the same inode.
- `ocfs2_clear_inode()` waits for checkpointing before dropping lock resources so remote nodes do not see uncheckpointed metadata as stable.
- Metadata cache callbacks lock with `ip_lock` and serialize I/O with `ip_io_mutex`.

Important dependencies:
- Uses OCFS2 DLM glue, journaling, extent map, file operations, directory/orphan helpers, xattr removal, refcount tree removal, suballocator dinode free, heartbeat/orphan recovery state, block ECC, and buffer-head I/O.
- Uses VFS inode lifecycle, quota APIs, page-cache truncation/writeback, and JBD2 inode tracking.

Risk and edge cases:
- Dinode validation distinguishes local ECC/block corruption from fatal filesystem metadata inconsistencies; callers must preserve that distinction.
- System-file iget flags must match on-disk `OCFS2_SYSTEM_FL`; mismatches are treated as code bugs.
- Orphan deletion has several intentional early exits: root inode, system files, downconvert thread context, active remote open locks, DIO orphan entries, and concurrent orphan recovery.
- Filecheck repair is deliberately narrow and refuses readonly, in-JBD, invalid-signature, and invalid-valid-flag cases.
- `ocfs2_wipe_inode()` must eventually signal orphan wipe completion after it increments orphan wipe counters or orphan recovery can wait indefinitely.
- Dirty buffer repair in read path may upgrade to an exclusive lock before writing a non-JBD dirty dinode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/inode.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/inode.h

Purpose: defines OCFS2's inode-private structure, inode-private flags, inode access macros, inode lifecycle/read/validate prototypes, metadata-cache conversion helpers, and small inline inode utilities.

Read coverage: complete file read, 173 lines.

Key structures and constants:
- `struct ocfs2_inode_info` embeds `struct inode vfs_inode` and stores OCFS2 block identity, RW/meta/open lock resources, allocation and xattr semaphores, spin-protected open/I/O/cluster fields, dynamic features, inode attributes, unwritten extent list, orphan recovery link, metadata cache, extent map, JBD2 inode, directory lookup hints, local allocation reservation, fsync transaction ids, and quota pointers.
- `OCFS2_INODE_*` flags distinguish system, journal, bitmap, deleted, maybe-orphaned, direct-I/O-open, skip-orphan-dir, and DIO-orphan-entry states.
- `OCFS2_FI_FLAG_*` constants select special `ocfs2_iget()` behavior for system files, orphan recovery, and filecheck check/fix operations.

Declared behavior:
- Exposes `ocfs2_ilookup()`, `ocfs2_iget()`, `ocfs2_inode_revalidate()`, `ocfs2_populate_inode()`, `ocfs2_refresh_inode()`, `ocfs2_mark_inode_dirty()`, `ocfs2_evict_inode()`, and inode block read/validation helpers.
- Publishes `ocfs2_aops` and `ocfs2_inode_caching_ops`.
- `ocfs2_inode_sector_count()` converts in-memory cluster count into 512-byte sector count.
- `ocfs2_is_refcount_inode()` tests the reflink/refcount dynamic feature.

Concurrency and lifetime:
- Header documents lock ownership by field: `ip_alloc_sem` protects allocation changes, `ip_xattr_sem` protects xattr changes, `ip_lock` protects selected counters/flags, and `recovery_lock` protects `ip_next_orphan`.
- Inode metadata cache access goes through `INODE_CACHE()` and `cache_info_to_inode()`.

Important dependencies:
- Includes `extent_map.h` and relies on OCFS2 lock resources, allocation reservations, caching info, extent maps, JBD2 inode state, and Linux quota structures.

Risk and edge cases:
- Consumers must not treat all `ip_flags` as spinlock-free; several fields are explicitly protected by `ip_lock`.
- `ocfs2_inode_sector_count()` assumes the inode's superblock cluster size is at least sector-sized and uses `ip_clusters`, not `i_size`.
- `ocfs2_is_refcount_inode()` reflects the in-memory dynamic feature copy; callers need a refreshed/locked inode when correctness depends on current on-disk state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ioctl.c

Purpose: implements OCFS2 ioctl dispatch, file attribute get/set support, filesystem information aggregation (`OCFS2_IOC_INFO`), online resize/group-add ioctls, reflink ioctl dispatch, FITRIM dispatch, extent movement dispatch, and compat ioctl handling.

Read coverage: complete file read, 1,003 lines.

Key structures and state:
- `ocfs2_info_request` is the common userspace request header used by all `OCFS2_IOC_INFO` subrequests.
- Information payloads handled here include block size, cluster size, max slots, label, UUID, feature bits, journal size, free-inode stats, and free-fragmentation stats.
- `OCFS2_INFO_FL_NON_COHERENT` controls whether info scans use cluster locks/system inodes or raw block reads.

Major logic:
- `ocfs2_fileattr_get()` takes a shared inode lock, refreshes OCFS2 inode flags from VFS flags, and exposes visible flags through `fileattr_fill_flags()`.
- `ocfs2_fileattr_set()` rejects fsxattrs, takes an exclusive inode lock, masks unsupported/modifiable flags, rechecks immutable/append capability under lock, journals an inode update, updates ctime and on-disk attributes, and commits.
- Simple info handlers copy request structs from userspace, fill scalar superblock/journal fields, mark requests filled, and copy results back.
- Free-inode info scans each slot's inode allocator. Coherent mode locks allocator inodes; non-coherent mode resolves system inode names and reads blocks directly.
- Free-fragmentation info scans global bitmap chain records and group descriptors, builds a power-of-two free-chunk histogram, tracks min/max/average free extents, and counts fully free chunks at the requested chunk size.
- Info request validation checks magic, exact request struct size, and request code; unknown valid requests are copied back with `FILLED` cleared for forward compatibility.
- `ocfs2_info_handle()` processes an array of request pointers, with compat pointer-array handling in `ocfs2_get_request_ptr()`.
- `ocfs2_ioctl()` dispatches space reservation, group extend/add, reflink, info, FITRIM, and move-extents commands with capability checks and mount write guards where required.
- `ocfs2_compat_ioctl()` handles compat reflink pointers and compat info request arrays, then delegates compatible commands to the native ioctl path.

Important entry points:
- `ocfs2_fileattr_get()`, `ocfs2_fileattr_set()`.
- `ocfs2_ioctl()`, `ocfs2_compat_ioctl()`.
- Internal info path: `ocfs2_info_handle()`, `ocfs2_info_handle_request()`, `ocfs2_info_handle_freeinode()`, `ocfs2_info_handle_freefrag()`.

Concurrency and lifetime:
- Attribute mutation is serialized by OCFS2 inode locking and a JBD2 transaction.
- Coherent info scans lock system inodes before reading allocator state; non-coherent scans intentionally trade freshness for avoiding cluster coordination.
- FITRIM and resize/group-add operations use VFS mount write protection.
- Freefrag bitmap scans hold global bitmap locking only in coherent mode and release all inode/buffer references on exit.

Important dependencies:
- Depends on OCFS2 inode locks, journaling, resize, reflink/refcount tree, directory/system-file lookup, suballocator/group descriptor readers, buffer-head I/O, trim, and move-extents code.
- Uses Linux `fileattr`, compat ioctl, capability, block discard, and userspace copy helpers.

Risk and edge cases:
- `OCFS2_IOC_INFO` pointer arrays require careful compat conversion; each request pointer can fault independently.
- Error reporting for info subrequests is best effort: `o2info_set_request_error()` may update only request flags in userspace.
- Non-coherent freefrag scans must clamp invalid `bg_bits` because raw reads bypass group descriptor validation.
- Freefrag chunk size must be nonzero and a power of two, and must not exceed clusters per group.
- Group extend/add and FITRIM require capabilities; move-extents performs its own write/regular-file/immutable checks in `move_extents.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ioctl.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ioctl.h

Purpose: declares OCFS2 file attribute and ioctl entry points used by the VFS file/inode operation tables.

Read coverage: complete file read, 20 lines.

Declared APIs:
- `ocfs2_fileattr_get()` and `ocfs2_fileattr_set()` implement Linux fileattr operations for OCFS2 inode flags.
- `ocfs2_ioctl()` is the native ioctl dispatcher.
- `ocfs2_compat_ioctl()` is the compat dispatcher for 32-bit userspace on 64-bit kernels.

Important dependencies:
- Uses VFS `dentry`, `mnt_idmap`, `file_kattr`, and `file` types; implementation is in `ioctl.c`.

Risk and edge cases:
- The header intentionally exposes only the ioctl surface, leaving command-specific structures in OCFS2 UAPI/internal headers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/journal.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/journal.c

Purpose: implements OCFS2's wrapper around JBD2 journaling, transaction lifecycle, metadata checksum triggers, journal allocation/init/load/shutdown/wipe, commit checkpoint thread, node journal replay/recovery, local-alloc/truncate-log/quota recovery completion, offline replay slot tracking, orphan scanning, and hard-readonly journal checks.

Read coverage: complete file read, 2,479 lines.

Key structures and state:
- `struct ocfs2_replay_map` tracks offline slots needing mount-time replay completion, with states `REPLAY_UNNEEDED`, `REPLAY_NEEDED`, and `REPLAY_DONE`.
- `struct ocfs2_recovery_map` in `journal.h` tracks node numbers queued for recovery.
- `struct ocfs2_la_recovery_item` queues second-phase recovery work: local alloc copy, truncate-log copy, quota recovery object, slot, and orphan recovery mode.
- `trans_inc_lock` serializes journal transaction id increments and metadata-cache transaction markers.

Major logic:
- Recovery initialization sets up recovery mutex/state/thread pointer/waitqueue and allocates a recovery map sized by `max_slots`.
- Replay slot computation marks slots with no node mapping as offline; later, mount recovery queues orphan cleanup for these slots.
- `ocfs2_commit_cache()` blocks new transactions with `j_trans_barrier`, flushes/checkpoints JBD2, increments OCFS2 transaction id, resets outstanding transaction count, wakes downconvert/checkpoint waiters, and reports errors.
- `ocfs2_start_trans()` rejects hard-readonly mounts, starts VFS internal write accounting, takes the transaction barrier, starts a JBD2 handle, and increments outstanding transaction count on clustered mounts.
- `ocfs2_commit_trans()` stops the JBD2 handle and releases barrier/write accounting for non-nested handles.
- Transaction credit helpers extend or restart handles without dropping OCFS2 locks; `ocfs2_allocate_extend_trans()` follows an ext4-style optimistic extension pattern.
- Metadata trigger setup attaches ECC/checksum frozen triggers and abort triggers for dinodes, extent blocks, refcount blocks, group descriptors, directory blocks, xattr blocks, quota blocks, dx roots, and dx leaves.
- `__ocfs2_journal_access()` validates buffer state, fails unsafe write-I/O-error reuse, marks the metadata cache with current transaction id, serializes buffer I/O through cache callbacks, obtains JBD2 write/undo access, and installs ECC triggers.
- `ocfs2_journal_dirty()` wraps `jbd2_journal_dirty_metadata()` and aborts the handle/journal on dirtying failure.
- Journal allocation/init obtains the local journal system inode, locks it with recovery semantics, validates size, creates the JBD2 journal inode object, records dirty state, installs ordered-data callbacks, stores inode/buffer references, and sets mount parameters.
- Journal load calls `jbd2_journal_load()`, clears stored journal errors, optionally flushes after replay, marks the OCFS2 journal dirty, and starts the commit kthread for clustered mounts.
- Journal shutdown stops the commit thread, flushes local journals when needed, destroys JBD2, marks the journal clean only after successful destruction/flush, unlocks and releases the journal inode, and frees the OCFS2 journal object.
- Recovery thread waits for mount, takes the super lock, computes replay slots, queues local orphan cleanup, replays dirty journals of dead nodes, stamps local alloc/truncate-log clean copies, clears recovered slots, refreshes recovery generations, defers quota recovery until safe, queues second-phase cleanup, and exits on disable.
- Journal replay dirty-reads recovery generation first to detect recovery already completed by another node, locks the target journal inode, force-reads cached journal blocks from disk, loads/flushes JBD2, clears dirty flag, bumps recovery generation, writes the dinode, and destroys temporary JBD2 state.
- Dead-node marking reads all journal recovery generations and trylocks remote journal inodes to detect nodes that need recovery.
- Orphan scan periodically takes a cluster-wide orphan scan lock, uses an LVB sequence to avoid duplicate scans across nodes, and queues orphan recovery work for all slots.
- Orphan recovery locks an orphan dir, collects inode references under the dir lock, marks normal orphans as maybe orphaned so `iput()` drives deletion, and handles DIO orphan entries by truncating/removing them under RW and inode locks.
- `ocfs2_check_journals_nolocks()` raw-reads all journal dinodes to refresh recovery generations and returns `-EROFS` if any journal is dirty.

Important entry points:
- Transaction API: `ocfs2_start_trans()`, `ocfs2_commit_trans()`, `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, `ocfs2_allocate_extend_trans()`.
- Journal metadata API: `ocfs2_initialize_journal_triggers()`, `ocfs2_journal_access_*()`, `ocfs2_journal_dirty()`.
- Lifecycle: `ocfs2_journal_alloc()`, `ocfs2_journal_init()`, `ocfs2_journal_load()`, `ocfs2_journal_shutdown()`, `ocfs2_journal_wipe()`.
- Recovery/orphan: `ocfs2_recovery_init()`, `ocfs2_recovery_thread()`, `ocfs2_recovery_exit()`, `ocfs2_mark_dead_nodes()`, `ocfs2_complete_mount_recovery()`, `ocfs2_complete_quota_recovery()`, `ocfs2_orphan_scan_start()`, `ocfs2_orphan_scan_stop()`.

Concurrency and lifetime:
- `j_trans_barrier` prevents checkpoint/shutdown from racing active transactions and also protects cluster-lock transaction ids until commit.
- Recovery state changes are synchronized with `recovery_lock` and `recovery_event`; disable paths wait for running recovery and queued completion work.
- `osb_lock` protects recovery maps, replay maps, orphan wipe counters, and recovery-generation state updates in several paths.
- Second-phase recovery runs on `ocfs2_wq` outside the recovery thread because local alloc/truncate-log/orphan/quota cleanup can take normal cluster locks.
- Orphan recovery advertises per-slot recovery state so `delete_inode()` exits early rather than deadlocking under orphan-dir locks.
- Commit thread loops until shutdown is requested and outstanding transaction count reaches zero.

Important dependencies:
- Wraps JBD2 journal APIs, OCFS2 DLM locks, metadata cache operations, block ECC, journal system inodes, localalloc, truncate log, slot map, quota recovery, orphan directories, inode/file truncation, and workqueues/kthreads.
- Uses Linux buffer cache, page-cache writeback for ordered data, waitqueues, random jitter, and mount write accounting.

Risk and edge cases:
- `ocfs2_commit_cache()` must not drop the transaction barrier while shutdown expects exclusive control.
- Journal replay must force-read blocks because buffer/page cache can hold stale remote journal contents.
- Recovery generation checks avoid double recovery when another node recovered a slot first.
- Dirty journal state is cleared only after JBD2 recovery/flush and dinode write; marking clean too early risks losing metadata replay.
- Orphan scans intentionally include active slots to trigger deletion of inodes held open on nodes that missed unlink notifications.
- `ocfs2_journal_dirty()` aborts aggressively on metadata dirty failures because continuing after journal metadata failure can corrupt the filesystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/journal.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/journal.h

Purpose: defines OCFS2 journal state structures, transaction/checkpoint inline helpers, journal/recovery/orphan-scan APIs, journal access prototypes, transaction access constants, and journal credit calculations for metadata operations.

Read coverage: complete file read, 610 lines.

Key structures and constants:
- `enum ocfs2_journal_state` distinguishes free, loaded, and shutdown journals.
- `struct ocfs2_journal` stores the JBD2 journal pointer, journal inode, owning OCFS2 superblock, journal dinode buffer, outstanding transaction count, transaction barrier, checkpoint waitqueue, local-alloc cleanup list, recovery work item, and OCFS2 transaction id.
- `struct ocfs2_recovery_map` is a flexible array of node numbers pending recovery.
- `OCFS2_JOURNAL_ACCESS_CREATE`, `WRITE`, and `UNDO` identify access intent for JBD2.
- Credit constants and inline calculators cover inode updates, xattr updates, quota writes/syncs, group extend/add, suballocator alloc/free, truncate log, directory operations, mknod/link/unlink/rename, orphan add/remove, xattr block creation, dx index updates, refcount tree operations, extent extension, symlink writes, and block group allocation.

Major logic:
- `ocfs2_inc_trans_id()` increments journal transaction ids with wraparound avoidance so zero is never used.
- `ocfs2_set_ci_lock_trans()` records the current transaction id in a metadata cache object so lock downconversion can determine checkpoint safety.
- `ocfs2_ci_fully_checkpointed()` tests whether a metadata cache object's last transaction is older than the journal's checkpointed transaction id.
- `ocfs2_ci_is_new()` tracks metadata that has not yet reached disk and clears `ci_created_trans` after checkpoint.
- `ocfs2_checkpoint_inode()` wakes the commit thread and waits until an inode metadata cache is fully checkpointed on clustered mounts.
- Ordered-data helpers wrap JBD2 ranged inode write and ordered truncate for OCFS2's embedded `ip_jinode`.
- `ocfs2_update_inode_fsync_trans()` records the transaction id needed by fsync/fdatasync unless the handle is aborted.

Declared APIs:
- Journal lifecycle/recovery: `ocfs2_journal_alloc()`, `ocfs2_journal_init()`, `ocfs2_journal_load()`, `ocfs2_journal_shutdown()`, `ocfs2_journal_wipe()`, `ocfs2_check_journals_nolocks()`, `ocfs2_recovery_thread()`, `ocfs2_mark_dead_nodes()`, `ocfs2_complete_mount_recovery()`, `ocfs2_complete_quota_recovery()`.
- Orphan scan: `ocfs2_orphan_scan_init()`, `ocfs2_orphan_scan_start()`, `ocfs2_orphan_scan_stop()`.
- Transaction: `ocfs2_start_trans()`, `ocfs2_commit_trans()`, `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, `ocfs2_allocate_extend_trans()`.
- Journal access wrappers for dinodes, extent blocks, refcount blocks, group descriptors, xattr blocks, quota blocks, directory blocks, dx roots, dx leaves, and no-ECC buffers.

Concurrency and lifetime:
- Transaction id helpers use global `trans_inc_lock`.
- `ocfs2_checkpoint_inode()` waits on `journal->j_checkpointed` and is skipped on local mounts.
- Credit calculators are conservative; callers still need matching locks, allocator reservations, and journal access/dirty calls.

Important dependencies:
- Includes Linux JBD2 and VFS headers and depends on OCFS2 inode/cache accessors, superblock feature tests, extent metadata sizing, block/cluster conversion helpers, and quota feature state.

Risk and edge cases:
- Metadata lock downconversion relies on correct `ci_last_trans` and transaction id increments; missing journal access markers can release locks before checkpoint.
- Credit math is intentionally maximum-oriented; under-reserving credits in callers can force transaction restarts in lock-sensitive code.
- `ocfs2_calc_extend_credits()` assumes the passed extent list is the root extent list.
- `ocfs2_update_inode_fsync_trans()` dereferences the active transaction; callers must pass a valid, non-stopped handle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/localalloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/localalloc.c

Purpose: implements OCFS2 node-local allocation windows for data clusters, including default sizing, enable/throttle state, mount/shutdown loading, recovery handoff, reservation/claim/free operations, syncing unused local bits back to the global bitmap, and sliding the local window.

Read coverage: complete file read, 1,318 lines.

Key structures and state:
- `OCFS2_LOCAL_ALLOC(dinode)` accesses the local alloc bitmap payload in a local alloc dinode.
- `osb->local_alloc_bits`, `local_alloc_default_bits`, `local_alloc_state`, `local_alloc_bh`, `osb_la_resmap`, and `la_last_gd` are the main per-node local allocation state.
- Local allocation states include unused, disabled, throttled, and enabled states; this file tests enabled/throttled via `ocfs2_la_state_enabled()`.
- `enum ocfs2_la_event` classifies slide, fragmentation, and ENOSPC events for window resizing.

Major logic:
- `ocfs2_la_default_mb()` picks a default local alloc size based on group descriptor capacity, cluster/block size limits, max default cap, distribution across slots, and local alloc bitmap capacity.
- `ocfs2_la_set_sizes()` applies user-requested or default local alloc sizes, clamping to bitmap capacity.
- `ocfs2_local_alloc_seen_free_bits()` and `ocfs2_la_enable_worker()` re-enable local allocation after enough free space is observed or after throttle timeout.
- `ocfs2_alloc_should_use_local()` checks local alloc state and rejects requests larger than half the current local window.
- `ocfs2_load_local_alloc()` reads the local alloc system inode for the local slot, validates flags and bitmap size, verifies it was recovered cleanly, stores the buffer head in `osb`, and enables local allocation.
- `ocfs2_shutdown_local_alloc()` disables local alloc, locks the global bitmap, journals clearing the local alloc dinode, releases the local alloc buffer, and syncs unused bits back to the main bitmap.
- `ocfs2_begin_local_alloc_recovery()` copies another slot's local alloc dinode, clears it on disk, recomputes ECC, and returns the copy for later cleanup after journal recovery.
- `ocfs2_complete_local_alloc_recovery()` locks the global bitmap and releases unused copied local alloc bits back to the main bitmap in a synchronous transaction.
- `ocfs2_reserve_local_alloc_bits()` locks the local alloc inode, rechecks state under `osb_lock`, slides the window if insufficient free bits exist, and fills an allocation context that owns inode and buffer references.
- `ocfs2_claim_local_alloc_bits()` finds/reserves clear bits, journals the local alloc dinode, marks bits used in the local bitmap, updates reservation map and used count, and returns global cluster offsets.
- `ocfs2_free_local_alloc_bits()` journals the local alloc dinode, clears bits in the local bitmap, and decrements used count for rollback paths.
- `ocfs2_sync_local_to_main()` walks zero bits in a local alloc copy and releases those unused cluster ranges to the global bitmap.
- `ocfs2_recalc_la_window()` shrinks/throttles/disables local alloc after ENOSPC or fragmentation and restores default sizing on normal slides when not throttled.
- `ocfs2_local_alloc_reserve_for_window()` reserves a new contiguous cluster window from the global bitmap, retrying with smaller windows after ENOSPC.
- `ocfs2_local_alloc_new_window()` claims clusters from the global bitmap, initializes local alloc offset/total/used fields, clears the local bitmap, and restarts the reservation map.
- `ocfs2_local_alloc_slide_window()` reserves a new window, clears and syncs the old local alloc copy, installs the new window, and records allocation statistics.

Important entry points:
- Lifecycle: `ocfs2_load_local_alloc()`, `ocfs2_shutdown_local_alloc()`, `ocfs2_la_set_sizes()`, `ocfs2_la_default_mb()`.
- Recovery: `ocfs2_begin_local_alloc_recovery()`, `ocfs2_complete_local_alloc_recovery()`.
- Allocation API: `ocfs2_alloc_should_use_local()`, `ocfs2_reserve_local_alloc_bits()`, `ocfs2_claim_local_alloc_bits()`, `ocfs2_free_local_alloc_bits()`.
- State feedback: `ocfs2_local_alloc_seen_free_bits()`, `ocfs2_la_enable_worker()`.

Concurrency and lifetime:
- Local alloc inode `i_rwsem` serializes window use/slide/disable with local allocation users.
- `osb_lock` protects state and current bit-window sizing.
- Global bitmap inode is locked while syncing old local windows or reserving/claiming new windows.
- Recovery is split: clear the recovered slot's local alloc before dropping journal recovery, then free copied unused bits later when normal cluster locks are safe.
- Allocation contexts returned from reserve hold inode and buffer references and must be freed by the caller.

Important dependencies:
- Uses OCFS2 system-file lookup, inode block reads, journaling, global bitmap/suballocator reservation and release, allocation reservation maps, block ECC, tracepoints, workqueues, and buffer-head I/O.

Risk and edge cases:
- Mount refuses local allocs that contain used bits, totals, or offsets because clean journal replay should have recovered them first.
- Shutdown clears the local alloc before syncing to the main bitmap to avoid double frees after later failures.
- Window throttling can reduce local alloc to disabled state; callers must recheck state after slide attempts.
- Reservation-map mode expects local allocation to go through reservations; the old bitmap scan path asserts reservations are disabled.
- `ocfs2_sync_local_to_main()` only frees zero bits from the local copy; used bits remain allocated to files and must not be released.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/localalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/localalloc.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/localalloc.h

Purpose: declares the OCFS2 local allocation lifecycle, recovery, sizing, allocation, free, and enable-worker APIs.

Read coverage: complete file read, 52 lines.

Declared APIs:
- Lifecycle/sizing: `ocfs2_load_local_alloc()`, `ocfs2_shutdown_local_alloc()`, `ocfs2_la_set_sizes()`, `ocfs2_la_default_mb()`.
- Recovery: `ocfs2_begin_local_alloc_recovery()`, `ocfs2_complete_local_alloc_recovery()`.
- Allocation decision and operations: `ocfs2_alloc_should_use_local()`, `ocfs2_reserve_local_alloc_bits()`, `ocfs2_claim_local_alloc_bits()`, `ocfs2_free_local_alloc_bits()`.
- Feedback/worker: `ocfs2_local_alloc_seen_free_bits()`, `ocfs2_la_enable_worker()`.

Important dependencies:
- Uses `struct ocfs2_super`, `struct ocfs2_dinode`, `struct ocfs2_alloc_context`, JBD2 `handle_t`, and workqueue types.

Concurrency and lifetime:
- Header exposes allocation-context based ownership: reserve fills an `ocfs2_alloc_context`, claim/free consume it under a transaction.
- Recovery APIs transfer ownership of an allocated dinode copy to the caller/completion path.

Risk and edge cases:
- Callers must not use local allocation merely because it is compiled in; `ocfs2_alloc_should_use_local()` enforces state and size policy.
- Claim/free require a matching local allocation context and active journal handle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/localalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/locks.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/locks.c

Purpose: implements OCFS2 userspace file locking hooks for BSD flock and POSIX locks, bridging Linux VFS locks to OCFS2 cluster file locks and plocks.

Read coverage: complete file read, 125 lines.

Major logic:
- `ocfs2_do_flock()` maps exclusive flock requests to OCFS2 file-lock level 1 and shared requests to level 0, converts nonblocking commands into trylock mode, serializes on `fp_mutex`, handles existing OCFS2 flock lock conversion by unlocking first, takes the cluster file lock, and then applies the VFS flock.
- If VFS flock setup fails after cluster locking, it releases the OCFS2 file lock.
- `ocfs2_do_funlock()` serializes unlock, drops the OCFS2 file lock, then applies the VFS unlock.
- `ocfs2_flock()` rejects non-flock requests, uses local VFS-only locks when mounted with local flocks or local mode, otherwise dispatches lock/unlock through OCFS2 cluster flock handling.
- `ocfs2_lock()` rejects non-POSIX locks and forwards POSIX locks to the cluster plock layer using the inode block number as resource identity.

Important entry points:
- `ocfs2_flock()`.
- `ocfs2_lock()`.

Concurrency and lifetime:
- Flock operations serialize per open file through `struct ocfs2_file_private::fp_mutex`.
- Cluster locks and VFS locks are coordinated so local VFS state is not installed unless the OCFS2 cluster lock succeeds.
- POSIX locks use the cluster connection plock service rather than the flock lock resource.

Important dependencies:
- Uses OCFS2 file lock helpers (`ocfs2_file_lock()`, `ocfs2_file_unlock()`), DLM/plock glue, file-private state, inode private block numbers, and Linux filelock APIs.

Risk and edge cases:
- Flock conversion is not atomic; the code intentionally unlocks the old level before locking the new level.
- Nonblocking flock maps `-EAGAIN` to `-EWOULDBLOCK`.
- Local flock mount option bypasses cluster flocking, which is correct only when users accept local-only lock semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/locks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/locks.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/locks.h

Purpose: declares OCFS2 file locking entry points for VFS file operations.

Read coverage: complete file read, 16 lines.

Declared APIs:
- `ocfs2_flock()` handles BSD flock-style locking.
- `ocfs2_lock()` handles POSIX byte-range locking.

Important dependencies:
- Uses Linux `struct file` and `struct file_lock`; implementation is in `locks.c`.

Risk and edge cases:
- The two APIs have different cluster backends in the implementation: flock uses OCFS2 file locks, while POSIX locks use plocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/locks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/mmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/mmap.c

Purpose: implements OCFS2 mmap fault and page-mkwrite handling, including signal masking around clustered faults, allocation for writable mapped pages, and VMA operation installation.

Read coverage: complete file read, 177 lines.

Major logic:
- `ocfs2_fault()` blocks signals around `filemap_fault()` so cluster lock paths do not abort with restart errors, then traces the fault.
- `__ocfs2_page_mkwrite()` validates that the folio still belongs to the inode mapping, is uptodate, and lies within current `i_size`; otherwise it returns `VM_FAULT_NOPAGE` for VM retry.
- For valid writable faults, it computes full-page or EOF-trimmed length and calls `ocfs2_write_begin_nolock()` / `ocfs2_write_end_nolock()` to allocate and prepare the whole page for mmap writeback.
- `ocfs2_page_mkwrite()` wraps the helper in `sb_start_pagefault()`, signal blocking, exclusive inode cluster lock, and exclusive `ip_alloc_sem`, ensuring remote truncation and local extent mutation cannot race the page becoming writable.
- `ocfs2_mmap_prepare()` refreshes atime under OCFS2 inode locking, installs `ocfs2_file_vm_ops`, and returns success.

Important entry points:
- `ocfs2_mmap_prepare()` is the VFS mmap preparation hook.
- Internal VM operations: `ocfs2_fault()`, `ocfs2_page_mkwrite()`.

Concurrency and lifetime:
- Page-mkwrite takes the inode cluster lock in exclusive mode and `ip_alloc_sem` write side before allocation.
- Signals are blocked in fault paths to avoid `-ERESTARTSYS` escaping cluster lock/message operations.
- The folio is revalidated before allocation because page cache truncation or remote lock downconversion can detach it.

Important dependencies:
- Uses OCFS2 write-begin/write-end no-lock helpers, inode locks, file operations, superblock pagefault accounting, Linux folio/page fault APIs, and tracepoints.

Risk and edge cases:
- The i_size check alone is insufficient because a remote truncate/reextend can reuse the index; the write path must recheck mapping under locks.
- `ocfs2_write_end_nolock()` is expected to return the full requested length; mismatch is treated as a bug.
- `ocfs2_mmap_prepare()` currently returns 0 even if atime locking failed after logging; it still installs VM ops.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/mmap.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/mmap.h

Purpose: declares the OCFS2 mmap preparation hook.

Read coverage: complete file read, 7 lines.

Declared APIs:
- `ocfs2_mmap_prepare(struct vm_area_desc *desc)` installs OCFS2 VM operations and performs mmap-time inode handling.

Important dependencies:
- Uses Linux `struct vm_area_desc`; implementation is in `mmap.c`.

Risk and edge cases:
- The header exposes only mmap setup; actual fault/page-mkwrite behavior is private to `mmap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/mmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/move_extents.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/move_extents.c

Purpose: implements the OCFS2 move-extents ioctl, supporting explicit physical-goal extent movement and automatic defragmentation by copying data to newly allocated clusters, updating extent records, handling refcounted extents, freeing old clusters, and reporting partial progress to userspace.

Read coverage: complete file read, 1,092 lines.

Key structures and state:
- `struct ocfs2_move_extents_context` carries inode/file, auto-defrag/partial flags, journal credits, latest new physical cluster, total moved clusters, refcount tree location, userspace range, dinode extent tree, metadata/data allocation contexts, and delayed deallocation context.
- Userspace `struct ocfs2_move_extents` supplies byte range, goal block, threshold, flags, and receives moved length/new offset/completion flag.

Major logic:
- `__ocfs2_move_extent()` copies data page-by-page from old clusters to new clusters, finds the target extent record, verifies flags, replaces/splits the extent record with the new physical location and refcount flag cleared, then frees old storage via refcount decrement or truncate-log append.
- `ocfs2_lock_meta_allocator_move_extents()` checks free extent record capacity, reserves extra metadata blocks when tree growth/sparse splits may need them, and adds extent-extension credits.
- `ocfs2_defrag_extent()` handles auto-defrag allocation: prepares refcount changes, reserves metadata and data clusters, flushes truncate log before cluster reservation to avoid global bitmap deadlock, supports partial defrag if requested, moves the extent, syncs writeback for copied data, and rolls back newly allocated clusters on selected failures.
- `ocfs2_find_victim_alloc_group()` raw-walks a system allocator's chain records and group descriptors to find the group containing a requested block.
- `ocfs2_validate_and_adjust_move_goal()` cluster-aligns explicit goals, validates that the goal is in the global bitmap, skips group descriptor block zero within a group, and rejects moves that would cross the group.
- `ocfs2_probe_alloc_group()` searches a victim group bitmap from the goal bit for a contiguous free run, allowing a bounded hop threshold.
- `ocfs2_move_extent()` handles explicit-goal movement: prepares refcount changes, reserves metadata, locks truncate log and global bitmap, probes/marks the target group, updates global bitmap inode/group counts, moves the extent, and syncs writeback.
- `ocfs2_calc_extent_defrag_len()` accumulates small extents until a threshold, skips already-large extents, or trims an extent to complete a threshold-sized defrag cycle.
- `__ocfs2_move_extents_range()` converts byte ranges to cluster ranges, skips empty/inline files and holes, iterates extents via `ocfs2_get_clusters()`, dispatches auto-defrag or explicit move, invalidates extent cache after each changed range, accumulates moved length/new offset, schedules truncate-log flush, and drains delayed deallocations.
- `ocfs2_move_extents()` serializes the operation with inode mutex, RW cluster lock, exclusive inode lock, and `ip_alloc_sem`, then updates inode ctime in a final transaction.
- `ocfs2_ioctl_move_extents()` validates userspace pointer, mount write access, regular writable file, immutable/append flags, range bounds, threshold/defaults, flags, explicit goal validity, executes the move, and copies progress back even after partial failure.

Important entry points:
- `ocfs2_ioctl_move_extents()`.
- Internal movement: `ocfs2_move_extents()`, `__ocfs2_move_extents_range()`, `ocfs2_defrag_extent()`, `ocfs2_move_extent()`, `__ocfs2_move_extent()`.

Concurrency and lifetime:
- Top-level movement holds inode mutex, OCFS2 RW lock, exclusive inode lock, and write side of `ip_alloc_sem`.
- Refcounted extents lock the refcount tree while preparing and applying refcount deletion.
- Truncate log inode mutex is used around truncate-log flush and old-cluster freeing decisions.
- Explicit-goal movement locks the global bitmap inode while marking target clusters allocated.
- Metadata/data allocation contexts and delayed deallocation contexts are freed/drained on exit.

Important dependencies:
- Uses OCFS2 extent tree mutation, cluster copy/COW writeback helpers, local alloc rollback, truncate log, global bitmap/suballocator updates, refcount tree, metadata allocator, inode locks, mount write accounting, and userspace copy helpers.

Risk and edge cases:
- Movement intentionally clears `OCFS2_EXT_REFCOUNTED` on replacement records because copied data is private after move.
- Partial defrag can reduce requested length; non-partial defrag clears completion and may return `-ENOSPC` after reporting progress.
- Explicit movement validates a goal before locking but global bitmap state can change later, so final probing/allocation can still fail.
- Truncate-log flush must occur before cluster reservation in defrag to avoid deadlock on the global bitmap.
- Range conversion ignores clusters containing unaligned start/end bytes for simplicity; movement is cluster-granular.
- Userspace receives `me_moved_len` and `me_new_offset` even when the operation fails after partial progress.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/move_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/move_extents.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/move_extents.h

Purpose: declares the OCFS2 move-extents ioctl helper.

Read coverage: complete file read, 12 lines.

Declared APIs:
- `ocfs2_ioctl_move_extents(struct file *filp, void __user *argp)` validates and executes the move-extents ioctl for regular writable OCFS2 files.

Important dependencies:
- Uses Linux `struct file` and userspace pointer annotations; implementation is in `move_extents.c`.

Risk and edge cases:
- All validation and partial-progress copyback semantics live in the implementation; callers should invoke this only from ioctl dispatch with mount write protection expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/move_extents.h -->