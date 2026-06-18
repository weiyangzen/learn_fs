# Group Research: group_758_linux_sources_os_linux_linux_fs_gfs2_file_c_sources_os_linux_linux_f_cf4d839b8457

Scope: `Docs/research_subset_a.md`, covering `sources/os/linux/linux` GFS2 files in this work item.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/file.c -->
# File Research: sources/os/linux/linux/fs/gfs2/file.c

## Scope

Implements GFS2 file and directory VFS operations: llseek, readdir, inode file attributes, ioctls, mmap faults, open/release, fsync, buffered/direct reads and writes, fallocate/punch-hole handling, splice-write size hints, and optional DLM-backed POSIX/flock locking.

## Public And Internal APIs Covered

- File operation tables: `gfs2_file_fops`, `gfs2_dir_fops`, `gfs2_file_fops_nolock`, `gfs2_dir_fops_nolock`.
- Attribute APIs: `gfs2_fileattr_get()`, `gfs2_fileattr_set()`, `gfs2_set_inode_flags()`.
- File lifecycle: `gfs2_open_common()`, `gfs2_open()`, `gfs2_release()`.
- I/O paths: `gfs2_file_read_iter()`, `gfs2_file_write_iter()`, direct read/write helpers, buffered write helper.
- MM paths: `gfs2_mmap()`, `gfs2_fault()`, `gfs2_page_mkwrite()`.
- Allocation paths: `gfs2_fallocate()`, `__gfs2_fallocate()`, `fallocate_chunk()`.
- DLM locking paths: `gfs2_lock()`, `gfs2_flock()`, `do_flock()`, `do_unflock()`.

## Control Flow And Behavior

- `gfs2_llseek()` takes the inode glock for `SEEK_END`, delegates data/hole seeks to inode helpers, and avoids glock acquisition for seek modes that do not need inode size or block mapping.
- `gfs2_readdir()` acquires the directory inode glock shared before calling `gfs2_dir_read()`.
- File flags map between VFS `FS_*` flags and on-disk `GFS2_DIF_*` flags. JDATA changes flush/wait/truncate cached pages, update ordered-data state, commit a dinode transaction, and reset address-space operations.
- `gfs2_page_mkwrite()` holds the inode glock exclusive, validates EOF, updates times, marks the glock dirty, unstuffs inline files when needed, reserves quota/rgrp space, begins a transaction, allocates backing blocks through iomap, and returns with the folio locked and dirty on success.
- Direct I/O uses deferred glock mode, disables or fences page faults while cluster locks are held, manually faults user pages on `-EFAULT`, and retries. Direct writes past EOF fall back to buffered I/O.
- Buffered writes acquire the inode glock exclusive, pre-fault user pages when possible, write through iomap, and lock the statfs inode when writing the rindex inode.
- `gfs2_file_write_iter()` serializes through `inode_lock()`, runs generic write checks and privilege stripping, dispatches direct or buffered writes, and performs sync/writeback handling.
- Fallocate supports punch-hole and keep-size allocation; journaled data files reject normal fallocate except for the rindex inode.
- DLM POSIX locks delegate to `dlm_posix_*`; DLM flock locks use per-open `gfs2_file::f_fl_gh` holders on `gfs2_flock_glops` glocks.

## State And Invariants

- Uses `gfs2_inode` fields `i_gl`, `i_diskflags`, `i_sizehint`, `i_res`, and `i_flags` including `GIF_SW_PAGED`.
- Per-open `struct gfs2_file` stores flock mutex/holder state.
- Page-fault recursion while holding glocks is explicitly avoided.
- Direct I/O buffered fallback must be synced and invalidated before reporting combined progress.
- Fallocate reservation math must remain consistent with quota, rgrp, metadata, and transaction reservations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/gfs2.h -->
# File Research: sources/os/linux/linux/fs/gfs2/gfs2.h

## Scope

Small common GFS2 header defining simple shared constants used across the filesystem.

## APIs And Constants

- Defines `NO_CREATE` / `CREATE` for object lookup or allocation call sites.
- Defines `NO_FORCE` / `FORCE` for call sites with optional forced behavior.
- Defines `GFS2_FAST_NAME_SIZE` as `8`, used for small-name storage thresholds elsewhere in GFS2.

## Dependencies And Invariants

- Has no external includes beyond its include guard.
- Provides intentionally minimal shared constants; semantic meaning comes from the call sites using these flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/gfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glock.c -->
# File Research: sources/os/linux/linux/fs/gfs2/glock.c

