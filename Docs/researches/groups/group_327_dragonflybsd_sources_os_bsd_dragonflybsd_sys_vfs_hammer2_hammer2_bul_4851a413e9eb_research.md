# Group Research: group_327_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer2_hammer2_bul_4851a413e9eb

Scope: `Docs/research_subset_a.md`

Files researched completely:
- `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_bulkfree.c`
- `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.c`
- `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.h`
- `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_chain.c`
- `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_cluster.c`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_bulkfree.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_bulkfree.c

## Purpose
Implements HAMMER2's bulk-free pass: a background/manual recovery-style scanner that reconstructs live allocation state from reachable blockrefs, compares it with the live freemap, and advances two-stage free transitions.

## Key Elements
- `hammer2_bulkfree_scan()` walks topology from a referenced unlocked parent, locks each parent shared with data resolution, uses `hammer2_chain_scan()` to iterate blockrefs, counts inode/dirent/chain/byte statistics, skips unsafe recursion on CRC-check errors, and bounds recursion by saving chains in a TAILQ when depth or saved-chain limits are exceeded.
- `hammer2_bulkfree_pass()` clears the live dedup cache, allocates a swap-backed in-memory freemap window, repeatedly scans the volume over storage ranges sized by the supplied bulkfree buffer, drains deferred chains, and only syncs freemap state if the scan was not aborted.
- `cbinfo_bmap_init()` initializes each 4MB in-memory freemap segment, marking reserved/out-of-media ranges as fully allocated/unavailable and normal usable ranges as fully free before live blockrefs are replayed.
- `h2_bulkfree_callback()` processes each reachable blockref in the current storage window, throttles non-leaf scanning with `hammer2_bulkfree_tps`, updates segment class/avail/linear metadata, and marks corresponding 16KB freemap bitmap cells as allocated (`11`).
- `h2_bulkfree_sync()` iterates live freemap leaves through the device freemap chain, skips unchanged segments when bitmap/linear/bigmask are already acceptable, modifies changed freemap leaves, resets the relaxed allocation heuristic, and calls the adjust routine.
- `h2_bulkfree_sync_adjust()` applies the transition rules: memory `00` versus live `11` becomes live `10`, memory `00` versus live `10` becomes live `00`, memory `11` versus live `10` becomes live `11`, and unexpected live-free-to-allocated repairs are counted and warned.
- `h2_bulkfree_test()` is an 8-way dedup heuristic keyed by `data_off`; it avoids repeatedly descending already-seen physical trees and preserves saved errors for duplicate references.
- `bigmask_get()` and `bigmask_good()` compute/check permissive freemap allocation-size availability masks used for sync shortcuts.

## Dependencies
Uses HAMMER2 chain traversal, freemap allocation metadata, device volume data locking/modification, swap-backed kernel memory, DragonFly sleep/signal/tick primitives, HAMMER2 dedup cache helpers, and global tuning knobs such as `hammer2_limit_saved_depth`, `hammer2_limit_saved_chains`, `hammer2_bulkfree_tps`, `hammer2_debug`, and `hammer2_aux_flags`.

## Behavior/Risks
- Designed to run concurrently with frontend operations by scanning a synchronized volume snapshot and relying on the two-stage freemap transition to avoid freeing newly allocated blocks.
- Aborts on user/kernel signal and avoids synchronizing a partial in-memory freemap after abort.
- Continues through CRC check errors where possible, but refuses to recurse through corrupt block tables because they can loop indefinitely or panic the scanner.
- Correctness depends on complete topology traversal, valid blockref `data_off`/radix boundaries, and no allocation crossing HAMMER2's 1GB L1 or 4MB L0 freemap boundaries; boundary violations are logged and clipped.
- Emergency/recovery value is high, but this file directly mutates freemap state and volume free-space accounting, so bugs can create leaks or false frees.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_bulkfree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.c

## Purpose
Implements the local locking portion of HAMMER2's CCMS cache coherency state, currently providing shared/exclusive thread locks over `ccms_cst_t`.

