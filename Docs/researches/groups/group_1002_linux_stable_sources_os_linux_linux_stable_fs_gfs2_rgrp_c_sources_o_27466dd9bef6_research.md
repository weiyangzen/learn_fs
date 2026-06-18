# Group Research: group_1002_linux_stable_sources_os_linux_linux_stable_fs_gfs2_rgrp_c_sources_o_27466dd9bef6

Scope: `Docs/research_subset_a.md`. This grouped report covers the requested Linux stable GFS2 and HFS source files only.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/rgrp.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/rgrp.c

## Scope

This file implements GFS2 resource group indexing, bitmap interpretation, block reservation, allocation/freeing, rgrp LVB synchronization, rgrp verification, FITRIM/discard, and rgrp-list locking helpers. It is the central allocator implementation behind `gfs2_inplace_reserve()`, `gfs2_alloc_blocks()`, dinode unlink/free paths, and extent/xattr metadata frees.

## Public And Internal APIs Covered

- Public rgrp lookup and traversal: `gfs2_blk2rgrpd()`, `gfs2_rgrpd_get_first()`, `gfs2_rgrpd_get_next()`, `check_and_update_goal()`.
- Rindex/rgrp lifecycle: `gfs2_rindex_update()`, `gfs2_ri_total()`, `gfs2_clear_rgrpd()`, `gfs2_rgrp_go_instantiate()`, `gfs2_rgrp_brelse()`, `gfs2_free_clones()`.
- Reservation APIs: `gfs2_inplace_reserve()`, `gfs2_inplace_release()`, `gfs2_rs_deltree()`, `gfs2_rs_delete()`.
- Allocation/free APIs: `gfs2_alloc_blocks()`, `__gfs2_free_blocks()`, `gfs2_free_meta()`, `gfs2_unlink_di()`, `gfs2_free_di()`, `gfs2_check_blk_type()`.
- Discard and diagnostics: `gfs2_rgrp_send_discards()`, `gfs2_fitrim()`, `gfs2_rgrp_verify()`, `gfs2_rgrp_dump()`.
- Rgrp list helpers: `gfs2_rlist_add()`, `gfs2_rlist_alloc()`, `gfs2_rlist_free()`, `rgrp_lock_local()`, `rgrp_unlock_local()`.

## Control Flow And Behavior

Resource group bitmap state is encoded as two bits per data block: free, used data, unlinked dinode, or used metadata/dinode. `gfs2_setbit()` enforces legal state transitions with `valid_change[]` and reports consistency failures with rgrp details before withdrawing. `gfs2_testbit()`, `gfs2_bit_search()`, `gfs2_bitfit()`, `gfs2_rbm_from_block()`, and `gfs2_rbm_add()` provide the low-level bitmap cursor machinery.

`gfs2_rindex_update()` locks the rindex inode if needed, then `read_rindex_entry()` allocates `gfs2_rgrpd` objects, initializes their rgrp glocks, computes bitmap descriptors with `compute_bitstructs()`, and inserts them into `sd_rindex_tree`. `set_rgrp_preferences()` marks node-local preferred rgrps based on journal id to reduce cluster contention.

Rgrp instantiation reads all bitmap/header blocks through the rgrp glock, validates metadata types, loads on-disk counters into `rd_free`, `rd_dinodes`, and `rd_igeneration`, initializes `rd_free_clone` and allocation failure state, and either initializes or validates the rgrp LVB. `update_rgrp_lvb()` can satisfy rgrp state from a valid LVB when `ar_rgrplvb` is enabled.

`gfs2_inplace_reserve()` searches up to three passes for an rgrp that can satisfy `ap->target` or later `ap->min_target`. It starts from an active reservation or inode goal, optionally applies Orlov directory skipping, avoids contended rgrp glocks using glock timing statistics, reclaims unlinked dinodes via `try_rgrp_unlink()`, flushes the log before the final pass, and records `rs_reserved` against `rd_reserved`.

Reservation discovery uses `rg_mblk_search()` and `gfs2_rbm_find()`. The search uses clone bitmaps when avoiding newly freed blocks, skips `GBF_FULL` bitmap blocks, respects other inodes' reservation ranges through `gfs2_next_unreserved_block()`, and updates `rd_extfail_pt` when no extent large enough exists. If a smaller but usable maximum extent is found, the minimum request is reduced to that extent.

`gfs2_alloc_blocks()` takes the local rgrp mutex, searches within the active reservation first and then without reservation, marks one dinode block or data/metadata blocks through `gfs2_alloc_extent()`, updates inode goal fields, consumes reservation accounting, decrements free counters, writes the rgrp header/LVB with `gfs2_rgrp_out()`, updates statfs and quota, and removes revokes for new dinode allocations. Any impossible allocation after reservation marks the rgrp readonly until unmount.

Freeing uses clone bitmaps. `rgblk_free()` allocates `bi_clone` lazily, copies the live bitmap into it, journals the bitmap buffer, then changes live bits. `__gfs2_free_blocks()` clears bitmap state, increments `rd_free`, clears the trimmed flag, writes the rgrp header, and wipes journal state for metadata/jdata/directory blocks. `gfs2_unlink_di()` changes a dinode to `UNLINKED` and increments `rl_unlinked`; `gfs2_free_di()` later returns it to free space and decrements dinode/unlinked counters.

FITRIM checks privileges, live journal state, discard capability, and rindex freshness, then locks each rgrp exclusively and submits discards for free ranges found by comparing clone/current bitmap state. Successfully trimmed rgrps are journaled with `GFS2_RGF_TRIMMED`; discard errors disable the mount's discard option.

## State And Data Structures

- `struct gfs2_rbm` is a cursor of rgrp, bitmap index, and bitmap-relative offset.
- `struct gfs2_extent` stores a candidate cursor plus length for fallback extent selection.
- `struct gfs2_rgrpd` state maintained here includes `rd_bits`, `rd_gl`, `rd_rgl`, `rd_flags`, `rd_free`, `rd_free_clone`, `rd_dinodes`, `rd_igeneration`, `rd_requested`, `rd_reserved`, `rd_extfail_pt`, `rd_last_alloc`, `rd_rstree`, and `rd_mutex`.
- `struct gfs2_blkreserv` ranges are kept in an rbtree per rgrp and carry `rs_start`, `rs_requested`, `rs_reserved`, and `rs_rgd`.
- Bitmap block state flags include `GBF_FULL`; rgrp flags include on-disk flags, preferred/error/check masks, and `GFS2_RGF_TRIMMED`.