## Scope

Implements the GFS2 glock core: glock lookup/allocation, reference lifetime, holder enqueue/dequeue, local compatibility, DLM state transitions, demotion handling, lock reply completion, glock LRU/shrinker disposal, inode-delete verification work, withdrawal/thaw/unmount cleanup, and debugfs reporting.

## Public And Internal APIs Covered

- Lifetime and lookup: `gfs2_glock_get()`, `gfs2_glock_hold()`, `gfs2_glock_put()`, `gfs2_glock_put_async()`, `gfs2_glock_free()`, `gfs2_glock_free_later()`.
- Holder lifecycle: `__gfs2_holder_init()`, `gfs2_holder_reinit()`, `gfs2_holder_uninit()`, `gfs2_glock_nq()`, `gfs2_glock_wait()`, `gfs2_glock_dq()`, `gfs2_glock_dq_uninit()`.
- Multi-glock acquisition: `gfs2_glock_nq_m()`, `gfs2_glock_dq_m()`, async wait/retry via `gfs2_glock_async_wait()`.
- DLM callbacks: `gfs2_glock_cb()`, `gfs2_glock_complete()`.
- Inode deletion coordination: `gfs2_queue_try_to_evict()`, `gfs2_queue_verify_delete()`, `gfs2_cancel_delete_work()`, `gfs2_flush_delete_work()`.
- Global maintenance: `gfs2_gl_hash_clear()`, `gfs2_withdraw_glocks()`, `gfs2_glock_thaw()`, `gfs2_glock_init()`, `gfs2_glock_exit()`.
- Debugging: `gfs2_dump_glock()`, `gfs2_create_debugfs_file()`, `gfs2_delete_debugfs_file()`, debugfs `glocks`, `glockfd`, `glstats`, `sbstats`.

## Control Flow And Behavior

- Glocks live in a global `rhashtable` keyed by `lm_lockname`; concurrent insertion waits on a hashed waitqueue when a dying glock with the same name is being removed.
- `may_grant()` enforces local compatibility: exclusive is exclusive except node-scope sharing, shared matches shared, deferred matches deferred, and `LM_FLAG_ANY` can accept compatible non-unlocked states.
- `gfs2_glock_nq()` queues holders, rejects impossible try-locks early, traps recursive non-flock locking by the same pid, and runs the queue; synchronous holders wait on `HIF_WAIT`, async holders rely on polling/wait APIs.
- `run_queue()` promotes locally grantable holders, starts DLM conversions through `do_xmote()`, and handles pending demotes only when current holders permit.
- `do_xmote()` invokes glock operation sync/invalidate hooks before demotion, avoids new locking operations after withdrawal, issues DLM `lm_lock()` when available, or completes locally.
- `finish_xmote()` records DLM replies, retries unlock/convert deadlock paths, reports try-lock failures, calls `go_xmote_bh`, promotes waiters, and wakes blocked holders.
- Remote callbacks call `request_demote()`, optionally delay inode demotion using adaptive hold time, and queue glock work.
- LRU/shrinker code demotes or frees idle glocks, sorting disposal by glock number to improve disk access locality.
- Iopen delete work evicts cached inodes or verifies deleted generations using `gfs2_lookup_by_inum()`.
- Unmount sets `SDF_SKIP_DLM_UNLOCK`, flushes work, demotes/clears all glocks, waits for `sd_glock_disposal`, unmounts locking, frees deferred dead glocks, and destroys the workqueue.

## State And Invariants

- `gl_lockref.lock` protects glock state, target, demote state, holder list, reply fields, and object pointer.
- `GLF_LOCK` serializes DLM conversion; `GLF_DEMOTE_IN_PROGRESS` is only valid while `GLF_LOCK` is set.
- `GLF_HAVE_FROZEN_REPLY` defers replies during DLM recovery unless a recovery holder is present.
- Holders must be removed from `gl_holders` before uninit; uninit drops the glock reference and pid reference.
- `GL_NOCACHE` forces demotion to unlocked on release.
- The LRU contains only unreferenced, non-dead glocks that may still have DLM state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glock.h -->
# File Research: sources/os/linux/linux/fs/gfs2/glock.h

## Scope

Declares the public glock interface, lock manager state/type/flag constants, lock manager operation vector, glock address-space wrapper, holder helpers, debug/assert macros, and lifecycle APIs used throughout GFS2.