## Key Elements
- `ccms_cst_init()` zeroes the cache-state structure and initializes its HAMMER2 spinlock; `ccms_cst_uninit()` asserts no active holders.
- `ccms_thread_lock()` acquires shared or exclusive state, allowing recursive exclusive acquisition by the owning thread and sleeping on the CST when incompatible locks or upgrades are present.
- `ccms_thread_lock_nonblock()` mirrors normal locking but returns `EBUSY` instead of sleeping.
- `ccms_thread_lock_temp_release()` and `ccms_thread_lock_temp_restore()` temporarily release and reacquire the caller's held state.
- `ccms_thread_lock_upgrade()` converts a shared lock to exclusive by incrementing `upgrade`, dropping the caller's shared count, and waiting for other shared holders to drain.
- `ccms_thread_lock_downgrade()` returns an upgraded exclusive lock back to shared state and wakes blocked waiters.
- `ccms_thread_unlock()` releases recursive exclusive, final exclusive, or shared locks, waking sleepers when the final blocking condition clears.
- `ccms_thread_unlock_upgraded()` releases a lock that had been upgraded from shared or falls back to normal unlock for exclusive-origin locks.
- `ccms_thread_lock_owned()` and `ccms_thread_lock_setown()` expose/check exclusive ownership.

## Dependencies
Uses DragonFly kernel primitives (`curthread`, `ssleep`, `wakeup`, `hz`, `panic`, `KKASSERT`) and HAMMER2 spin wrappers from `hammer2.h`/`hammer2_ccms.h`. `LOCKENTER` and `LOCKEXIT` are external lock-debug/accounting macros.

## Behavior/Risks
- The implementation is strictly local locking, not the full distributed MESI-like protocol described in the header comments.
- Exclusive locks are recursive only for the owning thread; shared locks wait behind pending upgrades to prevent upgrade starvation.
- The code depends on callers pairing upgrade/downgrade/unlock APIs correctly; incorrect pairing corrupts `upgrade`, `count`, or `td` state and will assert or panic.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.h

## Purpose
Defines HAMMER2's CCMS cache-state data model and kernel API for local/thread cache-state locking.

## Key Elements
- Documents CCMS as a cache coherency management layer intended to integrate with VFS inode topology, persistent cache grants, and possible cluster/remote coherency.
- Defines `ccms_key_t`, `ccms_tid_t`, `ccms_state_t`, and `ccms_type_t`.
- Defines cache states: `CCMS_STATE_INVALID`, `CCMS_STATE_SHARED`, and `CCMS_STATE_EXCLUSIVE`.
- Defines type flags for inherited state, modified exclusive state, master/slave roles, quorum slave state, and recursion. The macro `CCMS_TYPE_QSALVE` appears misspelled relative to the comment's `QSLAVE`.
- Defines `struct ccms_cst` with a HAMMER2 spinlock, granted/inherited state and type, upgrade count, shared/exclusive count, blocked flag, and owning thread for exclusive state.
- Declares kernel APIs for CST init/uninit, blocking/nonblocking lock acquisition, temporary release/restore, upgrade/downgrade, unlock, upgraded unlock, ownership testing, and owner setting.

## Dependencies
Includes DragonFly kernel type/param/serialize/spinlock headers and uses `hammer2_spin_t` and `thread_t`.

## Behavior/Risks
- The comments describe a broader distributed cache-coherency architecture than the local implementation in `hammer2_ccms.c` currently provides.
- `count` semantics are central: positive means shared holders, negative means recursive exclusive depth, and zero means unlocked.
- Consumers must observe top-down higher-level CST locking rules described in the comments to avoid deadlocks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_chain.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_chain.c

## Purpose
Implements HAMMER2's core in-memory chain abstraction: keyed topology nodes for volume roots, inodes, indirect blocks, freemap blocks, data blocks, and dirents, including lifecycle, locking, lookup, copy-on-write modification, insertion/deletion, indirect-node maintenance, blockref array management, checksum handling, and debugging.