## Dependencies

The file depends on GFS2 glocks, rindex internal reads, meta I/O, transactions, quotas, statfs, log flushing, rgrp LVBs, inode goals, journal wipes, glock statistics, and tracepoints. It also uses Linux rbtrees, buffer heads, discard APIs, capability checks, and user copy for `FITRIM`.

## Risks And Invariants

Allocation correctness depends on synchronizing the rgrp glock, local `rd_mutex`, reservation spinlock, clone bitmaps, transaction metadata buffers, and rgrp header/LVB counters. `rd_free`, `rd_free_clone`, `rd_requested`, and `rd_reserved` must never drift. Clone bitmaps intentionally prevent immediate reallocation of recently freed blocks before journal safety. `gfs2_check_blk_type()` relies on the inode glock for dinode synchronization and only makes sense for dinode/unlinked checks. Rgrp LVB mode can skip disk reads only when LVB magic and counters are valid. `rd_extfail_pt` is a performance hint and must not exclude allocations after reservations or frees change availability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/rgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/rgrp.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/rgrp.h

## Scope

This header declares the GFS2 resource group allocator interface used by inode, metadata, xattr, statfs, and trim paths. It also defines reservation tuning constants and inline helpers for reservation/rgrp membership tests.

## APIs And Definitions

- Reservation constants: `RGRP_RSRV_MINBLKS` reserves at least one 64-bit bitmap word's worth of blocks, and `RGRP_RSRV_ADDBLKS` grows inode size hints when reservations are consumed.
- Lookup/lifecycle declarations cover rgrp tree lookup/traversal, rindex update, rgrp instantiate/release, clone cleanup, and rgrp verification/dumping.
- Allocation declarations expose inplace reservation/release, block allocation, block/dinode freeing, unlinked dinode marking, and block type validation.
- `struct gfs2_rgrp_list` stores a dynamic list of rgrps and matching glock holders for multi-rgrp operations such as xattr indirect deallocation.
- Trim declarations expose `gfs2_rgrp_send_discards()` and `gfs2_fitrim()`.
- Inline `gfs2_rs_active()` checks whether a reservation is in an rbtree via `RB_EMPTY_NODE()`.
- Inline `rgrp_contains_block()` checks whether a filesystem block lies in an rgrp's data span.

## Dependencies

The header uses Linux slab/uaccess declarations and GFS2 inode, rgrp, holder, buffer, and file structures through forward declarations or included headers.

## Risks And Invariants

Callers must not treat `rgrp_contains_block()` as matching bitmap/header padding; it only tests `[rd_data0, rd_data0 + rd_data)`. `gfs2_rs_active()` requires reservation nodes to be initialized with `RB_CLEAR_NODE()` when inactive. `gfs2_rg_blocks()` lives in `trans.h`, but callers using the allocation API must reserve enough transaction blocks for rgrp header/bitmap updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/rgrp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/super.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/super.c

## Scope

This file implements GFS2 superblock operations and high-level filesystem lifecycle behavior: journal index cleanup, transition between read-only/read-write operation, statfs accounting and sync, freeze/thaw, inode writeback/dirtying, mount option display, inode eviction/deletion, inode slab allocation, and local statfs inode helpers.

## Public And Internal APIs Covered

- Journal helpers: `gfs2_jindex_free()`, `gfs2_jdesc_find()`, `gfs2_jdesc_check()`.
- RW/RO transitions: `gfs2_make_fs_rw()`, `gfs2_make_fs_ro()`, `gfs2_put_super()`, `gfs2_sync_fs()`.
- Statfs: `gfs2_statfs_change_in()`, `gfs2_statfs_change_out()`, `gfs2_statfs_init()`, `gfs2_statfs_change()`, `update_statfs()`, `gfs2_statfs_sync()`, `gfs2_statfs()`.
- Freeze/thaw: `gfs2_lock_fs_check_clean()`, `gfs2_freeze_func()`, `gfs2_freeze_super()`, `gfs2_freeze_fs()`, `gfs2_thaw_super()`.
- Inode metadata: `gfs2_dinode_out()`, `gfs2_write_inode()`, `gfs2_dirty_inode()`, `gfs2_drop_inode()`, `gfs2_evict_inode()`.
- VFS operation table: `gfs2_super_ops`.
- Local statfs helpers: `free_local_statfs_inodes()`, `find_local_statfs_inode()`.

## Control Flow And Behavior

`gfs2_jindex_free()` detaches the journal descriptor list under `sd_jindex_spin`, clears `sd_jdesc` under `sd_log_flush_lock`, frees each descriptor's journal extents, drops the journal inode, and frees descriptor memory. `gfs2_jdesc_check()` validates journal file size, computes block count, and rejects journals that still need allocation.

`gfs2_make_fs_rw()` invalidates the local journal glock's metadata, rejects unknown local journal sequence state, initializes quotas, and sets `SDF_JOURNAL_LIVE` if successful. `gfs2_make_fs_ro()` stops delete work and GFS2 threads, syncs quotas/statfs, performs two log flushes so revokes can be written before shutdown clears journal liveness, waits for an empty log, and cleans up quotas.

Statfs uses master and local statfs-change inodes. `gfs2_statfs_change()` journals the local statfs buffer, updates local counters under `sd_statfs_spin`, and wakes statfs sync when the configured percentage threshold is exceeded. `gfs2_statfs_sync()` locks the master statfs inode exclusively, reads master counters, starts a transaction, merges local counters into master with `update_statfs()`, zeros local counters, and clears forced sync. `gfs2_statfs_slow()` can instead lock every rgrp asynchronously and sum verified rgrp counters.

Freeze first freezes the VFS superblock, then `gfs2_lock_fs_check_clean()` locks journal glocks shared, unlocks the shared freeze glock, takes the freeze glock exclusively with recovery semantics, and checks every journal head for clean unmount state. Failures thaw and retry, especially when recovery is in progress. Thaw re-acquires shared freeze locking and clears `SDF_FREEZE_INITIATOR` / `SDF_FROZEN`.

