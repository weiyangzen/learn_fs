# Group Research: group_1000_linux_stable_sources_os_linux_linux_stable_fs_gfs2_file_c_sources_o_6485e0a29a62

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/linux/linux-stable/fs/gfs2` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/file.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/file.c

## Scope

This file implements GFS2 VFS file and directory file operations: seeking, directory iteration, file attributes, ioctls, mmap fault handling, open/release, fsync, direct and buffered read/write paths, fallocate/punch-hole dispatch, splice write hints, and optional DLM-backed POSIX/flock locking.

## Public And Internal APIs Covered

- VFS file ops exported as `gfs2_file_fops`, `gfs2_dir_fops`, `gfs2_file_fops_nolock`, and `gfs2_dir_fops_nolock`.
- File attribute API: `gfs2_fileattr_get()`, `gfs2_fileattr_set()`, `gfs2_set_inode_flags()`.
- File lifecycle: `gfs2_open_common()`, `gfs2_open()`, `gfs2_release()`.
- I/O entry points: `gfs2_file_read_iter()`, `gfs2_file_write_iter()`, direct helpers, buffered write helper, `gfs2_fsync()`.
- MM integration: `gfs2_mmap()`, `gfs2_fault()`, `gfs2_page_mkwrite()`.
- Space management front end: `gfs2_fallocate()` and `__gfs2_fallocate()`.
- DLM-only locking: `gfs2_lock()` for POSIX locks and `gfs2_flock()` for flock locks.

## Control Flow And Behavior

- `gfs2_llseek()` takes the inode glock for `SEEK_END`, delegates hole/data seeks to inode helpers, and avoids glock acquisition for seek modes that do not need size or block mapping.
- `gfs2_readdir()` acquires the directory inode glock shared and delegates to `gfs2_dir_read()`.
- File flags translate between VFS `FS_*` flags and on-disk `GFS2_DIF_*` bits. Changing `GFS2_DIF_JDATA` flushes and waits page cache, truncates cached pages, adjusts ordered-data inode state, updates the dinode in a transaction, and resets address-space operations.
- `gfs2_page_mkwrite()` takes the inode glock exclusive, checks EOF, updates times, marks the glock dirty, un-stuffs inline files when needed, reserves quota and rgrp space, starts a transaction, allocates backing blocks via iomap, and returns with the folio locked and dirty on success.
- Direct read/write run under deferred glock mode and disable/fence page faults to avoid fault recursion while holding cluster locks. On `-EFAULT`, they drop the glock, fault user pages in manually, and retry. Direct writes beyond EOF fall back to buffered I/O.
- Buffered writes take the inode glock exclusive, fault pages in before lock acquisition where possible, use iomap buffered write ops, and special-case writes to the rindex inode by also locking the statfs inode.
- `gfs2_file_write_iter()` serializes with `inode_lock()`, performs generic write checks and privilege stripping, then routes direct writes through direct plus buffered fallback or buffered writes with timestamp updates and write sync handling.
- Fallocate only supports punch hole and keep-size allocation. Journaled data files reject fallocate except for the rindex inode. Allocation is chunked by rgrp/quota limits and zeroes newly allocated blocks.
- DLM POSIX locking delegates to `dlm_posix_*` under the lockspace semaphore. DLM flock locking uses per-file `gfs2_file::f_fl_gh` holders on `gfs2_flock_glops` glocks and coordinates with VFS local lock state.

## State And Data Structures

- Uses `gfs2_inode` fields `i_gl`, `i_diskflags`, `i_sizehint`, `i_res`, and `i_flags` including `GIF_SW_PAGED`.
- Per-open `struct gfs2_file` stores a mutex and flock holder.
- Allocation paths use `gfs2_alloc_parms`, quota data, rgrp reservations, transaction block reservations, and glock dirty state.
- File operation tables differ by DLM lock support: DLM builds install `.lock` and `.flock`; nolock builds use `generic_setlease`.

## Dependencies

- VFS/MM/iomap APIs: file ops, inode locks, folios, page faults, iomap direct and buffered I/O, fsync, fiemap-related seek helpers via inode.c, and fileattr APIs.
- GFS2 subsystems: glocks, glops, bmap/iomap allocation, quota, rgrp, transactions, metadata I/O, log flushing, directory reading, and punch-hole implementation.

## Risks And Invariants

- Page faults must not recurse into GFS2 while glocks are held; the direct and buffered paths carefully disable or pre-fault user memory.
- Direct I/O semantics require buffered fallback pages to be synced and invalidated before reporting combined progress.
- JDATA flag transitions require cache flush/truncation and address-space-op switching; stale page-cache state would violate data mode semantics.
- Fallocate reservation math must match quota/rgrp/metadata reservation ownership.
- Flock holder lifetime is protected by `file->f_lock`, `f_fl_mutex`, and an extra glock reference to avoid sleeping under spinlock during final put.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/gfs2.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/gfs2.h

## Scope

This small umbrella header defines basic constants shared by the GFS2 implementation.

## APIs And Constants

- Defines boolean-like create controls: `NO_CREATE` and `CREATE`.
- Defines force controls: `NO_FORCE` and `FORCE`.
- Defines `GFS2_FAST_NAME_SIZE` as 8.

## Dependencies And Role

- Included by implementation files as a lightweight common header before deeper subsystem headers.
- `CREATE` / `NO_CREATE` are used by glock lookup/creation call sites, including `gfs2_glock_get()` callers.

## Risks And Invariants

- The values are intentionally simple integer constants, not typed enums exposed outside this subsystem.
- Changing `CREATE` / `NO_CREATE` values would affect call sites that pass them as `int create` flags.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/gfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glock.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/glock.c

## Scope

This file implements the GFS2 glock core: creation and lookup, holder queueing, local compatibility checks, DLM promote/demote state transitions, asynchronous completion, instantiate hooks, LRU/shrinker reclamation, iopen delete verification, withdrawal handling, unmount cleanup, and debugfs reporting.

## Public And Internal APIs Covered

- Lifetime: `gfs2_glock_get()`, `gfs2_glock_hold()`, `gfs2_glock_put()`, `gfs2_glock_put_async()`, `gfs2_glock_free()`, `gfs2_glock_free_later()`.
- Holder lifecycle: `__gfs2_holder_init()`, `gfs2_holder_reinit()`, `gfs2_holder_uninit()`.
- Acquire/release: `gfs2_glock_nq()`, `gfs2_glock_wait()`, `gfs2_glock_poll()`, `gfs2_glock_dq()`, `gfs2_glock_dq_wait()`, `gfs2_glock_dq_uninit()`, `gfs2_glock_nq_num()`, `gfs2_glock_nq_m()`, `gfs2_glock_dq_m()`.
- Completion/callback: `gfs2_glock_cb()`, `gfs2_glock_complete()`, `gfs2_glock_thaw()`.
- Object and delete tracking: `glock_set_object()`, `glock_clear_object()`, `gfs2_inode_remember_delete()`, `gfs2_inode_already_deleted()`, `gfs2_queue_try_to_evict()`, `gfs2_queue_verify_delete()`, `gfs2_cancel_delete_work()`, `gfs2_flush_delete_work()`.
- Global maintenance: `gfs2_withdraw_glocks()`, `gfs2_gl_hash_clear()`, `gfs2_glock_init()`, `gfs2_glock_exit()`.
- Debugfs: `gfs2_dump_glock()`, `gfs2_create_debugfs_file()`, `gfs2_delete_debugfs_file()`, `gfs2_register_debugfs()`, `gfs2_unregister_debugfs()`.

## Control Flow And Behavior

- Glocks are keyed by `lm_lockname` in a global rhashtable. Lookup uses RCU and a wait queue keyed by the same lockname so callers can wait while a dying glock is removed.
- New glocks are initialized with operation type, optional LVB, optional address_space, lockref, stats, holder list, delayed work, and iopen delete work.
- `may_grant()` encodes local compatibility: exclusive is incompatible except for node-scope exclusive sharing, shared only shares with shared, deferred only shares with deferred, and `LM_FLAG_ANY` can accept compatible non-unlocked current states.
- `gfs2_glock_nq()` queues a holder, rejects recursive acquisitions by the same pid except flock glocks, handles nonblocking fast path, and runs the queue. Synchronous callers wait for `HIF_WAIT` to clear, then instantiate if needed.
- `run_queue()` chooses between demotion and promotion. Demotion waits for holders to drain, sets `GLF_DEMOTE_IN_PROGRESS`, and calls `do_xmote()`. Promotion grants locally compatible holders or starts a DLM conversion to the first waiter’s state.
- `do_xmote()` invokes glops sync/invalidate hooks before DLM conversion. On withdrawal it discards cached state and avoids issuing new DLM operations. Async DLM conversions hold an extra glock reference until completion.
- `finish_xmote()` consumes DLM replies, updates state, handles canceled/try/error results, retries deadlock/unlock cases, invokes `go_xmote_bh`, promotes waiters, and clears `GLF_LOCK`.
- Remote callbacks call `request_demote()`, possibly delaying inode demotion by the adaptive hold time to reduce lock bouncing.
- Async multi-glock acquisition uses `GL_ASYNC`, waits with randomized/exponential timeout, and returns `-ESTALE` to tell callers to release and retry.
- LRU/shrinker paths demote and release unused glocks. Glocks with active locks, references, or log-flush state are preserved.
- Iopen delete work tries to evict local cached inodes on remote iopen contention, then verifies deleted inode generations by looking up unlinked dinodes and rescheduling on `-EAGAIN`.
- Unmount sets `SDF_SKIP_DLM_UNLOCK`, flushes workqueues, demotes/clears glocks, waits for disposal with warnings, unmounts the lock module, frees delayed-dead glocks, and dumps leftovers.
- Debugfs iterators expose glock state, per-glock stats, per-superblock per-cpu stats, and currently open file descriptors holding iopen/flock glocks.

## State And Data Structures

- Global state: `gl_hash_table`, glock wait table, global LRU list/count/lock, shrinker, debugfs root.
- Glock state: `gl_flags`, current/target/demote state, DLM reply, lockref, holders, glops, LVB, object pointer, AIL counters, delayed work, iopen delete fields, rhashtable node, and RCU head.
- Holder state: requested state, flags, owner pid, wait/holder bits, error, and caller return address for diagnostics.
- Superblock state used here: glock and delete workqueues, async wait queue, kill wait, lockstruct ops/recovery flags, dead glocks, and disposal counter.

## Dependencies

- DLM lock operations through `lm_lockops`.
- Glops callbacks from `glops.c` for sync, invalidate, instantiate, held, dump, and remote callback behavior.
- Inode lookup/eviction helpers in `inode.c` and VFS dcache pruning for iopen delete work.
- Linux rhashtable, lockref, RCU, workqueues, shrinker, debugfs, seq_file, pid namespaces, and file table helpers.

## Risks And Invariants

- `gl_lockref.lock` protects holder queues and state bits; many functions temporarily drop and reacquire it around sleeping or callback operations.
- `GLF_LOCK` and `GLF_DEMOTE_IN_PROGRESS` ordering is critical; the code asserts demote-in-progress only occurs while locked.
- Recursive lock detection prevents self-deadlock, but intentionally exempts flock glocks.
- Async DLM completion and workqueue reference accounting must balance exactly; queued work owns a glock reference.
- `go_sync()` / `go_inval()` are intentionally skipped or modified during withdrawal to avoid new shared-device writes.
- Iopen delete verification depends on generation tracking in the LVB to avoid confusing stale inode numbers with live recreated inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glock.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/glock.h

## Scope

This header declares glock lock types, lock states, lock flags, DLM output flags, lock-module operations, glock-as-address-space wrapper, public glock APIs, debugfs hooks, and small inline helpers.

## APIs And Constants

- Lock types: reserved, nondisk, inode, rgrp, meta, iopen, flock, plock, quota, journal.
- Lock states: unlocked, exclusive, deferred, shared, with comments documenting shared/deferred incompatibility.
- Request flags: try, try-one-callback, recover, any, node-scope, async, exact, skip, no-pid, no-cache, no-block.
- DLM output flags: state mask, try-again, deadlock, canceled, error.
- Hold-time tuning constants for adaptive inode glock caching.
- `struct lm_lockops` defines mount, recovery, unmount, withdraw, put-lock, lock, cancel, and mount-option parsing hooks.
- `gfs2_glock_is_locked_by_me()` scans holders for the current task.
- `gfs2_glock2aspace()` returns the embedded metadata address_space for glops with `GLOF_ASPACE`.
- Declares full glock lifecycle, acquire/release, async wait, callback, delete-work, hash clear, withdraw, thaw, debugfs, object binding, and delete-generation APIs.

## State And Data Structures

- `struct gfs2_glock_aspace` combines a glock and an address_space for inode/meta-style glocks.
- Holder initialization helpers use return addresses for later debug output.
- Inline holder helpers represent initialized and queued state by `gh_gl` and `gh_list`.

## Dependencies

- Includes `incore.h`, so it relies on core GFS2 in-memory structure definitions.
- Consumed across file, inode, rgrp, quota, super, recovery, and metadata paths that acquire cluster locks.

## Risks And Invariants

- Lock flag semantics are part of the glock state machine contract. Misusing `LM_FLAG_ANY`, `GL_EXACT`, or `GL_SKIP` changes correctness of inode instantiation and compatibility.
- `gfs2_glock_is_locked_by_me()` depends on holder owner pids and holder list ordering.
- `gfs2_glock_nq_init()` uninitializes the holder on enqueue failure; callers must not uninit it again unless it succeeded.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glops.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/glops.c

## Scope

This file defines glock operation callbacks for metadata, inode, resource-group, freeze, iopen, flock, nondisk, quota, and journal glocks. These callbacks plug lock-type-specific sync, invalidate, instantiate, held, dump, and remote-callback behavior into the generic glock state machine.

## Public And Internal APIs Covered

- Exported workqueue: `gfs2_freeze_wq`.
- AIL helpers: `gfs2_ail_flush()` and internal `__gfs2_ail_flush()` / `gfs2_ail_empty_gl()`.
- Metadata sync: `gfs2_inode_metasync()`.
- Object lookup helper: `gfs2_glock2rgrp()`.
- Operation tables: `gfs2_meta_glops`, `gfs2_inode_glops`, `gfs2_rgrp_glops`, `gfs2_freeze_glops`, `gfs2_iopen_glops`, `gfs2_flock_glops`, `gfs2_nondisk_glops`, `gfs2_quota_glops`, `gfs2_journal_glops`, and `gfs2_glops_list[]`.

## Control Flow And Behavior

- AIL flushing scans a glock’s AIL list, verifies buffers are not dirty/locked/pinned outside fsync mode, converts buffers to revokes, and flushes the log. Unexpected dirty/locked/pinned AIL buffers withdraw the filesystem.
- Resource-group sync flushes the log for the rgrp glock, writes/waits metadata pages covering the rgrp blocks, empties the glock AIL, and frees bitmap clones. Invalidation releases rgrp buffers and truncates metadata pages over the rgrp range.
- Inode sync first handles regular-file concerns: unmaps shared mappings marked by mmap write faults and waits for direct I/O. If dirty, it flushes the log, writes metadata and regular data mappings, waits, metasyncs, empties AIL, then clears dirty state.
- Inode invalidation asserts no AIL buffers remain, truncates metadata mapping when metadata invalidation is requested, marks instantiate-needed, drops ACL/security/dir hash caches, marks the rindex stale when invalidating it, and truncates regular-file page cache.
- Dinode refresh parses on-disk dinode fields into the in-core inode, validates inode number, type, height, directory depth, exhash consistency, stuffed size limits, and sets VFS inode flags/address-space ops.
- Inode instantiate reads the dinode if a `gl_object` inode exists and updates the iopen glock’s formal inode number.
- Inode held waits for direct I/O except deferred holders and resumes interrupted truncation when taking exclusive lock on an inode flagged `GFS2_DIF_TRUNC_IN_PROG`.
- Freeze callback reacts to remote freeze demotion requests by trying to pin the superblock active and queueing freeze work. Freeze xmote bottom-half invalidates the journal glock and reloads log pointers from the journal head.
- Iopen callback reacts to remote unlock requests by scheduling local inode eviction when the iopen glock is shared and has an inode object.

## State And Data Structures

- Uses `gl_object` as either `gfs2_inode` or `gfs2_rgrpd`, guarded by `gl_lockref.lock`.
- `GIF_GLOP_PENDING` serializes inode glop activity with waiters.
- AIL state is stored in `gl_ail_list`, `gl_ail_count`, `sd_ail_lock`, `sd_log_lock`, and revoke lists.
- Inode parsing fills `i_no_formal_ino`, `i_generation`, `i_diskflags`, `i_eattr`, `i_goal`, `i_height`, `i_depth`, `i_entries`, VFS timestamps, uid/gid, nlink, size, blocks, mode, and rdev.

## Dependencies

- Relies on glock core for state transitions, transactions/logging for AIL and flushes, rgrp code for rgrp instantiation/dump/free clones, metadata I/O for dinode buffers, directory/xattr/security cache helpers, recovery for journal head discovery, and VFS address-space writeback/invalidation.

## Risks And Invariants

- Demotion must not complete before dirty metadata/data and AIL entries are stable or revoked.
- Invalidation assumes AIL is empty; assertions withdraw on inconsistency.
- Dinode parsing is a trust boundary from disk to memory; all structural checks protect later metadata traversal.
- Freeze handling must avoid racing unmount; it uses `s_umount` trylock plus active superblock reference.
- Iopen callback must avoid scheduling delete work during filesystem kill.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glops.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/glops.h

## Scope

This header exports glock operation tables and the small set of glops helpers used outside `glops.c`.

## APIs

- Declares `gfs2_freeze_wq`.
- Declares operation tables for meta, inode, rgrp, freeze, iopen, flock, nondisk, quota, and journal glocks.
- Declares `gfs2_glops_list[]` for type-indexed lookup.
- Declares `gfs2_inode_metasync()` and `gfs2_ail_flush()`.

## Dependencies And Role

- Included by glock, file, inode, and other subsystem files that need specific glops instances for `gfs2_glock_get()` or need to flush inode metadata/AIL state.
- Depends on `incore.h` for glock and inode structure declarations.

## Risks And Invariants

- The exported operation tables are the binding between lock type numbers and behavior. Mismatching a glock type with the wrong table would corrupt lock-state semantics.
- `gfs2_ail_flush()` is used by fsync-style paths and must preserve the AIL/log ordering implemented in `glops.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/glops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/incore.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/incore.h

