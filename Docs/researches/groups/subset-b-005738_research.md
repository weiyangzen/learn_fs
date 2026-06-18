# subset-b-005738 OCFS2 inode, journal, allocation, ioctl, lock, mmap, and extent-move research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/inode.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/inode.c

## Purpose
`inode.c` implements the OCFS2 VFS inode lifecycle: translating on-disk `struct ocfs2_dinode` records into VFS inodes, validating and repairing dinode blocks, keeping inode metadata coherent with the journal, and coordinating clustered deletion through orphan directories and open locks. It is one of the main integration points between Linux inode operations and OCFS2 cluster locking, metadata caching, quotas, truncate logs, xattrs, refcount trees, and filecheck.

## Important APIs, types, and functions
- `struct ocfs2_find_inode_args` packages block number, VFS inode number, iget flags, and system file type for `iget5_locked()`.
- `ocfs2_ilookup()` and `ocfs2_iget()` are the public lookup/load entry points. `ocfs2_iget()` validates block zero, calls `iget5_locked()`, runs `ocfs2_read_locked_inode()` for new inodes, and seeds fsync transaction ids from JBD2.
- `ocfs2_populate_inode()` maps disk dinode fields into `struct inode` and `struct ocfs2_inode_info`, sets inode/file/address-space operations, system and bitmap flags, lock resources, and directory allocation reservation type.
- `ocfs2_read_locked_inode()` optionally takes OCFS2 open/meta locks, reads and validates the dinode, populates the inode, and writes out dirty non-JBD buffers after checksum repair paths.
- `ocfs2_evict_inode()`, `ocfs2_delete_inode()`, `ocfs2_wipe_inode()`, and `ocfs2_remove_inode()` implement clustered deletion and inode allocator release.
- `ocfs2_mark_inode_dirty()` and `ocfs2_refresh_inode()` synchronize mutable inode fields between VFS memory and disk dinodes.
- `ocfs2_validate_inode_block()`, `ocfs2_filecheck_validate_inode_block()`, and `ocfs2_filecheck_repair_inode_block()` validate signatures, generation, flags, slot bounds, inline data, chain-list geometry, refcount location, and metadata ECC.
- `ocfs2_inode_caching_ops` exposes owner, superblock, cache lock, and I/O lock callbacks for the OCFS2 metadata cache.

## Control flow
Inode acquisition starts in `ocfs2_iget()`, which fills `ocfs2_find_inode_args`, invokes `iget5_locked()` with `ocfs2_find_actor()` and `ocfs2_init_locked_inode()`, then calls `ocfs2_read_locked_inode()` while the inode is new. The read path decides whether cluster locking is safe: ordinary inodes can take open and metadata locks, while system files, orphan recovery loads, and local mounts avoid that path. It then reads the block through either the cached OCFS2 metadata path or synchronous raw block I/O, optionally using filecheck validation or repair, and calls `ocfs2_populate_inode()`.

Deletion is deliberately staged. `ocfs2_evict_inode()` writes the inode and either truncates pages or enters `ocfs2_delete_inode()` when link count is zero or the inode may be remotely orphaned. `ocfs2_delete_inode()` blocks signals, takes the NFS sync lock, takes the inode metadata lock, rejects DIO-orphaned entries, and asks `ocfs2_query_inode_wipe()` whether an exclusive open lock can be obtained cluster-wide. If so, `ocfs2_wipe_inode()` locks the owning orphan directory, truncates file data, removes directory indexes, xattrs, and refcount trees, then `ocfs2_remove_inode()` clears `OCFS2_VALID_FL`/`OCFS2_ORPHANED_FL`, timestamps deletion, drops quotas, and frees the dinode from the inode allocator.

Metadata update flow is the standard OCFS2 journal dance: call `ocfs2_journal_access_di()`, mutate the dinode fields, call `ocfs2_journal_dirty()`, and update inode fsync transaction ids. `ocfs2_clear_inode()` waits for checkpointing before destroying locks unless the inode was fully deleted.

## State and persistence behavior
Persistent state is primarily in dinode fields: block number, mode, link count, size, cluster count, timestamps, attributes, dynamic features, generation, slot ownership, orphan flags, deletion time, inline data, chain lists, and metadata ECC. In-memory state lives in `ocfs2_inode_info`: cluster locks, allocation/xattr semaphores, metadata cache, extent map, open count, orphan recovery link, direct-I/O markers, reservation state, and fsync transaction ids. The code treats cluster locks as the validity boundary for trusting cached inode contents. Deletes persist by journaling the dinode changes and inode allocator updates; checkpointing protects lock teardown from unflushed metadata.

## Dependencies and integration points
This file depends on OCFS2 DLM glue for metadata/open/rw locks, JBD2 through `journal.h`, metadata cache and buffer-head I/O, suballocator code, directory/orphan helpers, xattr removal, refcount-tree removal, truncate handling, quota accounting, filecheck error codes, and tracepoints. VFS integration happens through inode operation and file operation assignment in `ocfs2_populate_inode()` plus eviction/revalidation hooks.