`gfs2_dinode_out()` serializes VFS inode state and GFS2 inode fields into an on-disk dinode. `gfs2_dirty_inode()` handles atime-style updates even when called with varied lock/freeze contexts: it acquires the inode glock if needed, starts a dinode transaction if none exists, writes the dinode buffer, then unwinds.

Eviction separates linked inode cleanup from unlinked dinode deletion. `gfs2_drop_inode()` notices remote iopen demote requests and can clear nlink locally; under memory pressure it queues deferred verification/delete work. `evict_should_delete()` verifies that an unlinked dinode is still marked `GFS2_BLKST_UNLINKED`, instantiates the inode glock, and may upgrade the iopen glock. `evict_unlinked_inode()` deallocates exhash directories, xattrs, file blocks, then the dinode. `evict_linked_inode()` flushes dirty metadata/data and truncates page cache. Final eviction always drops reservations, ordered inode state, page cache, dir hash state, and glock references.

## State And Data Structures

Key superblock state includes journal descriptor lists, local/master statfs counters and buffers, freeze glock/holder, journal live/error flags, log flush locks, local statfs inode list, inode/rgrp/glock caches, and mount option structures. Inode eviction uses `i_iopen_gh`, `i_gl`, `i_res`, `i_eattr`, `i_diskflags`, glock flags, and block type state.

## Dependencies

This file ties GFS2 to VFS super operations, writeback controls, freeze/thaw APIs, glock locking, journal/log/revoke machinery, quota subsystem, statfs inode metadata, rgrp verification, directory/file/xattr deallocation, and sysfs teardown.

## Risks And Invariants

Unmount must stop recovery and journal writes before freeing glocks, rgrps, and journal descriptors. Freeze must not report success unless every journal is clean under the exclusive freeze glock. Deleting an unlinked inode must verify bitmap state before reading the dinode block. Memory pressure paths avoid direct DLM calls and use deferred glock put/delete work. Statfs local/master counters can be temporarily approximate but must be merged transactionally. Dirty inode updates must not start transactions after withdrawal or without correct glock state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/super.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/super.h

## Scope

This header exposes GFS2 superblock, journal, statfs, freeze, filesystem type, export, dentry, super operation, and xattr handler interfaces.

## APIs And Definitions

- Supported on-disk format range is declared as `GFS2_FS_FORMAT_MIN` 1801 through `GFS2_FS_FORMAT_MAX` 1802.
- `gfs2_jindex_size()` safely returns `sd_journals` under `sd_jindex_spin`.
- Declarations cover journal descriptor lookup/check/free, master-dir lookup, read-write/read-only transitions, uevents/thread destruction, statfs initialization/change/sync, freeze work, local statfs inode helpers, and `free_sbd()`.
- External operation tables include `gfs2_fs_type`, `gfs2meta_fs_type`, `gfs2_export_ops`, `gfs2_super_ops`, and `gfs2_dops`.
- Xattr handler pointer arrays are exported for format-min/format-max handler selection.

## Dependencies

The header depends on Linux `fs.h`, `dcache.h`, and GFS2 in-core structures.

## Risks And Invariants

Format gating matters for xattr namespace support in `xattr.c`. `gfs2_jindex_size()` is only a snapshot; callers needing descriptor stability must still hold appropriate locks. Lifecycle routines declared here often assume system inodes and glocks have already been initialized by mount code outside this file group.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/sys.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/sys.c

## Scope

This file implements GFS2 sysfs objects and attributes under the `gfs2` kset. It exposes mount identity/status, freeze and withdraw controls, quota/statfs sync triggers, glock demotion, lock-module controls, journal recovery controls, journal id/first-mounter assignment, and tunables.

## Public And Internal APIs Covered

- Generic sysfs plumbing: `struct gfs2_attr`, `gfs2_attr_show()`, `gfs2_attr_store()`, `gfs2_ktype`, `gfs2_uevent_ops`.
- Filesystem attributes: `id`, `fsname`, `uuid`, `freeze`, `withdraw`, `statfs_sync`, `quota_sync`, `quota_refresh_user`, `quota_refresh_group`, `demote_rq`, `status`.
- Lock module attributes: `proto_name`, `block`, `withdraw`, `jid`, `first`, `first_done`, `recover`, `recover_done`, `recover_status`.
- Tunables: quota warning/quantum/scale, max readahead, complaint period, statfs slow/quantum, new-files jdata, withdraw helper timeout.
- Exported functions: `gfs2_sys_fs_add()`, `gfs2_sys_fs_del()`, `gfs2_sys_init()`, `gfs2_sys_uninit()`, `gfs2_recover_set()`.

## Control Flow And Behavior

`gfs2_sys_fs_add()` initializes the per-mount kobject with the table name, creates the default, `tune`, and `lock_module` groups, links the block device as `device`, and emits a `KOBJ_ADD` uevent with read-only and spectator state. Teardown removes the link/groups, puts the kobject, and waits for `sd_kobj_unregister`.

Identity and status attributes expose device number, filesystem name, UUID, and detailed `sd_flags`/log counters. `freeze_store()` accepts only `0` or `1` from CAP_SYS_ADMIN and invokes VFS thaw/freeze. `withdraw_store()` accepts only `1`, logs a user-requested cluster withdraw, and calls `gfs2_withdraw()`.

Quota/statfs controls require CAP_SYS_ADMIN and accept `1` as a trigger. User and group quota refresh parse ids into `kqid` values in the current user namespace and call `gfs2_quota_refresh()`.

`demote_rq_store()` parses `<gltype>:<glnum> <mode>`, maps textual modes to GFS2 lock states, resolves the right glock operations including the special freeze glock, sets `SDF_DEMOTE` once, gets the glock without creation, issues a callback demotion, and puts the glock.

Lock-module controls expose protocol name and DLM-style block/unblock. Clearing block mode uses a memory barrier and thaws glocks. The helper withdraw status attribute completes `sd_withdraw_helper` with status 0 or 1 for the offline uevent flow in `util.c`.

Journal id and first-mounter stores wait for locking initialization, take `sd_jindex_spin`, and only allow changes while `SDF_NOJOURNALID` is still set. Spectator mounts cannot claim a positive journal id. `gfs2_recover_set()` waits for the local journal to be ready, rejects recovery of the local journal on non-spectator mounts, finds the requested journal descriptor, and queues recovery.