## Scope

This header defines the central in-memory structures and flags for GFS2: log operations, resource groups, buffers, lock names, glock operations/state, holders, quota data, reservations, inodes, transactions, journals, mount arguments, lock manager state, per-cpu lock stats, and the superblock-private `gfs2_sbd`.

## Key Structures

- `gfs2_log_header_host` and `gfs2_log_operations` describe journal headers and log element callbacks.
- `gfs2_bitmap` and `gfs2_rgrpd` represent resource-group bitmaps, clone bitmaps, allocation state, reservation tree, and rgrp glock linkage.
- `gfs2_bufdata` links buffer_heads to transactions and AIL lists.
- `lm_lockname` is the rhashtable key for glocks, consisting of block/lock number, superblock, and type.
- `gfs2_glock_operations` defines per-type sync, xmote bottom-half, invalidate, instantiate, held, dump, and remote callback hooks.
- `gfs2_holder` represents a queued or granted lock request.
- `gfs2_glock` stores all lock state, flags, holder queue, glops pointer, DLM LVB, object pointer, AIL counters, delayed work, iopen delete fields, and hash/RCU links.
- `gfs2_inode` embeds the VFS inode and adds dinode identity, glocks, quota data, rgrp reservation, allocation goal, size hint, ordered-data list, dir hash cache, disk flags, tree height, dir depth, entry count, and readahead.
- `gfs2_file` stores per-open flock state.
- `gfs2_quota_data`, `gfs2_qadata`, and quota constants represent quota locking/accounting state.
- `gfs2_trans` records transaction reservations, touched buffers, databuffers, revokes, and AIL lists.
- `gfs2_jdesc` tracks journal extents, recovery work, replay counts, and revoke replay state.
- `gfs2_args` and `gfs2_tune` hold mount options and tunables.
- `lm_lockstruct` tracks lockspace identity, DLM handles, recovery flags/generations, lockspace semaphores, and callback synchronization.
- `gfs2_sbd` is the filesystem-wide state object: VFS superblock, lock stats, flags, computed geometry, mount args, lock glocks, inode roots, statfs state, rgrp tree, journal index, workqueues, daemons, quota state, log/AIL state, freeze state, filesystem names, and debugfs directory.