## Risks and edge cases
- Clustered delete correctness relies on lock ordering among NFS sync, inode meta lock, orphan dir lock, and open lock. The code contains explicit deadlock avoidance for downconvert and orphan recovery contexts.
- Repair paths intentionally avoid repairing JBD-owned buffers and emergency/read-only states.
- Dinode validation differentiates local checksum failures from fatal structural errors; test expectations should reflect which failures abort the filesystem.
- `ocfs2_delete_inode()` blocks signals because `-ERESTARTSYS` during deletion could leave permanent orphan entries.
- Filecheck repair changes only a limited set of fields, such as `i_blkno`, generation, `l_next_free_rec`, and ECC; it does not blindly restore validity flags.

## Test signals
Useful tests include cold-cache `stat`/iget on normal and system files, filecheck check/fix injections for bad ECC, block number, generation, and extent-list counters, clustered unlink while another node holds an open lock, orphan recovery racing with local eviction, DIO orphan cleanup, quota-enabled delete, reflink/refcount delete, and eviction after uncheckpointed inode metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/inode.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/inode.h

## Purpose
`inode.h` declares OCFS2 private inode state and the public inode helpers used across the filesystem. It defines the core `struct ocfs2_inode_info` wrapper around VFS `struct inode`, flags that describe OCFS2-specific inode roles and lifecycle state, and prototypes for inode loading, validation, refresh, dirtying, and eviction.

## Important APIs, types, and functions
- `struct ocfs2_inode_info` embeds lock resources for rw/meta/open locks, allocation and xattr semaphores, metadata cache, extent map, JBD2 inode, reservation state, quota pointers, fsync transaction ids, and the embedded `vfs_inode`.
- `OCFS2_I()` converts VFS inode pointers to OCFS2 private inode state.
- `INODE_CACHE()` exposes the inode metadata cache.
- `OCFS2_INODE_SYSTEM_FILE`, `OCFS2_INODE_JOURNAL`, `OCFS2_INODE_BITMAP`, `OCFS2_INODE_DELETED`, `OCFS2_INODE_MAYBE_ORPHANED`, `OCFS2_INODE_OPEN_DIRECT`, `OCFS2_INODE_SKIP_ORPHAN_DIR`, and `OCFS2_INODE_DIO_ORPHAN_ENTRY` encode cluster and deletion state.
- `OCFS2_FI_FLAG_*` controls `ocfs2_iget()` behavior for system files, orphan recovery, and filecheck check/fix modes.
- Exported functions include `ocfs2_iget()`, `ocfs2_ilookup()`, `ocfs2_populate_inode()`, `ocfs2_mark_inode_dirty()`, `ocfs2_validate_inode_block()`, and inode-block read helpers.

## Control flow
Most callers use `ocfs2_iget()` to obtain an inode by disk block. The returned inode carries an initialized `ocfs2_inode_info` and can be passed to journal, locking, allocation, xattr, and extent-map helpers through the accessors in this header. Metadata I/O helpers use `INODE_CACHE()` so lower layers can retrieve owner block numbers and locking operations through `ocfs2_inode_caching_ops`.

## State and persistence behavior
The header separates persistent disk-backed fields from in-memory coordination state. `ip_blkno`, `ip_clusters`, `ip_dyn_features`, and `ip_attr` mirror dinode fields. Lock resources, semaphores, open counters, I/O markers, reservation data, and `ip_next_orphan` coordinate cluster-visible behavior but are rebuilt on iget. `i_sync_tid` and `i_datasync_tid` remember the journal transactions needed by fsync/fdatasync.

## Dependencies and integration points
The header depends on `extent_map.h` and forward declarations from the rest of OCFS2. It is included by most OCFS2 implementation files because `OCFS2_I()` and `INODE_CACHE()` are the common bridges from VFS objects to OCFS2 metadata, journal, DLM, and allocator state.

## Risks and edge cases
- The semantics of `OCFS2_INODE_MAYBE_ORPHANED`, `OCFS2_INODE_SKIP_ORPHAN_DIR`, and `OCFS2_INODE_DIO_ORPHAN_ENTRY` are subtle and directly affect whether eviction removes on-disk state.
- `ip_next_orphan` is protected by recovery-only assumptions rather than a general-purpose lock.
- Lock resource and semaphore ordering is not visible in the header but all users must follow the ordering established by inode, allocation, mmap, and recovery code.

## Test signals
Compile-time and runtime coverage should exercise flag transitions, `container_of()` access via `OCFS2_I()`, inode-cache operations, iget modes for system/orphan/filecheck cases, and fsync transaction id updates after metadata changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.c

## Purpose
`ioctl.c` implements OCFS2 user-visible ioctl handling and file attribute get/set support. It dispatches space reservation, online resize group operations, reflink, information queries, trim, and extent movement. It also implements the `OCFS2_IOC_INFO` multiplexed query API for filesystem geometry, labels, features, journal size, free inode counts, and free-fragmentation statistics.