Tunables are read and updated under `gt_spin`; setters require CAP_SYS_ADMIN and optionally reject zero.

## State And Data Structures

The file manipulates `sd_kobj`, `sd_kobj_unregister`, `sd_flags`, `sd_lockstruct`, `sd_jdesc`, log counters, tunables in `sd_tune`, `sd_withdraw_helper_status`, `sd_withdraw_helper`, `sd_locking_init`, and the global `gfs2_kset`.

## Dependencies

It depends on Linux kobject/sysfs/kset APIs, capability checks, current user namespace quota ids, block-device kobjects, and GFS2 glock, quota, statfs, recovery, freeze, and withdraw subsystems.

## Risks And Invariants

Most store handlers are privileged because they can freeze the filesystem, withdraw the mount, alter quota state, trigger recovery, or force glock demotion. Journal id and first-mount assignment are valid only before mount locking has completed journal selection. Sysfs teardown must wait for kobject release before freeing the superblock. `demote_rq` accepts raw glock identifiers, so strict parsing and glock type validation are important.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/sys.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/sys.h

## Scope

This header declares the small public interface for GFS2 sysfs setup, teardown, global kset lifecycle, and journal recovery triggering.

## APIs

- `gfs2_sys_fs_add()` creates per-mount sysfs entries.
- `gfs2_sys_fs_del()` removes per-mount sysfs entries and waits for kobject release.
- `gfs2_sys_init()` creates the global `gfs2` kset.
- `gfs2_sys_uninit()` unregisters the global kset.
- `gfs2_recover_set()` triggers recovery for a journal id.

## Dependencies And Invariants

Callers pass a live `struct gfs2_sbd`. `gfs2_sys_fs_del()` assumes `gfs2_sys_fs_add()` succeeded far enough to initialize the kobject and groups. Recovery triggering is implemented in `sys.c` but depends on journal readiness and recovery state outside this header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/sys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/trace_gfs2.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/trace_gfs2.h

## Scope

This tracepoint header defines the `gfs2` trace system. It covers glock state transitions and queueing, demote requests, lock timing statistics, log pin/flush/reservation/AIL events, block mapping and iomap operations, block allocation/free state, and multi-block reservation events.

## Trace Events And Helpers

- Symbol helpers map DLM states to readable names, bitmap states to `free/used/dinode/unlinked`, reservation actions to delete/tree-delete/insert/claim, and glock flags to compact flag strings.
- `glock_trace_state()` converts GFS2 lock states to DLM trace state constants.
- Locking events: `gfs2_glock_state_change`, `gfs2_glock_put`, `gfs2_demote_rq`, `gfs2_promote`, `gfs2_glock_queue`, `gfs2_glock_lock_time`.
- Journal/log events: `gfs2_pin`, `gfs2_log_flush`, `gfs2_log_blocks`, `gfs2_ail_flush`.
- Mapping/allocation events: `gfs2_bmap`, `gfs2_iomap_start`, `gfs2_iomap_end`, `gfs2_block_alloc`, `gfs2_rs`.

## Captured State

Lock tracepoints capture device, glock number/type, current/target/demote states, holder request state, remote/local demote source, glock flags, DLM reply status/flags, and smoothed timing counters. Log tracepoints capture device, sequence, flush flags, reservation deltas, free log blocks, pin/unpin block number and length, and AIL writeback mode/count. Allocation tracepoints capture inode number, physical block/range length, block state, rgrp address, clone-free blocks, requested reservations, and reserved blocks.

## Dependencies

