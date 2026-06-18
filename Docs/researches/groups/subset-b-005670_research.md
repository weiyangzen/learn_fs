# subset-b-005670 research

Grouped research for GFS2 resource groups, superblock/sysfs/transaction/util/xattr support, GFS2 tracepoints, and HFS B-tree/bitmap/xattr files. Each section preserves the original source path for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/rgrp.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/rgrp.c

## Purpose
`rgrp.c` implements GFS2 resource group discovery, bitmap interpretation, block allocation, block freeing, multi-block reservations, rindex refresh, FITRIM/discard, and resource-group consistency checks. It is the allocator core for data, metadata, dinodes, xattr blocks, and inode deletion cleanup.

## Important APIs, Types, And Functions
The internal `struct gfs2_rbm` identifies a bitmap position by resource group, bitmap-block index, and bitmap-relative offset. `struct gfs2_extent` records the best candidate free extent during scanning. Exported entry points include `gfs2_rindex_update`, `gfs2_blk2rgrpd`, `gfs2_rgrp_go_instantiate`, `gfs2_inplace_reserve`, `gfs2_alloc_blocks`, `__gfs2_free_blocks`, `gfs2_free_meta`, `gfs2_unlink_di`, `gfs2_free_di`, `gfs2_check_blk_type`, `gfs2_rlist_*`, `gfs2_rgrp_send_discards`, and `gfs2_fitrim`.

The bitmap helpers `gfs2_setbit`, `gfs2_testbit`, `gfs2_bit_search`, `gfs2_bitfit`, `gfs2_rbm_from_block`, `gfs2_rbm_add`, and `gfs2_rbm_find` translate between on-disk two-bit block states and filesystem block numbers. Reservation helpers (`rs_cmp`, `rs_insert`, `gfs2_rs_deltree`, `rg_mblk_search`, `gfs2_reservation_check_and_update`) maintain an rbtree of reserved block ranges per resource group.

## Control Flow
Resource groups are discovered by reading the rindex inode through `gfs2_rindex_update` -> `gfs2_ri_update` -> `read_rindex_entry`. Each entry allocates a `gfs2_rgrpd`, computes per-bitmap-block descriptors, obtains an rgrp glock, and inserts the descriptor into `sd_rindex_tree`. `set_rgrp_preferences` spreads preferred rgrps across journals to reduce cluster lock contention.

Allocation starts with `gfs2_inplace_reserve`. It chooses a starting rgrp from the inode goal or existing reservation, skips busy or non-preferred groups in early passes, acquires the rgrp glock, optionally refreshes from the lock value block, searches or creates a reservation, reclaims unlinked dinodes if needed, and falls back to `min_target` after log flush. `gfs2_alloc_blocks` then searches the reservation or rgrp bitmap, updates bitmap bits, reservation accounting, rgrp header/LVB, statfs, quota, inode goal, and revoke state.

Freeing uses `rgblk_free` to clone bitmap bytes before modifying states, then updates rgrp counts and journal state through `__gfs2_free_blocks`, `gfs2_free_meta`, `gfs2_unlink_di`, and `gfs2_free_di`. FITRIM walks rgrps under exclusive rgrp glocks, sends discards for free extents, and marks rgrps trimmed in a transaction.

## State And Persistence
Persistent state is in rindex entries, rgrp header blocks, rgrp bitmap blocks, and optionally rgrp LVBs. In-memory state includes `sd_rindex_tree`, `rd_bits`, `rd_free`, `rd_free_clone`, `rd_reserved`, `rd_requested`, `rd_rstree`, `rd_extfail_pt`, `rd_last_alloc`, and flags such as `GFS2_RDF_CHECK`, `GFS2_RGF_TRIMMED`, and `GFS2_RDF_ERROR`. Bitmap clone buffers delay reuse of newly freed blocks until the clone is discarded. All on-disk rgrp/bitmap updates are added to GFS2 transactions before mutation.

## Dependencies And Integration Points
This file is tightly coupled to glocks (`glock.h`, `glops.h`), metadata I/O, transactions, logging/revokes, quota, statfs, inode update paths, directory delete verification, tracepoints, and Linux block discard APIs. xattr and file deallocation paths rely on `gfs2_rlist_*`, `gfs2_inplace_reserve`, `gfs2_alloc_blocks`, and `gfs2_free_meta`.

## Risks And Edge Cases
Important risks are bitmap/rgrp count divergence, reservation-tree overlap, allocation under stale LVB state, wraparound in bitmap scans, rindex growth races, discard errors disabling mount-time discard, and unlinked dinode cleanup racing with inode cache state. Error paths often mark the rgrp readonly until unmount or withdraw the filesystem, so false positives are high-impact but protect metadata integrity.

## Test Signals
Useful signals include allocation/free tracepoints (`gfs2_block_alloc`, `gfs2_rs`), statfs consistency after allocations and frees, fsck clean runs after stress, FITRIM return ranges, ENOSPC behavior with fragmented rgrps, xfstests covering unlink/recreate and quota accounting, and multi-node allocation contention tests with rgrp LVB enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/rgrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/rgrp.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/rgrp.h

## Purpose
`rgrp.h` declares the GFS2 resource-group allocator interface used by inode, bmap, xattr, superblock, recovery, and debug code. It also defines reservation sizing constants and the small helper type for multi-rgrp lock acquisition.