## Important APIs, types, and functions
- `ocfs2_fileattr_get()` and `ocfs2_fileattr_set()` bridge VFS fileattr operations to OCFS2 inode attributes with cluster locking and journaling.
- `ocfs2_ioctl()` is the main unlocked ioctl dispatcher.
- `ocfs2_compat_ioctl()` handles 32-bit compat argument forms for reflink and info requests before delegating compatible commands.
- `ocfs2_info_handle()` validates an `ocfs2_info` request array and dispatches each `ocfs2_info_request`.
- `ocfs2_info_handle_*()` functions fill specific info structures: block size, cluster size, max slots, label, UUID, features, journal size, free inode stats, and free fragmentation stats.
- Free-inode and free-fragment helpers optionally use coherent cluster-locked reads or non-coherent raw block reads depending on `OCFS2_INFO_FL_NON_COHERENT`.

## Control flow
Attribute set first locks the inode exclusively, masks unsupported or immutable flags, repeats capability checks while the cluster lock is held, starts a small transaction, updates `ip_attr`, VFS inode flags, ctime, and marks the dinode dirty. The ioctl dispatcher copies small argument structures from userspace, checks capabilities and write access for mutating operations, calls the relevant OCFS2 subsystem, then drops write access.

`OCFS2_IOC_INFO` first copies the header, validates request count and pointer array, then copies each request header and dispatches by `ir_code` and `ir_size`. Known handlers set `OCFS2_INFO_FL_FILLED`; unknown requests clear the filled bit without failing the whole API. Free-inode scans iterate per-slot inode allocator system files. Free-fragment scans walk global bitmap chain records and group descriptors, building a histogram and aggregate chunk statistics.

## State and persistence behavior
Most info ioctls are read-only. Attribute set persists inode flags through `ocfs2_mark_inode_dirty()`. Resize group add/extend, reserve/unreserve space, reflink, trim, and move-extents delegate persistence to their subsystem implementations. Info handlers write result flags and data back to userspace; on per-request failures some handlers best-effort set `OCFS2_INFO_FL_ERROR` in the user request.

## Dependencies and integration points
This file integrates with VFS fileattr APIs, Linux ioctl/compat/capability helpers, OCFS2 inode locking and journaling, resize, reflink/refcount tree, file space management, sysfile lookup, suballocator and group descriptor readers, discard/trim, and `move_extents.c`.

## Risks and edge cases
- Non-coherent info scans intentionally read raw disk blocks without cluster locks; they include extra validation for group descriptor bitmap bounds but can return racing data.
- Request-array handling depends on userspace pointers stored as `u64`; compat paths must use `compat_ptr()` where appropriate.
- Mutating ioctls must hold `mnt_want_write_file()` and enforce capability checks. Missing one would allow write operations on read-only mounts or without privilege.
- Unknown info requests are non-fatal for forward/backward compatibility, which tests should not treat as a hard error.

## Test signals
Exercise normal and compat ioctl paths, `OCFS2_IOC_INFO` arrays with mixed known/unknown requests, coherent and non-coherent free-inode/free-frag queries, invalid magic/size/count/pointers, immutable/append fileattr changes with and without `CAP_LINUX_IMMUTABLE`, group resize privilege checks, FITRIM capability and discard support, and move-extents dispatch on invalid/non-regular files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.h

## Purpose
`ioctl.h` publishes the OCFS2 ioctl and file attribute entry points used by file operation tables and VFS inode operation setup.

## Important APIs, types, and functions
The header declares `ocfs2_fileattr_get()`, `ocfs2_fileattr_set()`, `ocfs2_ioctl()`, and `ocfs2_compat_ioctl()`. These prototypes expose the implementation in `ioctl.c` without exporting ioctl internals such as info request parsing.

## Control flow
Callers enter through VFS fileattr or ioctl hooks. `ocfs2_compat_ioctl()` is compiled only when the implementation side is under `CONFIG_COMPAT`, but the prototype is always visible to code that wires operation tables in matching build contexts.

## State and persistence behavior
The header has no state. Its declared functions may mutate persistent inode flags, filesystem geometry, extents, or allocation state depending on the ioctl command.

## Dependencies and integration points
It depends on kernel type declarations for `struct dentry`, `struct file_kattr`, `struct mnt_idmap`, and `struct file` supplied by including compilation units. It is an integration shim between OCFS2 VFS operation tables and the ioctl implementation.

## Risks and edge cases
Prototype drift between this header and `ioctl.c` would break VFS table wiring. Build coverage with and without compat support is important because the compat implementation is conditional.