The header depends on Linux tracepoint infrastructure, buffer heads, DLM constants, writeback controls, iomap, GFS2 in-core state, glocks, and rgrp definitions. It ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace_gfs2`, and `trace/define_trace.h` outside the include guard as required by tracepoint headers.

## Risks And Invariants

Trace events read live glock/rgrp/inode fields without adding primary synchronization; they are for diagnostics and assume callers pass stable objects at trace call sites. Field formats are part of observability tooling, so changes affect scripts. The `gfs2_rs` event uses `container_of(rs, struct gfs2_inode, i_res)`, so only inode-embedded reservations are valid.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/trace_gfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/trans.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/trans.c

## Scope

This file implements GFS2 transaction begin/end logic and helpers that attach metadata buffers, journaled data buffers, and revoke records to the active transaction. It mediates between filesystem mutation paths and the GFS2 log subsystem.

## Public And Internal APIs Covered

- Transaction lifecycle: `__gfs2_trans_begin()`, `gfs2_trans_begin()`, `gfs2_trans_end()`, `gfs2_trans_free()`.
- Buffer attachment: `gfs2_trans_add_data()`, `gfs2_trans_add_databufs()`, `gfs2_trans_add_meta()`.
- Revoke handling: `gfs2_trans_add_revoke()`, `gfs2_trans_remove_revoke()`.
- Diagnostics/allocation: `gfs2_print_trans()`, `gfs2_alloc_bufdata()`.

## Control Flow And Behavior

`__gfs2_trans_begin()` rejects nested transactions, zero-sized reservations, and withdrawn filesystems. It records the caller instruction pointer, block/revoke request, and reserved log block estimate. Metadata/data log descriptor overhead is included in `tr_reserved`. The function starts an internal write, takes `sd_log_flush_lock` for reading, verifies `SDF_JOURNAL_LIVE`, tries fast log/revoke reservation, and falls back to full reservation outside the lock if needed. Extra revokes are returned to the pool once the reservation is established.

`gfs2_trans_begin()` allocates a transaction object from `gfs2_trans_cachep` and delegates to `__gfs2_trans_begin()`. `gfs2_trans_end()` clears `current->journal_info`, releases all revokes and log blocks if the transaction was untouched, otherwise releases unused revokes, verifies that attached buffers/revokes fit reservations, commits the transaction to the log, frees unattached heap transactions, releases the log flush read lock, optionally flushes synchronously mounted filesystems, and ends the internal write.

`gfs2_trans_add_data()` attaches data buffers for journaled data mode. It handles already pinned buffers, allocates `gfs2_bufdata` if needed under `sd_log_lock`, asserts glock ownership, marks the glock dirty/LFLUSH, pins the buffer, increments data-buffer counts, and links it onto `tr_databuf`.

`gfs2_trans_add_meta()` follows similar mechanics for metadata, but validates the metadata magic before journaling, rejects adding buffers after withdrawal or complete freeze, pins the buffer, zeroes pad state, stamps the journal id into the metadata header, increments metadata-buffer counts, and links onto `tr_buf`.

`gfs2_trans_add_databufs()` walks folio buffer heads intersecting a byte range, marks them uptodate, and calls `gfs2_trans_add_data()`. Revoke removal scans `sd_log_revokes` for block numbers in the newly allocated range, removes matching revoke records, updates counters, detaches glock revoke state, frees bufdata, and releases revoke reservations.

## State And Data Structures

Transactions track requested blocks/revokes, actual new/removed metadata/data buffers, revoke count, flags such as `TR_TOUCHED`, `TR_ONSTACK`, and `TR_ATTACHED`, and per-transaction lists for data, metadata, and AIL state. Buffer heads use `b_private` for `struct gfs2_bufdata`.

## Dependencies

The file depends on GFS2 log reservation/commit/revoke APIs, glock dirty state, metadata headers, buffer head locking/pinning, folio buffers, superblock freeze state, and the VFS internal write accounting.

## Risks And Invariants

Only one transaction may exist per task through `current->journal_info`. Every mutating path must reserve enough blocks and revokes before calling add functions. Metadata buffers must have valid GFS2 magic before journaling. The log flush lock prevents inconsistent revoke accounting during flush. Adding metadata after `SB_FREEZE_COMPLETE` causes withdrawal because it violates freeze guarantees.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/trans.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/trans.h

## Scope

This header defines transaction reservation constants and declares the GFS2 transaction API.

## APIs And Definitions

- Reservation constants define one-block logical costs for dinodes, indirect blocks, journaled data, regular data, leaves, rgrp headers, rgrp bitmap work, xattrs, statfs, and quota.
- `gfs2_rg_blocks()` computes the rgrp transaction reservation for an allocation as either `requested + 1` for the rgrp header or the full rgrp bitmap/header length, whichever is smaller.
- Declarations expose transaction begin/end/free, metadata/data attachment, folio data-buffer attachment, and revoke add/remove.

## Dependencies And Invariants

`gfs2_rg_blocks()` assumes `ip->i_res.rs_rgd` is valid. Callers must combine these constants conservatively; under-reservation is caught later by transaction assertions and can trigger withdrawal. Data and metadata attachment require an active transaction in `current->journal_info`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/trans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/util.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/util.c

## Scope

This file implements global cache pointers, assertion/consistency/error reporting, spectator journal-clean checks, freeze glock helpers, and filesystem withdrawal behavior.

## Public And Internal APIs Covered

- Cache globals: `gfs2_glock_cachep`, `gfs2_glock_aspace_cachep`, `gfs2_inode_cachep`, `gfs2_bufdata_cachep`, `gfs2_rgrpd_cachep`, `gfs2_quotad_cachep`, `gfs2_qadata_cachep`, `gfs2_trans_cachep`, `gfs2_page_pool`.
- Clean/freeze helpers: `check_journal_clean()`, `gfs2_freeze_lock_shared()`, `gfs2_freeze_unlock()`.
- Withdrawal: `gfs2_withdraw()`, `gfs2_withdraw_func()`, internal `do_withdraw()`, `gfs2_offline_uevent()`.
- Diagnostics: `gfs2_lm()`, `gfs2_assert_i()`, `gfs2_assert_withdraw_i()`, `gfs2_assert_warn_i()`, `gfs2_consist_i()`, `gfs2_consist_inode_i()`, `gfs2_consist_rgrpd_i()`, metadata/type check reporters, and I/O error reporters.

## Control Flow And Behavior

`check_journal_clean()` locks a journal inode glock shared with recovery/exact/nocache flags, validates journal size/allocation, reads the journal head, and returns `-EPERM` if the journal lacks the clean unmount flag. This protects spectator mounts from becoming first mounters of dirty journals.

`gfs2_freeze_lock_shared()` and `gfs2_freeze_unlock()` manage the shared freeze glock holder used by mount/thaw paths. Errors other than try-failed are logged.

`gfs2_withdraw()` honors the configured error policy. In withdraw/deactivate modes it atomically sets `SDF_WITHDRAWN`, dumps a stack, skips work if the superblock is not born yet, logs the pending withdrawal, and schedules `sd_withdraw_work`. Panic mode panics immediately.

`gfs2_withdraw_func()` refuses to run during kill/unmount and asserts debug mode is off. It sends a `KOBJ_OFFLINE` uevent through `gfs2_offline_uevent()` so userspace can deactivate the shared block device. Depending on whether the device became inactive and whether the lock module provides `lm_unmount`, it orders lock-module unmount and `do_withdraw()` to either permit immediate remote recovery or drain local state first. Deactivate mode panics if the helper fails to deactivate the device.

`do_withdraw()` takes the log flush write lock, clears `SDF_JOURNAL_LIVE`, drains AIL transactions, wakes log/quota waiters, waits briefly for an empty log, marks the VFS superblock read-only, and dequeues pending non-system glock holders that cannot be granted after withdrawal.

Consistency helpers log fsid-qualified fatal messages and call `gfs2_withdraw()`. Inode and rgrp consistency paths also dump the relevant glock/rgrp state. Warning assertions are rate-limited by `gt_complain_secs`, can BUG in debug mode, and panic in panic error mode.

## State And Dependencies

The file manipulates `sd_flags`, `sd_log_flush_lock`, log wait queues, quota wait queues, `sd_kobj`, withdraw helper completion/status, lock module operations, freeze holder state, and tunables. It depends on GFS2 log, recovery, glock, rgrp, super, and sysfs subsystems.

## Risks And Invariants

Withdrawal must stop journal liveness before draining transactions and must prevent new write transactions. Shared block-device deactivation ordering affects cluster safety: if the device is inactive, remote recovery can begin sooner; otherwise local caches must drain before lock-module unmount. Consistency reporters must avoid duplicate noisy logging once already withdrawn. Freeze glock holder state must be initialized/uninitialized exactly once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/util.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/util.h

## Scope

This header provides GFS2 logging macros, assertion/consistency/error macros, metadata validation helpers, freeze/withdraw declarations, cache externs, and tunable access helpers.

## APIs And Definitions

- `fs_emerg`, `fs_warn`, `fs_err`, and `fs_info` prefix messages with `fsid=<sd_fsname>`.
- `gfs2_assert()` BUGs on fatal assertions; `gfs2_assert_withdraw()` logs and withdraws; `gfs2_assert_warn()` rate-limited warns and returns whether the assertion failed.
- `gfs2_consist()`, `gfs2_consist_inode()`, and `gfs2_consist_rgrpd()` wrap consistency reporting with caller location.
- `gfs2_meta_check()` checks only GFS2 magic and returns `-EIO`; `gfs2_metatype_check()` checks magic and expected metadata type and reports failures through withdrawing helpers.
- `gfs2_metatype_set()` writes type and format into a metadata header.
- I/O error macros wrap block/non-block error reporting.
- `gfs2_tune_get()` reads a tunable under `gt_spin`.
- `gfs2_withdrawn()` tests `SDF_WITHDRAWN` with an unlikely branch hint.
- Externs expose all major GFS2 slab caches and the page mempool.

## Dependencies And Invariants

The metadata helpers assume buffer data starts with `struct gfs2_meta_header`. `gfs2_tune_get()` is a snapshot and does not keep the tunable stable after return. Consistency macros are intended for serious on-disk or internal invariants; many call sites withdraw rather than attempting recovery in-place.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/xattr.c

## Scope

This file implements GFS2 extended attribute storage, lookup, list, get, set, replace, remove, and full xattr fork deallocation. It supports stuffed xattr values stored in EA blocks and unstuffed values stored in separate EA data blocks, with optional indirect EA block lists.

## Public And Internal APIs Covered

- VFS/ACL-facing APIs: `gfs2_listxattr()`, `gfs2_xattr_acl_get()`, `__gfs2_xattr_set()`, xattr handler arrays `gfs2_xattr_handlers_max` and `gfs2_xattr_handlers_min`.
- Lookup/iteration: `ea_foreach()`, `ea_foreach_i()`, `gfs2_ea_find()`, `ea_find_i()`.
- Data access: `gfs2_iter_unstuffed()`, `gfs2_ea_get_copy()`, `__gfs2_xattr_get()`, `gfs2_xattr_get()`.
- Allocation/write: `ea_alloc_blk()`, `ea_write()`, `ea_alloc_skeleton()`, `ea_init()`, `ea_set_i()`, `ea_set_simple()`, `ea_set_block()`.
- Removal/deallocation: `gfs2_xattr_remove()`, `ea_remove_stuffed()`, `ea_remove_unstuffed()`, `ea_dealloc_unstuffed()`, `ea_dealloc_indirect()`, `ea_dealloc_block()`, `gfs2_ea_dealloc()`.

## Control Flow And Behavior

Size handling starts with `ea_calc_size()` and `ea_check_size()`. Stuffed values store name and data in one EA record; unstuffed values store name plus an array of block pointers, with value bytes in `GFS2_METATYPE_ED` blocks. Type validity is format-gated: max format accepts all known types, min format only permits user/system/security.

`ea_foreach()` reads `ip->i_eattr`. If the inode does not use `GFS2_DIF_EA_INDIRECT`, it iterates a single EA block. Otherwise it validates the indirect block and walks its block pointer array, reading each EA block. `ea_foreach_i()` validates each EA block's metadata type, nonzero record length, record bounds, type validity, and final record alignment to the block end.

Lookup uses `gfs2_ea_find()` to scan for a matching type/name pair and returns a held buffer plus EA and previous-record pointers in `struct gfs2_ea_location`. `gfs2_listxattr()` locks the inode glock shared, formats recognized namespace prefixes, and either counts or copies NUL-terminated names.

Get operations lock the inode glock shared unless already held. `__gfs2_xattr_get()` checks `i_eattr`, name length, and existence. Stuffed data is copied directly; unstuffed data is copied by reading every pointed data block, validating `GFS2_METATYPE_ED`, and copying up to `sd_jbsize` payload bytes per block.

Set operations lock quota accounting and the inode glock exclusively unless already held. `__gfs2_xattr_set()` rejects immutable/append inodes, overlong names, and oversized values. A `NULL` value means remove; a zero-length non-NULL value is a real xattr value. New xattr forks are initialized by allocating an EA block, setting `ip->i_eattr`, and writing the request.

Existing forks are updated by searching for space in current EA records. `ea_set_simple()` can reuse an unused record, split slack from an existing record, remove old stuffed state, or, if the new value is unstuffed, reserve blocks/quota and allocate data blocks through `ea_alloc_skeleton()`. If no current EA block has space, `ea_set_block()` either appends a new EA block to an existing indirect block or converts a direct EA fork into an indirect block that points to the old and new EA blocks.

`ea_write()` writes header fields, name, and either stuffed data or newly allocated unstuffed data blocks. For each unstuffed block it allocates a filesystem block, removes matching revokes, creates metadata, stamps `GFS2_METATYPE_ED`, copies payload after the meta header, zero-fills tail bytes, records the block pointer, and increments inode block count.

Removal coalesces stuffed records with their predecessor when possible or marks the first record unused. Unstuffed removal frees data blocks in contiguous runs from the same rgrp, zeros data pointers, decrements inode block count, optionally coalesces the EA record, and updates ctime/dirty state. Full fork deallocation first removes all unstuffed data, then frees indirect EA blocks if present, then frees the root EA/indirect block and clears `ip->i_eattr`.

## State And Data Structures

Important structures are `gfs2_ea_header`, `gfs2_ea_request`, `gfs2_ea_location`, indirect EA pointer blocks, unstuffed EA data blocks, inode fields `i_eattr` and `i_diskflags`, inode block counts, quota reservations, and rgrp lists for multi-rgrp frees.

## Dependencies

The file depends on GFS2 glocks, meta I/O, rgrp allocation/freeing, transactions, quota lock/hold/check logic, dinode serialization, ACL code, VFS xattr handlers, and POSIX ACL/security/user/trusted namespace conventions.

## Risks And Invariants

EA record walking must reject zero-length, out-of-bounds, bad-type, and misaligned final records to avoid corrupt metadata traversal. Replacing unstuffed xattrs requires careful two-phase behavior: write the new value, then remove old unstuffed blocks. Direct-to-indirect conversion must preserve the old EA block pointer. Block and quota reservations must cover EA blocks, data blocks, rgrp metadata, statfs, and quota changes. `GFS2_DIF_APPENDONLY` prevents replacing existing xattrs even if VFS append state checks passed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/xattr.h

## Scope

This header defines GFS2 extended attribute layout macros, request/location helper structures, and exported xattr functions.

## APIs And Definitions

- Length and layout macros: `GFS2_EA_REC_LEN()`, `GFS2_EA_DATA_LEN()`, `GFS2_EA_SIZE()`, `GFS2_EA_IS_STUFFED()`, `GFS2_EA_IS_LAST()`, `GFS2_EAREQ_SIZE_STUFFED()`.
- Pointer macros map an EA header to name bytes, stuffed data bytes, unstuffed data pointer array, next record, and first EA record in a buffer.
- `struct gfs2_ea_request` carries type, name, value pointer, and lengths for set/write paths.
- `struct gfs2_ea_location` returns the containing buffer, matching EA record, and previous EA record.
- Exports: `__gfs2_xattr_set()`, `gfs2_listxattr()`, `gfs2_ea_dealloc()`, and ACL helper `gfs2_xattr_acl_get()`.

## Invariants

The layout macros assume validated on-disk EA headers and big-endian length fields. Callers must hold the appropriate inode glock for reading or writing EA blocks. Unstuffed pointer arrays start after the name rounded to an 8-byte boundary.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/hfs/Kconfig

## Scope

This Kconfig file declares the Linux HFS filesystem driver and its optional KUnit tests.

## Options

- `HFS_FS` is a tristate "Apple Macintosh file system support" option. It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. As a module, it builds as `hfs`.
- Help text states that enabling it permits mounting Macintosh-formatted floppy disks and hard drive partitions with full read-write access and points to `Documentation/filesystems/hfs.rst` for mount options.
- `HFS_KUNIT_TEST` is a tristate KUnit test option, depends on `HFS_FS && KUNIT`, defaults to `KUNIT_ALL_TESTS`, and is intended for kernel developer test harnesses rather than production builds.

## Invariants

The filesystem driver assumes block-device support and old buffer-head/direct-I/O infrastructure. KUnit tests are only selectable when both HFS and KUnit are available.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/hfs/Makefile

## Scope

This Makefile defines the object composition for the Linux HFS filesystem module/built-in target and its KUnit test target.

## Build Rules

- `obj-$(CONFIG_HFS_FS) += hfs.o` builds the aggregate HFS object when the filesystem is enabled.
- `hfs-objs` includes bitmap, B-tree find/node/record/tree, catalog, directory, extent, inode, attr, MDB, partition table, string, super, sysdep, and transaction objects.
- `obj-$(CONFIG_HFS_KUNIT_TEST) += string_test.o` builds the string KUnit tests when configured.

## Dependencies

The object list shows that the files in this group (`attr.c`, `bfind.c`, `bitmap.c`, `bnode.c`) are core components of the single `hfs.o` target.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/attr.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/attr.c

## Scope

This file exposes classic HFS Finder metadata fields as Linux extended attributes. It supports `hfs.creator` and `hfs.type` for regular data-fork files.

## Public And Internal APIs Covered

- Internal helpers: `__hfs_setxattr()` and `__hfs_getxattr()`.
- VFS handler callbacks: `hfs_xattr_get()` and `hfs_xattr_set()`.
- Handler table: `hfs_xattr_handlers`.

## Control Flow And Behavior

Both get and set reject non-regular files and resource-fork inodes with `-EOPNOTSUPP`. Set initializes a catalog B-tree search, copies the inode catalog key into the search key, finds the matching catalog record, reads a `struct hfs_cat_file`, and updates either `UsrWds.fdType` or `UsrWds.fdCreator` if the supplied value is exactly four bytes. Successful updates write the catalog record back to the B-tree node.

Get returns a size of four when called with size zero. When a buffer is supplied, it performs the same catalog lookup and copies the requested four-byte field if the buffer is large enough, otherwise returns `-ERANGE`.

The public xattr set callback does not support removal: `value == NULL` returns `-EOPNOTSUPP`. Handler flags encode whether the request is for type or creator.

## Dependencies

The file depends on HFS inode private state, catalog B-tree records, `hfs_find_init()`, `hfs_brec_find()`, `hfs_bnode_read()`, `hfs_bnode_write()`, and Linux xattr handler infrastructure.

## Risks And Invariants

The xattr values are fixed-width four-byte Finder fields, not arbitrary strings. The code assumes catalog records found by the inode catalog key are file records of at least `struct hfs_cat_file` size. All B-tree search resources are released with `hfs_find_exit()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/bfind.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/bfind.c