## Key Elements
- `hammer2_chain_cmp()` defines the RB-tree ordering by blockref key ranges and treats overlap as equality, making overlapping chains invalid.
- `hammer2_chain_setflush()` propagates `HAMMER2_CHAIN_ONFLUSH` upward until an inode or volume root so the flusher can find modified/update subtrees.
- `hammer2_chain_alloc()` and `hammer2_chain_init()` allocate and initialize disconnected chains, set PFS boundary state, derive physical byte size from `data_off` radix, and initialize locks/RB trees.
- `hammer2_chain_ref()`, `hammer2_chain_ref_hold()`, `hammer2_chain_drop()`, `hammer2_chain_lastdrop()`, `hammer2_chain_unhold()`, `hammer2_chain_drop_unhold()`, and `hammer2_chain_rehold()` implement reference/hold lifecycle, delayed disposal, parent unlinking, data-drop behavior, and nonrecursive parent re-drop handling.
- `hammer2_chain_lock()`, `hammer2_chain_load_data()`, and `hammer2_chain_unlock()` provide shared/exclusive chain locking with optional data resolution, I/O interlocking via `HAMMER2_CHAIN_IOINPROG`, checksum validation, INITIAL zero/new buffer handling, and last-unlock data release.
- `hammer2_chain_base_and_count()` and `hammer2_chain_countbrefs()` abstract parent blockref arrays and synchronize live blockref counts used by create/delete/search logic.
- `hammer2_chain_resize()` reallocates data/indirect/dirent physical storage when size changes, preserving data through modify/COW when needed and dropping old DIO state for caller-provided data rewrites.
- `hammer2_chain_modify()` is the central mutation routine: marks MODIFIED/UPDATE, handles dedup offsets, copy-on-write allocation, overwrite-in-place eligibility for CHECK_NONE data beyond snapshots, emergency-mode modify-in-place fallback, DIO replacement/dirtying, BLKMAPUPD propagation, and flush visibility.
- `hammer2_chain_modify_ip()` couples inode metadata modification with chain modification.
- `hammer2_chain_find()`, `hammer2_base_find()`, and `hammer2_combined_find()` merge in-memory RB-tree chains with on-media blockref arrays for range lookup/iteration.
- `hammer2_chain_get()`, `hammer2_chain_lookup_init()`, `hammer2_chain_lookup_done()`, `hammer2_chain_getparent()`, `hammer2_chain_repparent()`, and `hammer2_chain_repchange()` handle materializing media blockrefs into chains, safe parent acquisition despite lock-order reversal, and parent tracking across deletion/reparenting.
- `hammer2_chain_lookup()`, `hammer2_chain_next()`, and `hammer2_chain_scan()` provide key lookup, iteration, and raw blockref scans, including direct-data inode shortcut handling, deleted-chain skipping, upward/downward indirect traversal, and generation-race retries.
- `hammer2_chain_create()` creates or reconnects chains under a parent, inherits or enforces check methods, creates indirect blocks when blockref arrays are full, sets PFSROOT flags, inserts into parent RB/live state, and marks new chains modified.
- `hammer2_chain_create_indirect()` creates indirect/freemap-node blocks, chooses a keyspace, moves qualifying child blockrefs/chains into the new node while preserving original blockrefs when required, and returns the proper parent for the pending insert.
- `hammer2_chain_rename()`, `hammer2_chain_rename_obref()`, `_hammer2_chain_delete_helper()`, `hammer2_chain_delete()`, and `hammer2_chain_delete_obref()` move or remove chains from live RB trees and blockref arrays, preserving old blockrefs for indirect-maintenance moves and marking permanent deletions for flush/destroy.
- `hammer2_chain_indirect_maintenance()` deletes empty indirect blocks or collapses sparse indirect blocks back into the parent when the parent has room, with reptrack handoff for in-progress parent lookups.
- `hammer2_chain_indkey_freemap()`, `hammer2_chain_indkey_file()`, and `hammer2_chain_indkey_dir()` compute new indirect key/keybits for freemap, file data, inode index, and directory hash spaces.
- `hammer2_base_delete()` and `hammer2_base_insert()` maintain sorted parent blockref arrays, live-zero hints, BLKMAPPED/BLKMAPUPD flags, `leaf_count`, and embedded inode/data statistics.
- `hammer2_chain_setcheck()` and `hammer2_chain_testcheck()` generate and validate configured check modes: none/disabled, iSCSI CRC32, xxHash64, SHA192, and freemap CRC.
- `hammer2_characterize_failed_chain()` rate-limits checksum failure reporting and attempts to trace the failed chain back to an inode, PFS, and device.
- `hammer2_chain_inode_find()` locates inode chains by checking live inode structures first, then the inode index radix tree, validating the returned inode number.
- `hammer2_chain_bulksnap()` and `hammer2_chain_bulkdrop()` create/free a volume-root snapshot chain used by bulk scans.
- `hammer2_chain_dirent_test()` matches inode or dirent chains against names, including embedded short dirent names.
- `hammer2_dump_chain()` recursively prints chain topology for debugging.