## Test signals
Compile tests should cover ioctl table assignment, fileattr hooks, and compat builds. Runtime signals live in `ioctl.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/journal.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/journal.c

## Purpose
`journal.c` implements OCFS2 journaling, checkpointing, journal load/shutdown, transaction wrappers, metadata checksum triggers, node recovery, offline-slot replay, orphan scanning, quota recovery coordination, and the commit thread. It bridges OCFS2 cluster recovery semantics with the Linux JBD2 journal.

## Important APIs, types, and functions
- `ocfs2_journal_alloc()`, `ocfs2_journal_init()`, `ocfs2_journal_load()`, `ocfs2_journal_shutdown()`, and `ocfs2_journal_wipe()` manage a node journal lifecycle.
- `ocfs2_start_trans()`, `ocfs2_commit_trans()`, `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, and `ocfs2_allocate_extend_trans()` wrap JBD2 handles with OCFS2 barriers and superblock write accounting.
- `ocfs2_journal_access_*()` and `ocfs2_journal_dirty()` enforce metadata-cache locking and attach ECC triggers for dinodes, extent blocks, refcount blocks, group descriptors, directories, xattrs, quotas, and indexed directory blocks.
- `ocfs2_recovery_init()`, `ocfs2_recovery_thread()`, `__ocfs2_recovery_thread()`, `ocfs2_recover_node()`, and `ocfs2_complete_recovery()` coordinate node failure recovery.
- `ocfs2_compute_replay_slots()`, `ocfs2_queue_replay_slots()`, and `ocfs2_free_replay_slots()` track offline slots that need replay/cleanup.
- `ocfs2_orphan_scan_*()` periodically scans orphan directories to catch cluster-open inodes left behind by remote unlink races.

## Control flow
Mount allocates `struct ocfs2_journal`, opens the local journal system inode, initializes JBD2 with `jbd2_journal_init_inode()`, records whether the on-disk journal was dirty, loads/replays it, marks it dirty, and starts `ocfs2_commit_thread()` for clustered mounts. Transactions take `sb_start_intwrite()` and a read lock on `j_trans_barrier`, then start a JBD2 handle. Checkpointing takes the barrier in write mode, flushes JBD2, increments `j_trans_id`, clears `j_num_trans`, wakes the downconvert thread, and wakes waiters on `j_checkpointed`.

Recovery is driven by a recovery map of node numbers. `ocfs2_recovery_thread()` test-and-sets a dead node and starts one kernel thread. The thread waits for mount state, takes the super lock, computes offline replay slots, replays each dead node's journal, begins local alloc and truncate-log recovery, clears the slot, and queues completion work. Completion work runs outside the recovery thread to return local alloc bits, finish truncate logs and quotas, and recover orphans under ordinary cluster locks. Journal replay force-reads journal blocks, initializes a temporary JBD2 journal, loads and flushes it, clears the dirty flag, bumps the slot recovery generation, and writes the journal dinode.

## State and persistence behavior
Persistent journal state is stored in the journal dinode flags and recovery generation. Runtime state includes `j_state`, `j_journal`, `j_inode`, `j_bh`, `j_num_trans`, `j_trans_id`, `j_trans_barrier`, `j_checkpointed`, and queued recovery cleanup items. Recovery maps live in memory, while slot cleanup persists through journal dirty-bit clearing, slot-map clearing, local alloc cleanup, truncate-log recovery, quota updates, and orphan deletion. Metadata ECC is recomputed at JBD2 freeze time through triggers.

## Dependencies and integration points
The file depends heavily on JBD2, OCFS2 DLM and super locks, heartbeat/slot-map state, system file lookup, inode metadata cache, localalloc, truncate log, quota, directory/orphan helpers, refcount/file helpers, and buffer-head I/O. It also exports trigger setup used by superblock initialization and transaction APIs used by almost every mutating OCFS2 subsystem.

## Risks and edge cases
- Recovery is split into critical replay/slot-cleaning and later cleanup. Tests must distinguish a recovered slot from fully reclaimed local alloc/orphan/quota state.
- `ocfs2_replay_journal()` uses recovery generation numbers to avoid replaying a slot already recovered by another node.
- `j_trans_barrier` must not be dropped during transaction extension/restart because lock transaction ids depend on it.
- `ocfs2_journal_dirty()` aborts the handle and journal if metadata dirtying fails.
- Shutdown must stop the commit thread and flush outstanding transactions before destroying JBD2 and marking the journal clean.
- Orphan scan deliberately scans active slots to resolve cluster-open/unlinked inode cases.

## Test signals
Cover journal load with clean and dirty journals, replay generation races, dead-node detection by trylocking journals, commit thread wake/shutdown behavior, checkpoint waiters in inode clear, metadata ECC trigger recomputation, aborted journal handling, quota-enabled recovery disable transitions, orphan scan sequence-number behavior, and hard-readonly journal checks that return `-EROFS` when any journal is dirty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/journal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/journal.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/journal.h

## Purpose
`journal.h` defines OCFS2 journaling state, transaction APIs, recovery entry points, checkpoint helpers, journal access types, and credit calculation helpers. It is the central header for mutation accounting and JBD2 integration across OCFS2.