## Scope

This file implements HFS B-tree search cursor setup/teardown, binary search within a node, root-to-leaf traversal, record reading, and cursor movement across leaf nodes.

## Public And Internal APIs Covered

- `hfs_find_init()` allocates search/key buffers and locks the appropriate B-tree mutex subclass.
- `hfs_find_exit()` releases the current node, frees search buffers, and unlocks the tree.
- `__hfs_brec_find()` binary-searches one node for the best record not greater than the search key.
- `hfs_brec_find()` traverses from the root down index nodes to a leaf.
- `hfs_brec_read()` finds and reads a record body.
- `hfs_brec_goto()` moves the cursor by record count, crossing previous/next leaf links.

## Control Flow And Behavior

`hfs_find_init()` rejects null inputs, allocates enough memory for search and result keys, stores two key buffers in one allocation, logs the caller, and locks the catalog, extents, or attributes tree with a lockdep subclass based on CNID. Unknown tree CNIDs return `-EINVAL`.

`__hfs_brec_find()` performs a binary search over node records using `hfs_brec_lenoff()`, `hfs_brec_keylen()`, `hfs_bnode_read()`, and the tree's key comparator. It records the selected record number, key offset/length, entry offset, and entry length. It returns `0` for exact matches, `-ENOENT` for best-less-than-only results, and `-EINVAL` for zero-length keys.