## Dependencies
Relies on HAMMER2 structures and helpers from `hammer2.h`, DragonFly mutex/spin/lock/buf primitives, kernel allocation APIs, HAMMER2 freemap allocation/adjustment, flusher integration, inode lookup helpers, volume data, I/O layer, CRC/hash routines (`hammer2_icrc32`, `XXH64`, SHA256), rate-limited console printing, and many HAMMER2 flags/constants.

## Behavior/Risks
- This is a high-risk core metadata module. It coordinates COW, snapshots, dedup, freemap allocation, cached chain topology, and flush propagation.
- Lock ordering is delicate. Parent/child traversal uses top-down chain locks, bottom-up spinlock nesting for some ref/drop paths, nonblocking parent acquisition, and reptrack structures to survive deletion/reparent races.
- `hammer2_chain_modify()` has intentionally unsafe emergency-mode modify-in-place paths that can corrupt related snapshots; console warnings are rate-limited.
- Lookups and scans must reconcile on-media blockrefs with modified in-memory chains; generation checks and retry loops guard races, with max-loop panics for runaway corruption or logic bugs.
- Incorrect BLKMAPPED/BLKMAPUPD/UPDATE handling can leak chains, lose parent blockref updates, or leave dirty in-memory inode chains invisible to flush.
- Checksum validation is skipped for `NOTTESTED` and disabled/none modes; failed checks set chain errors and can prevent safe traversal by other modules such as bulkfree.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_chain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_cluster.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_cluster.c

## Purpose
Implements basic HAMMER2 cluster object operations over multiple per-node chains, including focus selection, ref/drop/lock wrappers, and quorum validation for multi-master or master/slave cluster views.

## Key Elements
- File-level comments describe the intended cluster abstraction: collect chains from multiple nodes into one frontend topology, handle I/O dispatch/status rollup/mastership/quorum, and provide chain-like APIs to vnops.
- `hammer2_cluster_type()` returns the focused chain's blockref type or empty type when the cluster is errored.
- `hammer2_cluster_bref()` copies the focus blockref but clears `data_off`, because physical offsets are per-node and not useful to the frontend cluster view.
- `hammer2_dummy_xop_from_chain()` builds a degenerate one-chain cluster/xop from a locked chain, transferring the chain lock/reference into the cluster and marking hard read/write and sync flags.
- `hammer2_cluster_ref()` increments the cluster reference count.
- `hammer2_cluster_drop()` releases the final cluster reference, drops all underlying chains, clears safety fields, and frees the cluster allocation.
- `hammer2_cluster_lock()` locks all underlying chains with the requested chain lock mode and marks the cluster locked without re-resolving focus.
- `hammer2_cluster_unhold()` and `hammer2_cluster_rehold()` apply chain unhold/rehold to all underlying chains.
- `hammer2_cluster_check()` is the core resolver. It counts total masters/slaves, determines quorum, selects the highest matching quorum `modify_tid`, returns `EINPROGRESS`, `ESRCH`, `EDEADLK`, `ENOENT`, `EIO`, or chain/check errors as appropriate, marks valid/invalid cluster items, chooses focus/focus index, sets read/write hard/soft and master/slave sync flags, and validates that non-focus matching items have the same type/key/keybits/modify_tid/bytes/ddflag.
- `hammer2_cluster_unlock()` clears the locked flag and unlocks all underlying chains.

## Dependencies
Uses `hammer2_chain_*` lifecycle/lock APIs, HAMMER2 PFS type arrays, cluster/citem flags, HAMMER2 error codes, atomic flag operations, and kernel assertions/printing.

## Behavior/Risks
- The implemented file is narrower than the extensive file header suggests; asynchronous xops and network dispatch live elsewhere, while this file mainly handles local cluster state/focus/quorum.
- `hammer2_cluster_check()` has several explicit TODO/XXX notes around soft master/slave handling and cumulative error behavior.
- Focus selection depends on quorum among masters and matching `modify_tid`; desynchronized nodes can yield `EINPROGRESS`, `ESRCH`, or `EDEADLK` instead of a usable focus.
- Cluster consumers must respect the locked/refcount contract. The dummy-xop constructor transfers ownership of the chain lock/reference, so callers must not unlock/drop that chain separately.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_cluster.c -->