## Important APIs, types, and functions
- `enum ocfs2_journal_state` models free, loaded, and shutdown journal states.
- `struct ocfs2_journal` stores the JBD2 journal pointer, journal inode, journal dinode buffer, transaction counters, transaction barrier, checkpoint waitqueue, and recovery cleanup work.
- `struct ocfs2_recovery_map` records node numbers pending recovery.
- Inline helpers `ocfs2_inc_trans_id()`, `ocfs2_set_ci_lock_trans()`, `ocfs2_ci_fully_checkpointed()`, `ocfs2_ci_is_new()`, `ocfs2_inode_is_new()`, and `ocfs2_ci_set_new()` manage transaction ids on metadata caches.
- Prototypes cover journal lifecycle, recovery, transaction handling, journal access variants, dirtying, and orphan scan setup.
- Credit macros and inline calculators define worst-case metadata credits for inode updates, quotas, allocation, truncation, mkdir/link/unlink/rename, xattrs, directory indexes, refcount trees, extent extension, symlink creation, and block group allocation.
- `ocfs2_jbd2_inode_add_write()`, `ocfs2_begin_ordered_truncate()`, and `ocfs2_update_inode_fsync_trans()` wrap ordered-data and fsync tracking hooks.

## Control flow
Callers start a transaction with `ocfs2_start_trans()` using a credit count from this header, request access through the typed `ocfs2_journal_access_*()` helper matching the metadata block type, modify the buffer, mark it dirty, and commit. Metadata locks consult transaction ids maintained here to decide when it is safe to downconvert or release locks. Inode clear can call `ocfs2_checkpoint_inode()` to kick the commit thread and wait until the inode cache transaction is fully checkpointed.

## State and persistence behavior
The header defines in-memory journal state and transaction-id bookkeeping rather than disk layout, but the APIs declared here are responsible for persisting all metadata updates through JBD2. Credit macros indirectly protect persistent consistency by ensuring transactions reserve enough space before mutating related disk structures.

## Dependencies and integration points
It includes Linux `fs.h` and `jbd2.h` and relies on OCFS2 inode and metadata cache helpers from surrounding includes. It is used by inode, allocation, xattr, directory, refcount, quota, resize, mmap, and ioctl/move-extents code.

## Risks and edge cases
- Incorrect credit calculations can cause transaction extension/restart in paths that hold locks, increasing deadlock risk.
- `trans_inc_lock` serializes transaction id observations and updates; callers must not bypass helpers.
- `ocfs2_checkpoint_inode()` can wait longer than expected if new metadata is added after the single checkpoint kick, which is called out in comments.
- Typed journal access should be used whenever metadata ECC applies; generic access leaves checksum management to the caller.

## Test signals
Compile and runtime tests should exercise credit helpers on different block/cluster sizes, metadata ECC trigger coverage for each typed access function, transaction id wrap avoidance, checkpoint waits for dirty inode caches, ordered truncate/write tracking, and quota feature combinations in credit calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/journal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.c

## Purpose
`localalloc.c` implements per-node local allocation windows for OCFS2 data clusters. It lets a node reserve a contiguous window from the global bitmap, satisfy small allocations locally, slide or shrink that window under pressure, and recover unused bits from crashed nodes.

## Important APIs, types, and functions
- `ocfs2_la_default_mb()` and `ocfs2_la_set_sizes()` choose local alloc window size based on cluster group geometry, max slots, block size, and user mount options.
- `ocfs2_load_local_alloc()` validates the node-local alloc system inode and enables local allocation if it is clean.
- `ocfs2_shutdown_local_alloc()` returns unused local bits to the global bitmap and marks the local alloc unused.
- `ocfs2_begin_local_alloc_recovery()` clears a recovered slot's local alloc on disk and returns a copy for later cleanup.
- `ocfs2_complete_local_alloc_recovery()` returns unused copied bits to the global bitmap after recovery locks are safe.
- `ocfs2_alloc_should_use_local()`, `ocfs2_reserve_local_alloc_bits()`, `ocfs2_claim_local_alloc_bits()`, and `ocfs2_free_local_alloc_bits()` are allocator-facing operations.
- Internal helpers count bits, find clear ranges through reservations or bitmap scans, sync unused local ranges to the main bitmap, recalculate window size/state, reserve a new global window, initialize it, and slide windows.

## Control flow
At mount, OCFS2 computes a local alloc size, reads the slot's local alloc inode, validates flags and bitmap size, verifies no stale used bits remain, stores the buffer head in `osb->local_alloc_bh`, and sets `OCFS2_LA_ENABLED`. Allocation callers first use a lockless-ish state check in `ocfs2_alloc_should_use_local()`, then `ocfs2_reserve_local_alloc_bits()` locks the local alloc inode, rechecks state, slides the window if needed, and returns an allocation context pinned to the local alloc buffer. Claim/free operations journal the local alloc dinode and update the local bitmap and used count.

Window sliding clears the current local alloc before returning unused bits to the main bitmap, so failures cannot double-free later. It reserves a new range from the global bitmap, starts a window-move transaction, syncs unused old bits back, then initializes the new local bitmap and reservation map. Recovery uses the same invariant in two phases: first clear the crashed local alloc while replay context is still active, then later free copied unused bits to the global bitmap under normal bitmap locks.