`hfs_brec_find()` clears cursor offsets, starts at `tree->root`, and walks `tree->depth` levels. Each node is loaded with `hfs_bnode_find()`, checked for expected height and type, assigned a parent, and searched. Index entries provide the next child node number. On invalid height/type or unusable index result it releases the node and returns an error.

`hfs_brec_goto()` moves relative to the current record. Negative movement walks `prev` leaf links; positive movement walks `next` links. It then refreshes offsets and reads the current key into `fd->key`.

## Dependencies

This file depends on HFS B-tree structures, node cache/loading, record layout helpers, key comparators, and per-tree mutexes.

## Risks And Invariants

The caller must pair `hfs_find_init()` with `hfs_find_exit()`. The tree lock protects the cursor and B-tree shape during traversal. Node validation enforces expected type/height by depth, but record length/key validation is limited to the helpers and zero-key checks. `hfs_brec_find()` returns `-ENOENT` even with a valid best-fit cursor, so callers must distinguish exact-match needs from traversal needs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/bfind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/bitmap.c

## Scope

This file implements allocation and free operations for the HFS volume bitmap.

## Public And Internal APIs Covered

- Internal `hfs_find_set_zero_bits()` searches the big-endian bitmap for zero bits and sets the contiguous run it finds.
- `hfs_vbm_search_free()` allocates allocation blocks from the volume bitmap.
- `hfs_clear_vbm_bits()` frees allocation blocks in the volume bitmap.