## Important Flags And Inline Helpers

- `DIO_WAIT` and `DIO_METADATA` describe invalidate/sync behavior.
- `BH_Pinned` and `BH_Escaped` extend buffer state for journal handling.
- `DFL_*` flags describe DLM recovery state.
- `GLF_*` flags cover glock lock in progress, demotion, dirty state, frozen replies, LRU membership, instantiate state, iopen delete work, cancellation, and deferred delete.
- `GIF_*` flags cover inode quota lock, mmap shared-write page state, and pending glop.
- `SDF_*` flags cover journal, withdrawal, recovery, DLM unlock skipping, AIL flush, freeze, kill, eviction, and frozen state.
- Helpers include `GFS2_I()`, `GFS2_SB()`, `glock_sbd()`, `gfs2_aspace()`, lock-stat increments, `gfs2_max_stuffed_size()`, and glock number/type accessors.

## Dependencies

- This header is the shared state contract for nearly all GFS2 implementation files.
- It depends on Linux VFS, kobject, workqueue, DLM, buffer_head, RCU, rbtrees, percpu, lockref, rhashtable, mutex, and on-disk GFS2 structures.

## Risks And Invariants

- Structure fields are shared across many subsystems; locking discipline is external and must match comments and users.
- Clone bitmap comments define an allocation invariant: blocks freed in a transaction cannot be reallocated in that same transaction.
- `lm_lockname` must avoid interior padding because it is used as an rhashtable key.
- `gfs2_inode` embeds `struct inode` first, making `GFS2_I()` effectively a container cast relied on throughout the code.
- `gfs2_sbd` combines log, DLM, rgrp, quota, freeze, and debug state; partial initialization or teardown ordering mistakes can affect multiple subsystems.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/incore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/inode.c