## State and persistence behavior
Persistent state is in the slot-local alloc dinode: bitmap totals, used count, local bitmap offset, and bitmap bytes. Runtime state is in `ocfs2_super`: `local_alloc_bh`, `local_alloc_state`, `local_alloc_bits`, `local_alloc_default_bits`, `la_last_gd`, `la_enable_wq`, and the local reservation map. Unused bits are persisted back to the global bitmap through `ocfs2_release_clusters()`. Fragmentation or ENOSPC can shrink or disable the local alloc and schedule delayed re-enable.

## Dependencies and integration points
The file integrates with system file lookup, inode locks, journal transactions and dinode access, global bitmap suballocation, reservation maps, truncate-log interactions through allocator behavior, workqueues for re-enable, and journal recovery via `journal.c`.

## Risks and edge cases
- Local alloc load rejects any non-empty local alloc because a clean journal with unrecovered local alloc would indicate fsck-worthy inconsistency.
- Window size calculations must not starve other nodes or exceed bitmap storage capacity.
- Sliding and shutdown must clear local alloc before freeing old bits to avoid double free after partial failure.
- Fragmented global bitmaps can throttle or disable local allocation and later re-enable it asynchronously.
- Allocation context ownership is unusual: successful reserve keeps the local alloc inode locked until the allocation context is released by higher-level allocator code.

## Test signals
Test default sizing across block/cluster sizes and slot counts, mount with stale local alloc bits, allocation using reservations and reservation-disabled fallback scanning, window slide under insufficient free bits, fragmentation-driven throttling/disable/re-enable, shutdown sync to main bitmap, crashed-node recovery two-phase cleanup, and local alloc free rollback from move-extents partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.h

## Purpose
`localalloc.h` declares the per-node local allocation API used by mount, recovery, and allocation paths.

## Important APIs, types, and functions
The header exposes load/shutdown, sizing, default-size calculation, recovery begin/complete, local-allocation eligibility, reservation/claim/free operations, free-bit observation, and delayed enable worker entry points. It forward declares `struct ocfs2_alloc_context` for allocator interactions.

## Control flow
Mount code sets sizes and loads the local alloc. Allocation code calls the eligibility check, reserves bits into an allocation context, then claims or frees bits inside a transaction. Recovery code calls begin recovery while handling a crashed slot and complete recovery later from journal completion work.

## State and persistence behavior
The header itself is stateless. Declared functions manipulate the local alloc dinode, global bitmap, OCFS2 superblock local alloc fields, reservation maps, and delayed enable work.

## Dependencies and integration points
It is used by allocator paths and `journal.c` recovery. It depends on OCFS2 superblock, dinode, allocation context, JBD2 `handle_t`, and workqueue types supplied by including files.

## Risks and edge cases
Callers must respect locking and lifetime rules: reserve returns an allocation context holding references/locks, claim/free require an active transaction, and recovery begin returns a copied dinode that completion must eventually free or consume.

## Test signals
Build coverage should ensure allocator and recovery users agree on prototypes. Runtime signals are covered by localalloc mount, allocation, shutdown, and recovery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/locks.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/locks.c

## Purpose
`locks.c` implements userspace file locking support for OCFS2. It maps BSD `flock()` operations onto OCFS2 file cluster locks plus VFS lock bookkeeping, and maps POSIX byte-range locks to the cluster stack's plock implementation.

## Important APIs, types, and functions
- `ocfs2_flock()` handles `FL_FLOCK` requests, using local VFS locks for local mounts or `localflocks`, and cluster-aware helpers otherwise.
- `ocfs2_lock()` handles `FL_POSIX` requests through `ocfs2_plock()`.
- `ocfs2_do_flock()` serializes per-file flock state with `fp_mutex`, converts existing cluster flock levels by unlocking first, obtains an OCFS2 file lock, then installs the VFS lock.
- `ocfs2_do_funlock()` releases the OCFS2 file lock and then updates VFS lock state.

## Control flow
For clustered flock, the code chooses PR/EX-like level from lock type and trylock behavior from `SETLK` versus `SETLKW`. If a lock resource is already attached at a different level, it first installs an unlock request in the VFS lock layer and releases the OCFS2 file lock because conversion is not guaranteed atomic. It then obtains the desired cluster file lock and calls `locks_lock_file_wait()`. If VFS locking fails, it releases the cluster lock.

## State and persistence behavior
There is no persistent disk state. Runtime state lives in `struct ocfs2_file_private`, especially `fp_flock` and `fp_mutex`, plus VFS file lock state and DLM/plock state in the cluster stack.

## Dependencies and integration points
The file depends on Linux file locking APIs, OCFS2 file-private state, DLM glue, mount options, and cluster connection plock support. It is wired into OCFS2 file operations through the regular and no-plock operation tables selected at inode population time.