## Control Flow And Behavior

`hfs_find_set_zero_bits()` starts from an offset, scans big-endian 32-bit words for the first clear bit in HFS left-to-right bit order, then sets bits up to the requested maximum or until it encounters an already-set bit. It updates `*max` to the number of bits actually set and returns the starting bit, or a value at/above size when no zero bit is found.

`hfs_vbm_search_free()` rejects zero-length requests, locks `bitmap_lock`, searches from the supplied goal to the end of the filesystem allocation-block range, wraps to zero if needed, and returns zero length/start when full. On success it decrements `free_ablocks`, marks the bitmap dirty, unlocks, and returns the starting allocation block.

`hfs_clear_vbm_bits()` validates nonzero work and range bounds, locks the bitmap, clears partial leading bits, full 32-bit words, and trailing bits, increments `free_ablocks`, unlocks, and marks the bitmap dirty.

## Dependencies

The file depends on `HFS_SB(sb)->bitmap`, `bitmap_lock`, `fs_ablocks`, `free_ablocks`, `hfs_bitmap_dirty()`, and big-endian bitmap storage.

## Risks And Invariants

The allocation helper both finds and sets bits; callers must hold/expect bitmap mutation. Its comments note it may read beyond the logical bit count within aligned memory. `hfs_clear_vbm_bits()` does not verify that bits were previously set despite historical comments mentioning already-clear detection; it simply clears and increments free count, so callers must not double-free ranges. Bitmap dirtying is required after every successful mutation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/bnode.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/bnode.c

## Scope

This file implements basic HFS B-tree node I/O, validation, cache/hash management, reference counting, creation, unlinking, and deletion cleanup.

## Public And Internal APIs Covered

- Bounds helpers: `is_bnode_offset_valid()`, `check_and_correct_requested_length()`.
- Node data access: `hfs_bnode_read()`, `hfs_bnode_read_u16()`, `hfs_bnode_read_u8()`, `hfs_bnode_read_key()`, `hfs_bnode_write()`, `hfs_bnode_write_u16()`, `hfs_bnode_write_u8()`, `hfs_bnode_clear()`, `hfs_bnode_copy()`, `hfs_bnode_move()`.
- Diagnostics/linking: `hfs_bnode_dump()`, `hfs_bnode_unlink()`.
- Cache/lifecycle: `hfs_bnode_findhash()`, `hfs_bnode_unhash()`, `hfs_bnode_find()`, `hfs_bnode_create()`, `hfs_bnode_get()`, `hfs_bnode_put()`, `hfs_bnode_free()`.

## Control Flow And Behavior

All explicit node offset operations first validate that the starting offset is within `tree->node_size`; overlong requests are truncated with an error log. Reads can span pages in `node->page[]`, honoring `page_offset` and `pages_per_bnode`. Writes, clears, copies, and moves operate on mapped page data and mark destination pages dirty. Key reads use variable key length for leaf or variable-index-key trees, otherwise fixed maximum key length, and reject impossible key lengths by zeroing the destination key.

`hfs_bnode_unlink()` updates previous and next sibling descriptors, adjusts tree leaf head/tail for leaf nodes, clears the tree root/depth if unlinking the root, and marks the node deleted. Actual bitmap freeing is deferred until the final `hfs_bnode_put()`.

The node cache is a hash table keyed by node id. `__hfs_bnode_create()` allocates a variable-sized `hfs_bnode`, inserts it into the hash under `hash_lock` unless another thread won the race, initializes refcount/waitqueue, reads the node's pages from the B-tree inode mapping, and leaves `HFS_BNODE_NEW` set until validation completes. Racing finders wait on `lock_wq` for `HFS_BNODE_NEW` to clear.

`hfs_bnode_find()` first checks the hash, otherwise creates a node, reads the descriptor, validates node type/height against tree depth, validates record offset table monotonicity/range/alignment, and validates index/leaf key sizes against entry sizes. On success it clears `HFS_BNODE_NEW` and wakes waiters. On failure it sets `HFS_BNODE_ERROR`, wakes waiters, drops the node, and returns `-EIO`.

`hfs_bnode_create()` creates a new zeroed node, dirties all pages covering it, clears the new flag, and wakes waiters. `hfs_bnode_put()` decrements the refcount under the tree hash lock; final deleted nodes are unhashed, cleared on disk, released from the B-tree node bitmap with `hfs_bmap_free()`, and freed.

## State And Data Structures

Nodes track tree pointer, node id, flags (`HFS_BNODE_NEW`, `ERROR`, `DELETED`), refcount, waitqueue, sibling ids, parent id, node type/height, record count, page offset, page array, and hash linkage. Trees provide node size/count, depth, pages-per-node, inode mapping, hash table, and leaf head/tail.

## Dependencies

The file depends on Linux page cache APIs, page copying/zeroing/mapping helpers, HFS B-tree record layout, B-tree bitmap freeing, hash locking, and node flags.

## Risks And Invariants

Offset correction prevents out-of-bounds memory access but can mask higher-level corrupt length calculations after logging. Multi-page reads are supported, but several mutation helpers operate on `page[0]` and rely on node sizes/page offsets used by HFS. Node validation must complete before waiters use a new node. Deleted nodes are only physically freed when their refcount reaches zero, preserving cache safety during B-tree modifications.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/bnode.c -->