## Important APIs, Types, And Functions
`RGRP_RSRV_MINBLKS` and `RGRP_RSRV_ADDBLKS` tune minimum and growth sizes for multi-block reservations. The header exports rgrp lookup and lifecycle helpers (`gfs2_blk2rgrpd`, `gfs2_rgrpd_get_first`, `gfs2_rgrpd_get_next`, `gfs2_clear_rgrpd`, `gfs2_rindex_update`, `gfs2_rgrp_go_instantiate`, `gfs2_rgrp_brelse`) and allocator APIs (`gfs2_inplace_reserve`, `gfs2_inplace_release`, `gfs2_alloc_blocks`, `gfs2_free_meta`, `__gfs2_free_blocks`, `gfs2_free_di`, `gfs2_unlink_di`).

`struct gfs2_rgrp_list` packages an array of `gfs2_rgrpd *` and matching glock holders so callers can collect all rgrps touched by a multi-block operation, allocate holders, lock them together, then free the list.

## Control Flow And State
Callers typically refresh the rindex, locate rgrps, reserve space, begin a transaction, allocate or free, and release the reservation. The inline `gfs2_rs_active` tests whether an inode reservation is linked into a resource-group reservation tree. `rgrp_contains_block` provides the basic address-range predicate used throughout allocation and validation.

## Dependencies And Integration Points
The declarations depend on GFS2 in-core structures and Linux slab/uaccess headers. This header is consumed by file/block mapping, inode creation/deletion, xattr storage, superblock statfs, and debug dump code.

## Risks And Test Signals
Because this header exposes low-level allocation primitives, misuse risks include allocating without an active reservation, freeing outside a single rgrp, or assuming a reservation is active without checking its rbtree node. Compile coverage should catch signature drift; runtime signals come from rgrp consistency checks, tracepoint output, and stress tests around ENOSPC, unlink, and xattr block allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/rgrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/super.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/super.c

## Purpose
`super.c` supplies GFS2 superblock operations and mount-state transitions: journal descriptor management, read-write activation, statfs accounting, freeze/thaw, sync, inode eviction, writeback integration, mount option display, and unmount cleanup.

## Important APIs, Types, And Functions
Key exported helpers are `gfs2_jindex_free`, `gfs2_jdesc_find`, `gfs2_jdesc_check`, `gfs2_make_fs_rw`, `gfs2_make_fs_ro`, `gfs2_statfs_init`, `gfs2_statfs_change`, `update_statfs`, `gfs2_statfs_sync`, `gfs2_freeze_func`, `free_local_statfs_inodes`, and `find_local_statfs_inode`. The VFS-facing `gfs2_super_ops` wires in `.alloc_inode`, `.free_inode`, `.write_inode`, `.dirty_inode`, `.evict_inode`, `.put_super`, `.sync_fs`, `.freeze_super`, `.freeze_fs`, `.thaw_super`, `.statfs`, `.drop_inode`, and `.show_options`.

`enum evict_behavior` describes whether an evicted inode should be deleted locally, skipped, or deferred. The file also serializes dinode fields with `gfs2_dinode_out`.

## Control Flow
Read-write activation invalidates the local journal glock, verifies journal sequence knowledge, initializes quota, and sets `SDF_JOURNAL_LIVE`. Read-only transition flushes delete work, destroys daemon threads, syncs quota/statfs, performs two log flushes to commit metadata and revokes, waits for log empty, and cleans quota.

Statfs has a fast path that combines master and local statfs deltas under `sd_statfs_spin`, plus a slow path that asynchronously locks rgrps and totals verified rgrp counts. Syncing statfs locks the master statfs inode, starts a transaction, folds local deltas into master, and clears the local buffer.

Freeze first freezes the VFS, then obtains journal locks and the freeze glock to verify all journals have clean unmount headers. Thaw reacquires the shared freeze glock and calls VFS thaw. Inode eviction distinguishes linked inodes from unlinked dinodes, verifies bitmap type before reading deleted dinodes, upgrades iopen glocks when this node is final opener, and deallocates xattrs, file blocks, exhash directories, and dinode blocks.

## State And Persistence
Persistent state includes journal index inodes, local/master statfs files, dinodes, quota changes, and journal log contents. Important flags are `SDF_JOURNAL_LIVE`, `SDF_NORECOVERY`, `SDF_FROZEN`, `SDF_FREEZE_INITIATOR`, `SDF_KILL`, and `SDF_EVICTING`. Eviction updates on-disk dinodes, writes back glock metadata address spaces, and records deleted inode formal numbers to avoid stale lookups.

## Dependencies And Integration Points
This file integrates VFS superblock operations, GFS2 glocks, journaling, quota, rgrp, xattr deallocation, directory deallocation, recovery, sysfs cleanup, and debugfs. It relies on freeze glocks for cluster-wide freeze semantics and on journal glocks to avoid freezing over dirty recoverable journals.

## Risks And Test Signals
High-risk paths include unmount while recovery is active, freeze retries during journal recovery, evicting unlinked inodes under memory pressure, journal-live races during withdrawal, and statfs divergence between local and master files. Signals include xfstests freeze/thaw and unlink tests, multi-node recovery tests, dirty inode writeback under journaled-data mode, statfs slow/fast comparisons, and clean unmount log headers after remount read-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/super.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/super.h