## Scope

This file implements GFS2 inode lookup, setup, creation, linking, unlink/rmdir, symlink, mkdir/mknod, atomic open, rename/exchange, symlink following, permission checks, setattr/getattr, fiemap, seek-data/hole helpers, update-time handling, and inode operation tables.

## Public And Internal APIs Covered

- Exported helpers: `gfs2_setup_inode()`, `gfs2_inode_lookup()`, `gfs2_lookup_by_inum()`, `gfs2_lookup_meta()`, `gfs2_lookupi()`, `gfs2_dinode_dealloc()`, `gfs2_permission()`, `gfs2_seek_data()`, `gfs2_seek_hole()`.
- VFS operation tables: `gfs2_file_iops`, `gfs2_dir_iops`, and `gfs2_symlink_iops`.
- Creation helpers: `gfs2_create_inode()`, `alloc_dinode()`, `init_dinode()`, `gfs2_init_dir()`, `gfs2_init_xattr()`, `link_dinode()`.
- Namespace operations: `gfs2_create()`, `gfs2_lookup()`, `gfs2_link()`, `gfs2_unlink()`, `gfs2_symlink()`, `gfs2_mkdir()`, `gfs2_mknod()`, `gfs2_atomic_open()`, `gfs2_rename2()`.
- Attribute/data-map operations: `gfs2_setattr()`, `gfs2_getattr()`, `gfs2_fiemap()`, `gfs2_update_time()`.