## Risks and edge cases
- Flock conversion is explicitly non-atomic; there is a window between unlock and relock.
- Nonblocking flock maps `-EAGAIN` to `-EWOULDBLOCK`.
- Local mounts and `OCFS2_MOUNT_LOCALFLOCKS` intentionally bypass cluster locks.
- `ocfs2_lock()` requires `FL_POSIX`; passing other lock types returns `-ENOLCK`.

## Test signals
Exercise flock shared/exclusive/unlock, blocking and nonblocking contention across nodes, conversion from shared to exclusive, localflocks/local mount bypass, POSIX byte-range lock propagation through plocks, and VFS failure rollback of cluster flock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/locks.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/locks.h

## Purpose
`locks.h` declares OCFS2 VFS lock handlers for BSD flock and POSIX locks.

## Important APIs, types, and functions
It declares `ocfs2_flock(struct file *, int, struct file_lock *)` and `ocfs2_lock(struct file *, int, struct file_lock *)`.

## Control flow
The functions are called from OCFS2 file operation tables when userspace requests file locks. The implementation determines whether to use local VFS locks, OCFS2 file locks, or cluster plocks.

## State and persistence behavior
The header has no state. Declared functions affect runtime lock state only, not disk metadata.

## Dependencies and integration points
It integrates OCFS2 file operations with Linux `struct file_lock` and cluster lock management.

## Risks and edge cases
The main risk is mismatched prototypes or incorrect table wiring that bypasses cluster lock semantics. Runtime behavioral risk is in `locks.c`.

## Test signals
Build tests should cover operation table assignment. Runtime tests should cover flock/plock behavior in clustered and local mount modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/mmap.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/mmap.c

## Purpose
`mmap.c` implements OCFS2 memory-mapped file fault handling, especially write faults in a clustered filesystem where page allocation, inode size, and remote truncation must be serialized with cluster locks.

## Important APIs, types, and functions
- `ocfs2_mmap_prepare()` installs OCFS2 VM operations and updates atime under an inode lock.
- `ocfs2_fault()` wraps `filemap_fault()` with OCFS2 signal blocking to avoid interruption issues during cluster lock paths.
- `ocfs2_page_mkwrite()` handles write faults by taking pagefault write accounting, blocking signals, taking the inode metadata lock, and taking `ip_alloc_sem`.
- `__ocfs2_page_mkwrite()` validates folio mapping/uptodate/size, calls `ocfs2_write_begin_nolock()` with `OCFS2_WRITE_MMAP`, and completes with `ocfs2_write_end_nolock()`.
- `ocfs2_file_vm_ops` installs `.fault` and `.page_mkwrite`.

## Control flow
On mmap setup, OCFS2 takes an atime-aware inode lock and assigns VM ops. Read faults simply call the generic filemap fault under blocked signals. Write faults start pagefault accounting, block signals, lock the inode exclusively, take the allocation semaphore, and run the no-lock write-begin/end path to allocate and prepare the page range. If the folio no longer belongs to the mapping, is not uptodate, or lies beyond current size, the function returns `VM_FAULT_NOPAGE` so the VM can retry.

## State and persistence behavior
Mmap write faults can allocate clusters and dirty file metadata through the write-begin/end implementation. The local file's page cache and disk extents become persistent through the normal OCFS2 write and journal paths. The code itself mainly coordinates runtime locks and fault return values.

## Dependencies and integration points
It integrates Linux VM fault operations, OCFS2 inode locks, allocation semaphore, write path helpers from `aops.h`, atime locking, superblock pagefault accounting, and OCFS2 tracepoints.

## Risks and edge cases
- Remote truncation and data-lock downconversion can detach or invalidate folios; the mapping and uptodate checks are required before allocation.
- Last-page writes adjust length to `i_size`, avoiding allocation beyond EOF.
- Signal blocking is used because cluster lock paths may otherwise return restart errors into VM fault handling.
- `ocfs2_mmap_prepare()` returns success even if the atime lock failed after logging, because it always sets VM ops and returns 0 in the current implementation.

## Test signals
Test mmap read/write faults, write faults racing with truncate from another node, writes to the last partial page, ENOSPC propagation through `vmf_error()`, local pagecache invalidation retry paths, atime update locking, and pagefault behavior under signal delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/mmap.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/mmap.h

## Purpose
`mmap.h` declares the OCFS2 mmap preparation hook.

## Important APIs, types, and functions
It exposes `ocfs2_mmap_prepare(struct vm_area_desc *desc)`, which installs OCFS2 VM operations for file mappings.

## Control flow
The file operation mmap path calls this helper with a `vm_area_desc`; implementation code assigns `.fault` and `.page_mkwrite` handlers.

## State and persistence behavior
The header has no state. The declared function affects VMA runtime operations and can trigger atime locking in its implementation.

## Dependencies and integration points
It integrates OCFS2 file operations with Linux VMA setup. Including files must provide `struct vm_area_desc`.

## Risks and edge cases
The main risk is build/API drift with the kernel mmap prepare signature. Runtime mmap risks live in `mmap.c`.