## Purpose
`super.h` is the public header for GFS2 superblock helpers and VFS operation tables. It defines supported on-disk filesystem format bounds and exposes lifecycle, journal, statfs, freeze, and teardown functions to the rest of GFS2.

## Important APIs, Types, And Functions
`GFS2_FS_FORMAT_MIN` and `GFS2_FS_FORMAT_MAX` gate on-disk format compatibility. `gfs2_jindex_size` reads `sd_journals` under `sd_jindex_spin`. Other declarations cover journal descriptor lookup/check/free, master-directory lookup, read-write/read-only transitions, online uevents, thread teardown, statfs conversion and sync, freeze work, local statfs inode lookup/free, and `free_sbd`.

The header exports `gfs2_fs_type`, `gfs2meta_fs_type`, `gfs2_export_ops`, `gfs2_super_ops`, `gfs2_dops`, and xattr handler arrays for minimum and maximum format variants.

## Control Flow And State
Callers use these functions during mount, remount, unmount, statfs, journal recovery, and VFS operation dispatch. State protected through these APIs includes journal lists, statfs deltas, per-node local statfs inodes, the live journal bit, and superblock-private lifecycle resources.

## Dependencies And Integration Points
The header includes Linux VFS/dcache types and GFS2 `incore.h`. It is included by mount code, xattr handling, sysfs, rgrp, util, and other filesystem subsystems needing superblock-level operations.

## Risks And Test Signals
The main risk is contract drift between prototypes and `super.c` or callers, especially around statfs and format-dependent xattr handlers. Build coverage, mount/remount tests, statfs tests, and xattr tests across minimum and maximum GFS2 formats are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/super.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/sys.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/sys.c

## Purpose
`sys.c` implements the `/sys/fs/gfs2/<locktable>/` interface and per-filesystem kobject lifecycle. It exposes read-only status, administrative controls, lock-module controls, recovery triggers, and tunables.

## Important APIs, Types, And Functions
`struct gfs2_attr` wraps a sysfs attribute with GFS2-specific show/store callbacks. The exported functions are `gfs2_sys_fs_add`, `gfs2_sys_fs_del`, `gfs2_sys_init`, `gfs2_sys_uninit`, and `gfs2_recover_set`.

Top-level attributes include `id`, `fsname`, `uuid`, `freeze`, `withdraw`, `statfs_sync`, `quota_sync`, quota refresh controls, `demote_rq`, and `status`. `lock_module` attributes expose protocol name, lock blocking, withdraw-helper status, journal id assignment, first-mount coordination, and recovery control. `tune` attributes update quota, statfs, readahead, warning, new-files-jdata, and withdraw-helper timeout fields.

## Control Flow
All sysfs reads and writes dispatch through `gfs2_attr_show` and `gfs2_attr_store`, converting the kobject back to `struct gfs2_sbd`. `gfs2_sys_fs_add` initializes the kobject, creates default, tune, and lock-module groups, links the block device, and emits `KOBJ_ADD` with readonly and spectator environment variables. Deletion removes the link/groups, drops the kobject, and waits for release completion.

Administrative store handlers parse simple numeric commands, require `CAP_SYS_ADMIN` for mutation where needed, and call into freeze/thaw, withdraw, statfs, quota, glock demotion, and recovery code. `gfs2_recover_set` waits for the local journal to be ready, rejects recovery of the active non-spectator journal, locates a target journal descriptor, and queues recovery.

## State And Persistence
Most state is in-memory mount state: `sd_flags`, lockstruct fields, tune fields, journal id, completion objects, and log counters. Store operations can cause persistent effects indirectly by freezing, syncing quota/statfs, recovering journals, or withdrawing the filesystem. Kobject state persists only for the lifetime of the mounted filesystem.

## Dependencies And Integration Points
The sysfs layer integrates GFS2 with udev, lock managers, quota, recovery, glocks, freeze/thaw, and withdrawal helpers. `gfs2_uevent` adds locktable, lockproto, journal id, and UUID variables to kobject events.

## Risks And Test Signals
Risks include incorrect capability checks, accepting invalid tunable values, racing journal id assignment with lock initialization, recovery attempts during shutdown, and kobject cleanup leaks on partial setup failure. Test signals include sysfs permission/parse tests, manual recovery trigger tests, freeze/withdraw sysfs tests, uevent content, and lock-module coordination in clustered mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/sys.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/sys.h

## Purpose
`sys.h` declares the small public surface for GFS2 sysfs integration and journal recovery triggering.

## Important APIs
`gfs2_sys_fs_add` and `gfs2_sys_fs_del` attach and detach per-mount sysfs kobjects. `gfs2_sys_init` and `gfs2_sys_uninit` create and destroy the global `gfs2` kset under `fs_kobj`. `gfs2_recover_set` starts recovery for a requested journal id.

## Control Flow And State
Module initialization calls `gfs2_sys_init`; each mount calls `gfs2_sys_fs_add` after enough superblock state exists for sysfs exposure; unmount calls `gfs2_sys_fs_del`; module exit calls `gfs2_sys_uninit`. Recovery callers can use `gfs2_recover_set` without knowing the sysfs parser details.

## Dependencies And Integration Points
The header forward-declares `struct gfs2_sbd` and includes spinlock support because the implementation coordinates with superblock and lockstruct state. It is consumed by mount, superblock teardown, and sysfs-related recovery code.