## Control Flow And Behavior

- `gfs2_set_iop()` selects inode and file operation tables by inode mode and local-vs-DLM flock mode.
- `gfs2_setup_inode()` clears `__GFP_FS` from inode mapping allocations to avoid reclaim recursion into the filesystem.
- `gfs2_inode_lookup()` uses `iget5_locked()`, allocates inode and iopen glocks for new inodes, optionally verifies block type, checks deleted generations via the inode LVB, binds glock objects, instantiates disk state when type is unknown, takes an iopen shared holder, sets operation tables, and handles stale-generation failures.
- `gfs2_lookupi()` handles dot/root-dotdot special cases, avoids retaking a directory glock already held by the current task, checks execute permission unless root lookup, and delegates directory search.
- Create path obtains parent quota data, updates rindex, locks parent exclusive, validates permissions/link limits/name, handles existing files for atomic open, reserves directory-add space, allocates a VFS inode, applies ACL and suiddir/sgid uid/gid rules, inherits JDATA/SYSTEM/TOPDIR behavior, allocates dinode and optional xattr block, creates inode/iopen glocks, inserts the inode, initializes on-disk dinode, applies ACL/security xattrs, links the inode into the directory, instantiates dentry/file, and has a long cleanup path for partially created dinodes.
- Dinode deallocation checks the inode owns exactly one block, finds the rgrp, locks it node-scope exclusive, frees the dinode, releases final pages, and updates quota/statfs/rgrp transaction state.
- Hard link takes parent and child exclusive glocks, validates permissions, link counts, immutability/append-only state, reserves directory-add blocks, adds the directory entry, increments child nlink, and instantiates the dentry.
- Unlink/rmdir updates rindex, locks parent, child, and child rgrp, validates sticky-bit/append/immutable/permission and directory emptiness, removes the dirent, updates link count and ctime, and calls `gfs2_unlink_di()` when nlink reaches zero.
- Rename uses a global rename glock for cross-directory operations, rejects moving a directory into its own subtree, asynchronously acquires all participating inode glocks with retry on `-ESTALE`, optionally locks target rgrp for unlink flag updates, validates old and new entries, reserves new directory entry space, unlinks target if present, updates moved inode or dotdot, deletes old dirent, and adds new dirent.
- Exchange similarly locks participating directories/inodes, validates both entries, updates dotdot/ctime for both moved inodes, swaps directory entries, and adjusts parent nlinks when directories cross parents.
- `gfs2_rename2()` supports `RENAME_EXCHANGE`, treats `RENAME_NOREPLACE` as redundant, and rejects other flags.
- `gfs2_get_link()` reads stuffed symlink data from the dinode under a shared glock.
- `gfs2_permission()` can run from RCU mode; it returns `-ECHILD` when it would need to block. Otherwise it takes a shared/any glock unless already held and delegates to generic permission after immutable write rejection.
- `gfs2_setattr()` takes the inode glock exclusive, performs VFS setattr checks, routes size changes to truncate code, UID/GID changes through quota transfer, and mode/time/simple changes through transactions and ACL chmod.
- `gfs2_getattr()` takes a shared/any glock unless already held, maps append/immutable disk flags to STATX attributes, and calls `generic_fillattr()`.
- `gfs2_fiemap()` and seek-data/hole acquire shared inode glocks around iomap queries and pre-fault fiemap output buffers on `-EFAULT`.
- `gfs2_update_time()` upgrades an already-held non-exclusive glock to exclusive before generic timestamp update; NOWAIT returns `-EAGAIN`.