## Test signals
Build coverage should exercise mmap operation wiring. Runtime tests should verify VM operations are installed and mmap write faults use OCFS2 locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.c

## Purpose
`move_extents.c` implements `OCFS2_IOC_MOVE_EXT`, supporting manual extent relocation to a requested physical goal and automatic defragmentation. It copies file data to new clusters, rewrites extent records, handles refcounted extents, updates allocation bitmaps, and reports partial progress to userspace.

## Important APIs, types, and functions
- `struct ocfs2_move_extents_context` carries inode/file, mode flags, credits, new physical position, moved count, refcount location, userspace range, extent tree, metadata/data alloc contexts, and deferred deallocation context.
- `ocfs2_ioctl_move_extents()` validates the user request, write access, file type, immutable/append flags, thresholds, and movement flags before calling `ocfs2_move_extents()`.
- `ocfs2_move_extents()` takes inode mutex, OCFS2 rw lock, metadata lock, and allocation semaphore, then updates ctime after the range operation.
- `__ocfs2_move_extents_range()` walks logical clusters, skips holes, chooses defrag or move behavior, invalidates the extent cache after each moved range, and returns moved length/new offset.
- `ocfs2_defrag_extent()` allocates new clusters from normal allocator paths for auto defrag.
- `ocfs2_move_extent()` moves to a user-specified goal by probing the global bitmap group near the goal and setting bits directly.
- `__ocfs2_move_extent()` copies clusters, splits/replaces the extent record, clears refcounted flag on replacement, and frees/decrements the old extent through truncate log or refcount tree.

## Control flow
The ioctl path copies `struct ocfs2_move_extents`, clamps length to EOF, defaults threshold to 1 MiB, validates flags, and either enables auto defrag or validates the physical goal. The main move path excludes concurrent writes with `ocfs2_rw_lock()`, locks the inode metadata, and serializes extent tree changes with `ip_alloc_sem`.

For each allocated extent in the requested logical range, auto defrag accumulates extents until the threshold and calls `ocfs2_defrag_extent()`, which may allow partial cluster claims if requested. Manual movement converts the userspace goal to clusters, finds the containing global bitmap group, probes for a free run within `me_threshold`, copies data, updates the extent tree, updates global bitmap dinode/group counts, and advances the goal. Both paths schedule truncate-log flush and run deferred deallocations after the range walk.

## State and persistence behavior
Persistent changes include new data clusters, updated extent records, global bitmap/group descriptor updates, truncate-log entries or refcount decrements for old clusters, ctime updates, and inode fsync transaction ids. The userspace range is copied back with `me_moved_len`, `me_new_offset`, and `OCFS2_MOVE_EXT_FL_COMPLETE` when fully complete. Runtime extent cache is truncated at each moved logical cluster to avoid stale flags or physical mappings.

## Dependencies and integration points
This file integrates with ioctl dispatch, mount write accounting, OCFS2 rw/meta locks, allocation and localalloc, global bitmap system inode, extent tree/path splitting, refcount tree, copy-on-write page duplication/writeback, truncate log, deferred deallocation, inode journaling, and extent map invalidation.

## Risks and edge cases
- Manual movement's goal validation is best effort; the bitmap can change before actual move.
- Partial defrag can improve success rate but may increase fragmentation; userspace controls this through flags.
- Refcounted extents need refcount tree locking and extra credits before replacement removes `OCFS2_EXT_REFCOUNTED`.
- Truncate-log flushing must happen before reserving clusters in defrag to avoid deadlocks on the global bitmap.
- Error paths still copy progress back to userspace, so tests should verify partial results.
- The code comments note xattr extents are not handled.

## Test signals
Exercise manual move to valid/invalid goals, group-boundary validation, auto defrag with threshold behavior, partial defrag ENOSPC behavior, holes in the range, refcounted/reflinked extents, immutable/append/non-regular/no-write-fmode rejection, ctime update, extent-cache invalidation, truncate-log flush scheduling, and user copy-out after partial failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.h

## Purpose
`move_extents.h` declares the OCFS2 move-extents ioctl entry point.

## Important APIs, types, and functions
It exposes `ocfs2_ioctl_move_extents(struct file *filp, void __user *argp)`, the dispatcher target for `OCFS2_IOC_MOVE_EXT`.

## Control flow
`ioctl.c` calls this function when userspace requests extent movement. The implementation validates the request, performs movement or defrag, and copies the updated range back to userspace.

## State and persistence behavior
The header has no state. The declared function can persist extent tree, allocation bitmap, truncate-log/refcount, and inode timestamp changes.

## Dependencies and integration points
It integrates ioctl dispatch with the extent movement implementation and depends on kernel `struct file` and user pointer annotations.

## Risks and edge cases
The main header-level risk is prototype drift from ioctl dispatch. Behavioral risk is in `move_extents.c`, especially partial completion and refcounted extents.

## Test signals
Build coverage should verify `OCFS2_IOC_MOVE_EXT` dispatch links to this prototype. Runtime tests should exercise move-extents behavior through ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.h -->