## Risks And Test Signals
Risks are mostly lifecycle ordering errors, such as deleting a sysfs object before attributes are removed or exposing sysfs before required superblock fields are initialized. Signals are clean mount/unmount cycles, sysfs file presence, recovery trigger behavior, and absence of kobject reference warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/trace_gfs2.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/trace_gfs2.h

## Purpose
`trace_gfs2.h` defines Linux tracepoints for GFS2 glock state, log/journal activity, block mapping, iomap operations, block allocation, and resource reservations. It gives runtime observability for allocator, locking, and log behavior without adding ad hoc logging.

## Important APIs, Types, And Events
The file sets `TRACE_SYSTEM gfs2`, declares symbolic printers for DLM lock states, GFS2 block states, reservation actions, and glock flags, and maps GFS2 lock states to DLM trace values through `glock_trace_state`.

Trace events include `gfs2_glock_state_change`, `gfs2_glock_put`, `gfs2_demote_rq`, `gfs2_promote`, `gfs2_glock_queue`, `gfs2_glock_lock_time`, `gfs2_pin`, `gfs2_log_flush`, `gfs2_log_blocks`, `gfs2_ail_flush`, `gfs2_bmap`, `gfs2_iomap_start`, `gfs2_iomap_end`, `gfs2_block_alloc`, and `gfs2_rs`.

## Control Flow And State Captured
Lock events capture device, glock type/number, current/target/demote states, queue direction, DLM status, and timing statistics. Log events capture pin/unpin, flush start/end, log sequence, reservation counts, and AIL writeback. Mapping events capture inode, logical/physical blocks, iomap range/type/flags, and return codes. Allocator events capture rgrp address, free clone count, requested/reserved counts, allocation state, and reservation range.