## APIs And Constants

- Lock types: `LM_TYPE_INODE`, `LM_TYPE_RGRP`, `LM_TYPE_META`, `LM_TYPE_IOPEN`, `LM_TYPE_FLOCK`, `LM_TYPE_PLOCK`, `LM_TYPE_QUOTA`, `LM_TYPE_JOURNAL`, and nondisk/reserved types.
- Lock states: `LM_ST_UNLOCKED`, `LM_ST_EXCLUSIVE`, `LM_ST_DEFERRED`, `LM_ST_SHARED`.
- Request flags include try-lock, recovery, any-state, node-scope, async, exact, skip, no-pid, no-cache, and no-block modes.
- DLM reply flags include state mask, retry/deadlock/canceled/error statuses.
- Defines `struct lm_lockops`, the lock manager interface used by `glock.c`.
- Declares holder/glock APIs for get/put, enqueue/dequeue, waits, multi-lock acquisition, callbacks, delete work, hash clear, withdraw, thaw, debugfs, and object association.
- Inline helpers include `gfs2_glock_is_locked_by_me()`, `gfs2_glock2aspace()`, `gfs2_glock_nq_init()`, `gfs2_holder_initialized()`, `gfs2_holder_queued()`, and `glock_needs_demote()`.

## Invariants

- `gfs2_glock_is_locked_by_me()` only scans current granted holders and stops at first waiter.
- `gfs2_glock2aspace()` is valid only for glock operation types with `GLOF_ASPACE`.
- `gfs2_glock_nq_init()` owns cleanup on enqueue failure by uninitializing the holder.
- `GLOCK_BUG_ON` dumps glock state before crashing, making glock invariants diagnosable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glops.c -->
# File Research: sources/os/linux/linux/fs/gfs2/glops.c

## Scope

Defines glock operation callbacks for metadata, inode, resource group, freeze, iopen, flock, quota, journal, and nondisk glock types. Handles AIL flushing, metadata sync/invalidation, dinode refresh, freeze callbacks, and iopen eviction callbacks.

## Public And Internal APIs Covered

- Exported helpers: `gfs2_ail_flush()`, `gfs2_inode_metasync()`, `gfs2_glock2rgrp()`.
- Glock operation objects: `gfs2_meta_glops`, `gfs2_inode_glops`, `gfs2_rgrp_glops`, `gfs2_freeze_glops`, `gfs2_iopen_glops`, `gfs2_flock_glops`, `gfs2_nondisk_glops`, `gfs2_quota_glops`, `gfs2_journal_glops`, and `gfs2_glops_list[]`.
- Inode callbacks: `inode_go_sync()`, `inode_go_inval()`, `inode_go_instantiate()`, `inode_go_held()`, `inode_go_dump()`.
- Rgrp callbacks: `rgrp_go_sync()`, `rgrp_go_inval()`, `gfs2_rgrp_go_dump()`.
- Freeze/iopen callbacks: `freeze_go_callback()`, `freeze_go_xmote_bh()`, `iopen_go_callback()`.

## Control Flow And Behavior

- AIL flush walks a glock’s AIL buffers, adds revokes, withdraws on unexpected dirty/pinned/locked buffers outside fsync-tolerant paths, and flushes the log.
- Rgrp sync flushes the log for dirty rgrp glocks, writes/waits the metadata range, empties AIL state, and frees allocation clones.
- Rgrp invalidation releases rgrp buffers, asserts AIL is empty, and truncates the rgrp metadata range.
- Inode sync waits for direct I/O on regular files, unmaps shared writable mappings when needed, flushes metadata and data, empties AIL, clears dirty state, and wakes glop-pending waiters.
- Inode invalidation truncates metadata pages on full invalidation, marks instantiate needed, drops ACL/security/dir hash caches, invalidates rindex state, and truncates regular file page cache.
- Dinode refresh validates inode number, type, height, directory depth, exhash rules, stuffed-file size, and populates VFS inode metadata from disk.
- `inode_go_held()` waits for direct I/O for non-deferred holders and resumes interrupted truncation when the inode is held exclusive.
- Freeze callbacks schedule freeze work on remote unlock requests and reload journal-head state after freeze glock promotion/demotion.
- Iopen callback schedules remote eviction when another node wants the iopen glock unlocked.

## State And Invariants