## State And Data Structures

- Inode creation and lookup manipulate `gfs2_inode` identity, glocks, iopen holder, quota data, rgrp reservations, disk flags, size/blocks, mode, ACL/security xattrs, directory entry counts, and allocation goals.
- Directory-add operations use `struct gfs2_diradd` and transaction reservations calculated by `gfs2_trans_da_blks()`.
- Multi-inode rename uses arrays of `gfs2_holder` with `GL_ASYNC` and the global `sd_rename_gl`.
- Quota-changing setattr uses old/new uid/gid pairs, `gfs2_alloc_parms`, quota locks, quota checks, and quota deltas over current inode block count.

## Dependencies

- VFS inode, dentry, namei, ACL, xattr, LSM, permission, setattr, fiemap, and iomap APIs.
- GFS2 glocks/glops, directory code, bmap/iomap, metadata I/O, quota, rgrp allocation, transactions, super/withdraw helpers, ACL/xattr code, and file operations from `file.c`.

## Risks And Invariants

- New inode creation is not a single transaction; comments note the crash window where an allocated block can look like a valid inode, and cleanup must zero link count/deallocate correctly on failure.
- Inode/iopen glock object binding must be undone on failure to avoid stale object pointers.
- Rename/exchange require strict multi-glock acquisition and retry discipline to avoid deadlocks and stale state.
- Directory moves must preserve dotdot and parent nlink invariants.
- Permission/getattr paths must avoid blocking in RCU mode.
- Quota transfer on chown must debit old IDs and credit new IDs under quota locks in the same transaction.
- Fiemap must not fault user memory while holding the glock; it retries after faulting the destination.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/inode.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/inode.h