## Dependencies And Integration Points
The header includes Linux tracepoint infrastructure plus GFS2 in-core, glock, and rgrp definitions. It must remain in sync with fields used in `glock.c`, `log.c`, `bmap.c`, `rgrp.c`, transaction code, and writeback code. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` inclusion support kernel trace generation.

## Risks And Test Signals
Risks include dereferencing unstable glock/rgrp fields in trace fast paths, format drift that breaks trace consumers, and compile issues when structures change. Signals include successful kernel tracepoint generation, `tracefs` event availability, allocator stress runs showing coherent `gfs2_block_alloc` and `gfs2_rs` sequences, and lock contention tests producing `gfs2_glock_lock_time` data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/trace_gfs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/trans.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/trans.c

## Purpose
`trans.c` implements GFS2 transaction begin/end, metadata and journaled-data buffer attachment, revoke addition/removal, and transaction object cleanup. It is the bridge between higher-level filesystem mutations and the GFS2 log.

## Important APIs, Types, And Functions
`__gfs2_trans_begin` initializes a caller-provided transaction and reserves log space and revokes. `gfs2_trans_begin` allocates a transaction from `gfs2_trans_cachep`. `gfs2_trans_end` releases unused reservations or commits touched transactions. `gfs2_trans_add_data`, `gfs2_trans_add_databufs`, and `gfs2_trans_add_meta` attach buffers to transaction lists. `gfs2_trans_add_revoke`, `gfs2_trans_remove_revoke`, and `gfs2_trans_free` manage revoke state and final cleanup.

## Control Flow
Transaction begin rejects nesting through `current->journal_info`, rejects zero-work transactions, fails with `-EROFS` when withdrawn or journal-live is false, calculates reserved log blocks, starts an internal write, then reserves log blocks and revokes under `sd_log_flush_lock`. If fast reservation fails, it does a full reservation outside the read lock and then rechecks journal liveness.

Adding a metadata buffer allocates or reuses `gfs2_bufdata`, validates the metadata magic, checks withdrawn/frozen state, pins the buffer, stamps the journal id, marks the glock dirty, and links the buffer into the transaction. Journaled data follows a similar flow but links into `tr_databuf`. Transaction end releases unused revokes, validates that touched buffers and revokes fit the requested credits, commits through `gfs2_log_commit`, releases the flush lock, optionally flushes synchronous mounts, and ends the internal write.

## State And Persistence
State is held in `current->journal_info`, `struct gfs2_trans` lists and counters, buffer private `gfs2_bufdata`, glock flags `GLF_LFLUSH`/`GLF_DIRTY`, log reservation counters, and the on-disk journal after commit. Untouched transactions release their reservations without log commit.

## Dependencies And Integration Points
This file depends on GFS2 log reservation/commit APIs, metadata I/O, glocks, buffer heads, folios, revokes, and withdrawal helpers. All metadata mutators in rgrp, xattr, superblock, inode, quota, and directory code depend on these routines.

## Risks And Test Signals
Risks include incorrect credit estimates, missing `gfs2_trans_add_meta` before mutation, stale revoke removal when reusing blocks, nested transaction bugs, and mutations while frozen or withdrawn. Signals include assertion output from `gfs2_print_trans`, log flush tracepoints, xfstests journal replay coverage, synchronous mount behavior, and fsck after crash/recovery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/trans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/trans.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/trans.h

## Purpose
`trans.h` declares the GFS2 transaction API and common log credit constants used across metadata mutators.

## Important APIs And Constants
Credit constants such as `RES_DINODE`, `RES_INDIRECT`, `RES_RG_HDR`, `RES_RG_BIT`, `RES_EATTR`, `RES_STATFS`, and `RES_QUOTA` give callers shared accounting units. `gfs2_rg_blocks` returns the rgrp bitmap/header credit needed for a request, capped by the current rgrp length. Transaction APIs cover begin/end, adding data and metadata buffers, adding/removing revokes, and freeing transaction objects.

## Control Flow And State
Callers reserve credits before mutating metadata, add every changed buffer to the active transaction, and end the transaction to commit or release log reservations. `gfs2_rg_blocks` depends on `ip->i_res.rs_rgd`, so it is only valid after in-place reservation has selected a resource group.

## Dependencies And Integration Points
The header depends on buffer heads and GFS2 in-core transaction, rgrp, inode, glock, and bufdata types. It is included by rgrp, xattr, superblock, inode, quota, and directory code.

## Risks And Test Signals
The central risk is under-reserving log credits, which may trigger transaction assertions or forced withdraws. Compile coverage catches signature drift; runtime coverage comes from metadata-heavy tests, xattr allocation/deallocation, rgrp allocation, quota updates, and crash replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/trans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/util.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/util.c

## Purpose
`util.c` provides GFS2 global caches, assertion/consistency reporting, freeze-glock helpers, journal-clean checking, I/O error handling, and filesystem withdrawal orchestration.

## Important APIs, Types, And Functions
The file defines global slab caches for glocks, inodes, bufdata, rgrps, quota data, and transactions, plus `gfs2_page_pool`. Exported helpers include `gfs2_assert_i`, `check_journal_clean`, `gfs2_freeze_lock_shared`, `gfs2_freeze_unlock`, `gfs2_lm`, `gfs2_withdraw_func`, `gfs2_withdraw`, `gfs2_assert_withdraw_i`, `gfs2_assert_warn_i`, `gfs2_consist_i`, `gfs2_consist_inode_i`, `gfs2_consist_rgrpd_i`, `gfs2_meta_check_ii`, `gfs2_metatype_check_ii`, `gfs2_io_error_i`, and `gfs2_io_error_bh_i`.

## Control Flow
`check_journal_clean` locks a journal inode glock in shared recovery-aware mode, validates the journal descriptor, finds the journal head, and requires an unmount log header for spectator safety. Freeze helpers acquire and release the shared freeze glock.

Withdrawal starts in `gfs2_withdraw`, which honors mount error policy: withdraw/deactivate schedules async work once, panic policy panics. `gfs2_withdraw_func` optionally emits an offline uevent and waits for `gfs2_withdraw_helper` status, then orders lock-manager unmount relative to local cache drain depending on whether the block device was deactivated. `do_withdraw` clears `SDF_JOURNAL_LIVE`, drains AIL transactions, wakes log/quota waiters, waits briefly for the log to empty, marks the VFS superblock read-only, and dequeues glock holders that can no longer complete.

## State And Persistence
The file modifies `sd_flags` (`SDF_WITHDRAWN`, `SDF_JOURNAL_LIVE`), `s_flags` (`SB_RDONLY`), withdraw-helper status/completion, log wait queues, and lock-manager state. It does not directly write normal filesystem metadata, but withdrawal controls whether future writes can happen and whether remote recovery can proceed.

## Dependencies And Integration Points
It integrates with glocks, log/AIL, recovery, rgrp dump, superblock journal checks, sysfs uevents, lock managers, quota waiters, and kernel panic/BUG policy. The consistency helpers are called from most metadata validation paths.

## Risks And Test Signals
Risks include deadlock during withdrawal, helper timeout policy errors, duplicate withdrawal work, missed read-only transition, and over-aggressive BUG/panic behavior under debug or panic-on-error settings. Signals include forced I/O error tests, withdraw sysfs tests, spectator dirty-journal rejection, cluster recovery after offline uevent success/failure, and absence of hung log/quota waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/util.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/util.h

## Purpose
`util.h` declares GFS2 utility, consistency, metadata validation, freeze, withdrawal, cache, and tune-access helpers. It centralizes error-reporting macros that include the filesystem id.

## Important APIs, Types, And Macros
Logging macros `fs_emerg`, `fs_warn`, `fs_err`, and `fs_info` prefix messages with `sd_fsname`. Assertion wrappers include `gfs2_assert`, `gfs2_assert_withdraw`, and `gfs2_assert_warn`. Consistency macros wrap inode, rgrp, and superblock consistency functions with call-site information.

Inline metadata validators `gfs2_meta_check` and `gfs2_metatype_check_i` check GFS2 magic and expected metadata type. `gfs2_metatype_set` initializes metadata headers. The header also declares journal-clean checks, freeze lock helpers, I/O error helpers, slab caches, the page mempool, `gfs2_tune_get`, `gfs2_withdrawn`, `gfs2_lm`, `gfs2_withdraw_func`, and `gfs2_withdraw`.

## Control Flow And State
Callers use these macros in hot metadata paths to fail fast on corrupt headers or impossible state. `gfs2_tune_get` serializes tune reads under the tune spinlock. `gfs2_withdrawn` checks `SDF_WITHDRAWN` as a fast guard before work that cannot proceed on a withdrawn filesystem.

## Dependencies And Integration Points
The header depends on Linux mempool and GFS2 `incore.h`. It is included by most GFS2 implementation files, so it is part of the core error-handling contract.

## Risks And Test Signals
Risks include inconsistent error policy, missing call-site information, metadata checks with wrong expected type, and cache declaration drift. Signals are compile coverage, metadata corruption injection, debug mount behavior, panic/withdraw policy tests, and journal-clean spectator mount tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/xattr.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/xattr.c

## Purpose
`xattr.c` implements GFS2 extended attribute listing, lookup, get, set, remove, allocation, unstuffed data handling, indirect EA block handling, ACL data retrieval, and xattr fork deallocation.

## Important APIs, Types, And Functions
The main VFS handlers are `gfs2_xattr_get` and `gfs2_xattr_set`; exported GFS2 APIs are `__gfs2_xattr_set`, `gfs2_listxattr`, `gfs2_ea_dealloc`, and `gfs2_xattr_acl_get`. Internal request and location state comes from `struct gfs2_ea_request` and `struct gfs2_ea_location` in `xattr.h`.

Key helpers include `ea_calc_size`, `ea_check_size`, `ea_foreach`, `gfs2_ea_find`, `ea_dealloc_unstuffed`, `ea_list_i`, `gfs2_iter_unstuffed`, `ea_alloc_blk`, `ea_write`, `ea_alloc_skeleton`, `ea_set_simple`, `ea_set_block`, `ea_remove_stuffed`, `gfs2_xattr_remove`, `ea_dealloc_indirect`, and `ea_dealloc_block`.

## Control Flow
All xattr enumeration walks from `ip->i_eattr`. A direct EA block is scanned as EA records; an indirect EA fork first reads an indirect block and then scans each pointed-to EA block. Every record is bounds-checked, type-checked against filesystem format, and passed to a callback.

Get operations hold the inode glock shared unless already held, find the typed name, and copy stuffed data directly or unstuffed data through metadata data blocks. Set operations acquire quota data, hold the inode glock exclusive unless already held, validate immutable/append-only and name/data sizes, then initialize a new EA fork, replace in place, split an existing free tail, allocate unstuffed data blocks, or add a new EA block through direct-to-indirect conversion. Removal treats NULL value as delete, merges stuffed records where possible, or frees unstuffed data blocks under the owning rgrp glock.

Deallocation for inode eviction first removes unstuffed EA data, then frees indirect EA block pointers if present, then frees the primary EA block and updates the dinode when initialized.

## State And Persistence
Persistent state includes the dinode `di_eattr` pointer, `GFS2_DIF_EA_INDIRECT`, EA blocks, indirect pointer blocks, unstuffed EA data blocks, inode block counts, quota/statfs deltas, and ctime. All metadata mutations run inside GFS2 transactions and use rgrp allocation/freeing for block state.

## Dependencies And Integration Points
The file integrates VFS xattr handlers, POSIX ACL support, inode glocks, metadata I/O, rgrp allocation, quota, statfs, transactions, and GFS2 format-version rules. `super.h` exports handler arrays that choose trusted-xattr support based on filesystem format.

## Risks And Test Signals
Risks include malformed EA record lengths, direct/indirect fork transition bugs, leaking unstuffed blocks on replacement failure, quota/statfs drift, append-only enforcement differences, and using stale buffer pointers after replacing/removing an EA. Signals include xfstests xattr/ACL coverage, large xattr tests crossing stuffed thresholds, format-minimum trusted-xattr rejection, crash replay after xattr replacement, and fsck verification of EA forks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/xattr.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/xattr.h

## Purpose
`xattr.h` defines GFS2 extended attribute layout macros, request/location structs, and exported xattr APIs.

## Important APIs, Types, And Macros
Layout macros compute record and data lengths (`GFS2_EA_REC_LEN`, `GFS2_EA_DATA_LEN`), complete record size (`GFS2_EA_SIZE`), stuffed request size, stuffed/last flags, and pointer arithmetic from headers to names, data, data-pointer arrays, next records, and the first EA record in a buffer.

`struct gfs2_ea_request` carries the requested name, value, name length, value length, and GFS2 EA type. `struct gfs2_ea_location` records the buffer, matching EA header, and previous record for replacement/removal.

Exports include `__gfs2_xattr_set`, `gfs2_listxattr`, `gfs2_ea_dealloc`, and `gfs2_xattr_acl_get`.

## Control Flow And State
The macros encode the on-disk EA grammar used by `xattr.c`: stuffed data is stored after the name, unstuffed data stores an aligned array of block pointers, records are 8-byte aligned, and the last record fills the block. The API expects callers to hold appropriate glocks or use the VFS handlers that acquire them.

## Dependencies And Integration Points
This header is used by xattr implementation, ACL code, inode eviction, and superblock xattr handler exports. It depends on GFS2 on-disk EA header definitions and Linux inode types.

## Risks And Test Signals
Pointer arithmetic bugs here affect every xattr operation and can become metadata corruption. Test signals include xattr boundary-size tests, ACL get/set tests, malformed image rejection, and fsck after xattr create/replace/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/hfs/Kconfig

## Purpose
This Kconfig file declares build options for the Linux HFS filesystem and its KUnit tests.

## Important Options
`HFS_FS` is a tristate option named "Apple Macintosh file system support". It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. Its help text describes read-write access to Macintosh-formatted media and the module name `hfs`.

`HFS_KUNIT_TEST` is a tristate option for HFS filesystem KUnit tests. It depends on `HFS_FS && KUNIT`, defaults to `KUNIT_ALL_TESTS`, and is hidden when all KUnit tests are enabled.

## Control Flow And State
There is no runtime control flow here. The configuration controls whether HFS code is built in, built as a module, or omitted, and whether KUnit test objects are built.

## Dependencies And Integration Points
The selected symbols ensure the HFS implementation has block-device support, buffer heads, native language support, and legacy direct I/O support. The KUnit option integrates with the kernel KUnit harness and the HFS Makefile.

## Risks And Test Signals
Risks include stale dependency/selects when HFS internals change or tests building without required helpers. Signals are kernel configuration dependency resolution, module build success, and KUnit TAP output when `HFS_KUNIT_TEST` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/hfs/Makefile

## Purpose
The HFS Makefile defines how the kernel builds the HFS filesystem module or built-in object and its optional KUnit test object.

## Important Targets
`obj-$(CONFIG_HFS_FS) += hfs.o` builds the aggregate HFS object when configured. `hfs-objs` lists component objects: bitmap, B-tree find/node/record/tree, catalog, dir, extent, inode, attr, mdb, partition table, string, super, sysdep, and trans support. `obj-$(CONFIG_HFS_KUNIT_TEST) += string_test.o` adds the string KUnit test object when enabled.

## Control Flow And State
There is no runtime behavior. Build composition determines which `.c` files are linked into `hfs.o`, so dependencies among HFS internals are resolved at link time.

## Dependencies And Integration Points
The file consumes `CONFIG_HFS_FS` and `CONFIG_HFS_KUNIT_TEST` from Kconfig. It integrates all core HFS implementation files into one filesystem object.

## Risks And Test Signals
Risks include omitting a new source file from `hfs-objs`, stale test target names, or adding order-sensitive objects incorrectly. Signals are successful built-in and module builds, modpost output, and KUnit test linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/attr.c -->
# sources/distributed-fs/ceph-client/fs/hfs/attr.c

## Purpose
`attr.c` exposes classic HFS Finder metadata fields, file type and creator code, through Linux xattr handlers named `hfs.type` and `hfs.creator`.

## Important APIs, Types, And Functions
`enum hfs_xattr_type` distinguishes `HFS_TYPE` and `HFS_CREATOR`. `__hfs_setxattr` updates the catalog record's `UsrWds.fdType` or `UsrWds.fdCreator`. `__hfs_getxattr` retrieves the same four-byte fields. `hfs_xattr_get` and `hfs_xattr_set` adapt these helpers to the Linux xattr handler interface. `hfs_xattr_handlers` exports both handlers.

## Control Flow
Set rejects non-regular files and resource-fork inodes, initializes a catalog B-tree search, finds the inode catalog record by `HFS_I(inode)->cat_key`, reads the catalog file record, validates that the supplied value is exactly four bytes, copies the new Finder field, and writes the modified record back to the B-tree node. Get returns length four for size probes, or reads the catalog record and copies the requested four-byte field when the caller provided enough space.

## State And Persistence
The persistent state is the HFS catalog file record, specifically Finder user words inside `struct hfs_cat_file`. There is no separate xattr fork; Linux xattr calls are translated into catalog metadata updates.

## Dependencies And Integration Points
This file depends on HFS catalog B-tree search (`hfs_find_init`, `hfs_brec_find`, `hfs_bnode_read`, `hfs_bnode_write`), inode helpers, and the VFS xattr handler interface. It is linked into `hfs.o` through the HFS Makefile.

## Risks And Test Signals
Risks include exposing these attributes on unsupported inode types, accepting non-four-byte values, catalog search failures, and writeback not marking B-tree pages dirty. Signals include xattr get/set tests for `hfs.type` and `hfs.creator`, resource-fork rejection, catalog consistency after remount, and Finder metadata round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/bfind.c -->
# sources/distributed-fs/ceph-client/fs/hfs/bfind.c

## Purpose
`bfind.c` implements search cursor setup, teardown, binary search within a B-tree node, root-to-leaf traversal, record read, and cursor movement for HFS B-trees.

## Important APIs, Types, And Functions
`hfs_find_init` initializes `struct hfs_find_data`, allocates search and result key buffers, and locks the appropriate B-tree mutex class based on catalog, extents, or attributes tree CNID. `hfs_find_exit` releases the current bnode, frees buffers, and unlocks the tree. `__hfs_brec_find` performs in-node binary search for the best matching record. `hfs_brec_find` traverses from root to leaf through index records. `hfs_brec_read` finds and reads a record into a caller buffer. `hfs_brec_goto` moves a cursor by record count across neighboring leaf nodes.

## Control Flow
Search initialization must precede all operations and pins the tree lock. `hfs_brec_find` resets cursor offsets, starts at `tree->root`, checks expected node height and type at each level, calls `__hfs_brec_find`, and for index levels reads the child CNID from the found record. On leaf arrival, it leaves `fd->bnode`, record index, key offset/length, entry offset, and entry length populated.

`__hfs_brec_find` binary-searches record offsets, reads candidate keys, compares through `tree->keycmp`, and records either an exact match or the predecessor record. `hfs_brec_goto` moves backward or forward through `prev` and `next` leaf links and refreshes cursor offsets and key data.

## State And Persistence
The file updates only in-memory cursor state and bnode references. It reads persistent B-tree node descriptors, key areas, record offsets, and child pointers through `hfs_bnode_read`.

## Dependencies And Integration Points
It depends on `btree.h`, bnode lookup/reference management, per-tree key comparison, and mutex nesting classes. Catalog, extent, attribute, and xattr code use these search cursors to locate persistent records.

## Risks And Test Signals
Risks include invalid key lengths, inconsistent node height/type, off-by-one predecessor selection, cursor movement across leaf boundaries, and missing unlocks on init errors. Signals include catalog lookup tests, extent lookup tests, malformed B-tree image rejection, lockdep cleanliness for nested B-tree locks, and record iteration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/bfind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/hfs/bitmap.c

## Purpose
`bitmap.c` manages the HFS volume bitmap: finding and setting free allocation blocks, clearing allocated ranges, updating free block counts, and marking the bitmap dirty.

## Important APIs, Types, And Functions
`hfs_find_set_zero_bits` scans a big-endian 32-bit bitmap for the first zero bit at or after an offset, sets up to the requested number of consecutive zero bits, and returns the start. `hfs_vbm_search_free` is the public allocator search that locks the bitmap, tries the requested goal, wraps to zero if needed, decrements `free_ablocks`, and marks the bitmap dirty. `hfs_clear_vbm_bits` clears a range, increments `free_ablocks`, and marks the bitmap dirty.

## Control Flow
Allocation checks for nonzero requested count, locks `bitmap_lock`, scans the in-memory bitmap for a free run, wraps when the goal scan fails, reports full disk by returning zero length, updates free count, marks dirty, and unlocks. The low-level scanner handles partial first words, full 32-bit words, and partial tail words in left-to-right HFS bit order.

Freeing validates nonzero count and range, locks the bitmap, masks out partial first word, clears full words, masks the tail, updates the free count, unlocks, and marks the bitmap dirty.

## State And Persistence
State lives in `HFS_SB(sb)->bitmap`, `fs_ablocks`, and `free_ablocks`. Dirty marking schedules persistence through HFS metadata writeback; the file itself mutates the in-memory big-endian bitmap words.

## Dependencies And Integration Points
The code depends on HFS superblock state, `bitmap_lock`, endian conversion helpers, debug logging, and `hfs_bitmap_dirty`. Extent and allocation code call these functions to reserve or release allocation blocks.

## Risks And Test Signals
Risks include off-by-one wrap behavior, mismatched big-endian bit order, free count drift, clearing out-of-range ranges, and lack of already-clear detection despite comments mentioning that error. Signals include allocation/free stress tests, fsck free block count checks, fragmented bitmap tests, full-disk tests, and endian-sensitive image tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/bnode.c -->
# sources/distributed-fs/ceph-client/fs/hfs/bnode.c

## Purpose
`bnode.c` implements low-level HFS B-tree node I/O, validation, sibling unlinking, hash-cache lookup, node creation/loading, reference counting, deletion cleanup, and page-backed memory operations.

## Important APIs, Types, And Functions
Read/write helpers include `hfs_bnode_read`, `hfs_bnode_read_u16`, `hfs_bnode_read_u8`, `hfs_bnode_read_key`, `hfs_bnode_write`, `hfs_bnode_write_u16`, `hfs_bnode_write_u8`, `hfs_bnode_clear`, `hfs_bnode_copy`, and `hfs_bnode_move`. Structural helpers include `hfs_bnode_dump`, `hfs_bnode_unlink`, `hfs_bnode_findhash`, `hfs_bnode_unhash`, `hfs_bnode_find`, `hfs_bnode_free`, `hfs_bnode_create`, `hfs_bnode_get`, and `hfs_bnode_put`.

Internal guards `is_bnode_offset_valid` and `check_and_correct_requested_length` reject or clamp invalid node offsets/lengths. `hfs_bnode_hash` maps CNIDs to the tree hash table.

## Control Flow
`hfs_bnode_find` first searches the tree hash under `hash_lock`; if absent, `__hfs_bnode_create` allocates a node, inserts a new placeholder into the hash, reads backing pages from the B-tree inode mapping, and leaves `HFS_BNODE_NEW` set while validation proceeds. Other waiters find the placeholder, increment its refcount, and wait for `HFS_BNODE_NEW` to clear.

Validation reads the node descriptor, records prev/next links, record count, type, and height, verifies type/height consistency with tree depth, then walks the record offset table to ensure monotonic, in-range, even offsets and plausible key sizes. `hfs_bnode_create` creates a zeroed new node and clears `HFS_BNODE_NEW`. `hfs_bnode_put` decrements the refcount under the hash lock; deleted nodes are unhashed, zeroed, freed in the bitmap, and released.

## State And Persistence
Persistent state is the page-backed B-tree node data, descriptor, record offsets, links, and records. In-memory state includes node refcount, flags (`NEW`, `ERROR`, `DELETED`), hash chain membership, loaded pages, node identity, type, height, sibling links, and parent. Writes mark affected pages dirty.

## Dependencies And Integration Points
This file depends on Linux page cache helpers, HFS B-tree structures, hash locking, wait queues, and B-tree bitmap allocation/freeing. Higher-level B-tree search, insert/delete, catalog, extent, and xattr code depend on these node primitives.

## Risks And Test Signals
Risks include page-boundary assumptions in write/copy/move helpers, clamped reads hiding corruption, stale hash entries, refcount underflow, waiting on nodes that remain `NEW`, and malformed offset tables. Signals include KASAN/KCSAN/lockdep under B-tree mutation, malformed image mount rejection, catalog/extent iteration tests, node create/delete stress, and dirty page writeback checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/bnode.c -->