- `GLF_DIRTY` controls whether inode/rgrp sync work is needed.
- `GIF_GLOP_PENDING` protects inode pointers during glock operation callbacks.
- Inode glocks use `GLOF_ASPACE | GLOF_LVB`; rgrp and quota glocks use LVBs.
- Metadata invalidation requires empty AIL state.
- Dinode validation defends against stale or corrupt on-disk metadata before exposing inode state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glops.h -->
# File Research: sources/os/linux/linux/fs/gfs2/glops.h

## Scope

Header exporting glock operation descriptors and glock operation helper APIs.

## APIs

- Declares global freeze workqueue `gfs2_freeze_wq`.
- Exports all glock operation tables used by glock creation and lock-type dispatch.
- Exports `gfs2_glops_list[]`, indexed by lock type.
- Declares `gfs2_inode_metasync()` and `gfs2_ail_flush()`.

## Invariants

- Consumers select behavior by lock type through these operation tables.
- Only the declarations live here; callback behavior is implemented in `glops.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/glops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/incore.h -->
# File Research: sources/os/linux/linux/fs/gfs2/incore.h

## Scope

Central in-core GFS2 data model header. Defines runtime structures for glocks, holders, inodes, resource groups, quota data, transactions, journals, mount arguments, lockspace state, per-cpu lock stats, and the superblock-private `gfs2_sbd`.

## Major Structures

- Logging: `gfs2_log_header_host`, `gfs2_log_operations`, `gfs2_bufdata`, `gfs2_trans`, `gfs2_jdesc`, `gfs2_revoke_replay`.
- Allocation: `gfs2_bitmap`, `gfs2_rgrpd`, `gfs2_blkreserv`, `gfs2_alloc_parms`.
- Locking: `lm_lockname`, `gfs2_glock_operations`, `gfs2_holder`, `gfs2_glock`, `lm_lockstruct`, `gfs2_lkstats`, `gfs2_pcpu_lkstats`.
- Inode/file state: `gfs2_inode`, `gfs2_file`.
- Quota/statfs: `gfs2_qadata`, `gfs2_quota_data`, `gfs2_statfs_change_host`, `local_statfs_inode`.
- Mount/superblock: `gfs2_args`, `gfs2_tune`, `gfs2_sb_host`, `gfs2_sbd`.

## Important Flags And Helpers

- Buffer bits: `BH_Pinned`, `BH_Escaped`.
- DLM recovery flags: `DFL_BLOCK_LOCKS`, `DFL_NO_DLM_OPS`, `DFL_FIRST_MOUNT`, `DFL_MOUNT_DONE`, `DFL_DLM_RECOVERY`, and related flags.
- Glock flags: `GLF_LOCK`, instantiate/demote/dirty/LRU/reply/delete/cancel states.
- Inode flags: `GIF_QD_LOCKED`, `GIF_SW_PAGED`, `GIF_GLOP_PENDING`.
- Superblock flags include journal, withdraw, recovery, freeze, kill, and eviction states.
- Inline helpers: `GFS2_I()`, `GFS2_SB()`, `glock_sbd()`, `gfs2_aspace()`, lock-stat increments, and `gfs2_max_stuffed_size()`.

## Invariants

- `lm_lockname` is designed as an rhashtable key with no internal holes before the key length.
- `struct gfs2_inode` embeds `struct inode` first so `GFS2_I()` is a container cast.
- Glock operation flags determine whether a glock has an attached metadata address space or LVB.
- `gfs2_sbd` is the cross-subsystem anchor for lock state, journals, rgrps, quota, log state, workqueues, and debugfs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/incore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/inode.c -->
# File Research: sources/os/linux/linux/fs/gfs2/inode.c

## Scope

Implements GFS2 inode lookup, creation, linking, unlink/rmdir, symlink/mkdir/mknod, atomic open, rename/exchange, permission checks, getattr/setattr, fiemap, seek-data/hole, symlink reads, inode operation tables, and inode setup/deallocation helpers.

## Public And Internal APIs Covered

- Exported helpers: `gfs2_setup_inode()`, `gfs2_inode_lookup()`, `gfs2_lookup_by_inum()`, `gfs2_lookup_meta()`, `gfs2_lookupi()`, `gfs2_permission()`, `gfs2_dinode_dealloc()`, `gfs2_seek_data()`, `gfs2_seek_hole()`.
- VFS inode operations: create, lookup, link, unlink/rmdir, symlink, mkdir, mknod, rename, permission, setattr, getattr, listxattr, fiemap, ACL operations, update_time, atomic_open, fileattr get/set.
- Creation internals: `create_ok()`, `alloc_dinode()`, `init_dinode()`, `gfs2_init_dir()`, `gfs2_init_xattr()`, `link_dinode()`, `gfs2_create_inode()`.
- Rename internals: `gfs2_rename()`, `gfs2_exchange()`, `gfs2_rename2()`, `gfs2_ok_to_move()`, `update_moved_ino()`.

## Control Flow And Behavior

- `gfs2_inode_lookup()` uses `iget5_locked()`, creates inode and iopen glocks for new inodes, optionally checks block type/generation, marks instantiate needed, attaches glock objects, sets inode/file ops, and handles stale generation mismatches.
- `gfs2_lookupi()` takes the directory glock shared unless already held, checks execute permission unless root/internal lookup, and searches the GFS2 directory.
- `gfs2_create_inode()` serializes on the parent directory glock exclusive, handles existing dentries for atomic open, reserves directory space, creates ACL/security xattrs, allocates dinode blocks, creates inode and iopen glocks, initializes the dinode, links it into the directory, and unwinds with deallocation on failure.
- Link/unlink paths take parent/child glocks, validate permissions, immutable/append/sticky-bit state, directory emptiness, quota/rgrp reservations, and update directory entries and link counts in transactions.
- Rename uses the global rename glock for cross-directory moves, asynchronously acquires involved inode glocks in deadlock-safe order, validates both old and new directory entries, reserves target directory space when needed, optionally unlinks the overwritten target, updates `..` for moved directories, and commits directory entry changes in one transaction.
- `RENAME_EXCHANGE` swaps two existing entries and adjusts parent link counts when directory/non-directory types cross parents.
- `gfs2_permission()` supports RCU/nonblocking permission checks by returning `-ECHILD` when it cannot take a glock.
- `gfs2_setattr()` takes the inode glock exclusive, handles size changes through truncate helpers, handles chown with quota transfer accounting, and updates ACLs on chmod.
- `gfs2_fiemap()`, `gfs2_seek_data()`, and `gfs2_seek_hole()` hold inode locks plus shared glocks and use iomap helpers; fiemap retries after faulting user extent memory.

## State And Invariants

- New inodes keep inode glock and iopen glock object pointers synchronized with `glock_set_object()` / `glock_clear_object()`.
- `i_no_addr`, `i_no_formal_ino`, and `gl_no_formal_ino` coordinate stale inode and remote delete detection.
- Directory operations assume parent/child/rgrp glocks are held before mutating directory entries, link counts, or unlink state.
- Creation failure before dentry instantiation must explicitly deallocate dinode/eattr state; after instantiation, eviction owns cleanup.
- Cross-directory rename must prevent moving a directory below itself by walking `..` under the rename glock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/inode.h -->
# File Research: sources/os/linux/linux/fs/gfs2/inode.h

## Scope

Declares GFS2 inode helper APIs, inline inode/data-mode helpers, block-count helpers, lookup/create-related exports, seek helpers, file operation exports, and file-attribute hooks.

## APIs And Helpers

- Declares page/internal read/address-space helpers: `gfs2_release_folio()`, `gfs2_internal_read()`, `gfs2_set_aops()`.
- Inline helpers classify inode/data state: `gfs2_is_stuffed()`, `gfs2_is_jdata()`, `gfs2_is_ordered()`, `gfs2_is_writeback()`, `gfs2_is_dir()`.
- Block helpers convert between GFS2 block counts and VFS sector-based `i_blocks`: `gfs2_set_inode_blocks()`, `gfs2_get_inode_blocks()`, `gfs2_add_inode_blocks()`.
- Identity helpers: `gfs2_check_inum()`, `gfs2_inum_out()`, `gfs2_check_internal_file_size()`.
- Declares inode lookup and permission APIs used outside `inode.c`.
- Declares `gfs2_open_common()`, `gfs2_seek_data()`, `gfs2_seek_hole()`, and fileattr functions implemented in `file.c`.
- Exports DLM and nolock file operation tables, with compile-time selection for single-node builds.

## Invariants

- `gfs2_is_stuffed()` treats height zero as inline/stuffed data.
- `gfs2_check_internal_file_size()` enforces min/max and block alignment for internal metadata files and reports inode consistency errors on failure.
- `gfs2_localflocks()` returns mount option state under DLM builds and always local-locking in single-node builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/inode.h -->