## Scope

This header declares inode-facing GFS2 helpers, small inline inode predicates/accounting helpers, file operation exports, and file attribute APIs.

## APIs And Helpers

- Declares folio/internal read/address-space helpers: `gfs2_release_folio()`, `gfs2_internal_read()`, `gfs2_set_aops()`.
- Inline predicates: `gfs2_is_stuffed()`, `gfs2_is_jdata()`, `gfs2_is_ordered()`, `gfs2_is_writeback()`, `gfs2_is_dir()`.
- Block accounting helpers: `gfs2_set_inode_blocks()`, `gfs2_get_inode_blocks()`, `gfs2_add_inode_blocks()`.
- Identity helpers: `gfs2_check_inum()`, `gfs2_inum_out()`, `gfs2_check_internal_file_size()`.
- Declares inode lookup and namespace helpers: `gfs2_setup_inode()`, `gfs2_inode_lookup()`, `gfs2_lookup_by_inum()`, `gfs2_dinode_dealloc()`, `gfs2_lookupi()`, `gfs2_lookup_meta()`.
- Declares `gfs2_permission()`, `gfs2_dinode_out()`, `gfs2_open_common()`, `gfs2_seek_data()`, `gfs2_seek_hole()`.
- Exports file operation tables, mapping DLM-disabled builds to nolock tables.
- Declares file attribute helpers and `gfs2_set_inode_flags()`.
- Defines `gfs2_localflocks()` based on DLM build support and mount arguments.

## Dependencies And Role

- Included by file, inode, glops, and other GFS2 files needing inode state predicates, VFS op tables, and lookup/permission helpers.
- Bridges inode implementation with file operations and build-time DLM configuration.

## Risks And Invariants

- `gfs2_is_stuffed()` relies on `i_height == 0` as the inline-data marker.
- Block accounting shifts between filesystem blocks and sectors; callers must pass block counts, not byte counts.
- `gfs2_check_internal_file_size()` enforces internal file size alignment and withdraws/marks consistency errors through `gfs2_consist_inode()`.
- Build-time DLM conditionals change exported operation tables; callers should use the public names rather than assuming lock support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/inode.h -->