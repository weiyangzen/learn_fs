# Group Research: group_847_linux_sources_os_linux_linux_fs_ubifs_lpt_c_sources_os_linux_linux_f_bb06628a3f98

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux/fs/ubifs/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/lpt.c -->
# File Research: sources/os/linux/linux/fs/ubifs/lpt.c

## Role

Implements UBIFS LEB Properties Tree (LPT) geometry, default creation, packed on-flash encoding, lazy read/lookup, dirty copy-on-write lookup, authenticated hashing, range scanning, and debug validation.

## Key APIs

- `ubifs_calc_lpt_geom()`, `ubifs_create_dflt_lpt()`
- `ubifs_pack_pnode()`, `ubifs_pack_nnode()`, `ubifs_pack_ltab()`, `ubifs_pack_lsave()`
- `ubifs_unpack_bits()`, `ubifs_unpack_nnode()`
- `ubifs_read_nnode()`, `ubifs_get_nnode()`, `ubifs_get_pnode()`
- `ubifs_pnode_lookup()`, `ubifs_lpt_lookup()`, `ubifs_lpt_lookup_dirty()`
- `ubifs_lpt_calc_hash()`, `ubifs_lpt_init()`, `ubifs_lpt_scan_nolock()`
- Debug entry: `dbg_check_lpt_nodes()`

## Important Behavior

The file treats the LPT as a miniature wandering tree stored between the log and orphan areas. It supports a small model, where the whole LPT can be rewritten, and a big model, where LPT garbage collection and the saved-LEB table are needed.

Geometry calculation derives tree height, pnode/nnode counts, packed bit widths, node sizes, ltab/lsave sizes, and minimum LPT space. Default-format creation iteratively chooses `lpt_lebs` and big/small model, then writes pnodes, nnodes, optional lsave, and ltab while calculating the authenticated LPT hash.

Packed LPT nodes do not use normal UBIFS common headers. `pack_bits()` and `ubifs_unpack_bits()` encode tight bit fields plus CRC16. Pnodes store per-main-LEB free/dirty/index state; nnodes store child LPT locations; ltab stores LPT-area free/dirty state; lsave stores useful main-area LEB numbers for faster big-LPT mount.

Runtime lookup lazily reads nnodes and pnodes from flash, validates branch ranges and pnode free/dirty invariants, sets main-area LEB numbers, and inserts loaded pnode lprops into category heaps/lists. Dirty lookup performs COW if a cnode is currently being committed, preserving commit consistency while allowing new lprops changes.

`ubifs_lpt_calc_hash()` walks pnodes, packs each pnode, and hashes them for authenticated mounts. `lpt_check_hash()` compares the calculated hash with the master-node LPT hash.

`ubifs_lpt_scan_nolock()` scans lprops across a requested LEB range with wraparound support. Its callback may request that the current path be materialized into the in-memory LPT and category structures.

## Dependencies

Depends on UBIFS lprops category helpers, UBI LEB read/change/unmap I/O, CRC16, authenticated hash helpers, LPT commit/free functions in `lpt_commit.c`, and debug helpers.

## Research Notes

Correctness depends on exact agreement between LPT geometry, superblock/master metadata, and packed bit widths. CRC/type/range failures abort mount. Dirty COW and category replacement are concurrency-sensitive around commit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/lpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/lpt_commit.c -->
# File Research: sources/os/linux/linux/fs/ubifs/lpt_commit.c

## Role

Implements commit-time LPT handling: selecting dirty LPT cnodes, laying them out, writing them, maintaining LPT-area lprops, performing trivial and regular LPT garbage collection, freeing obsolete COW nodes, and validating/dumping LPT state for debugging.

## Key APIs

- `ubifs_lpt_start_commit()`
- `ubifs_lpt_end_commit()`
- `ubifs_lpt_post_commit()`
- `ubifs_lpt_free()`
- Debug entries: `dbg_check_ltab()`, `dbg_chk_lpt_free_spc()`, `dbg_chk_lpt_sz()`, `ubifs_dump_lpt_lebs()`

## Important Behavior

Commit starts by checking LPT consistency, optionally running LPT GC if free space is low, doing trivial GC marking, populating lsave for big LPT, building a circular list of dirty cnodes, laying out new node locations, and calculating the LPT hash into the master node.

`get_cnodes_to_commit()` walks the dirty in-memory LPT tree and freezes dirty cnodes by setting `COW_CNODE`. Later modifications in `lpt.c` copy these cnodes instead of altering the commit snapshot.

`layout_cnodes()` assigns target LEB/offset locations without writing. It places lsave and ltab where possible, allocates empty LPT LEBs via `alloc_lpt_leb()`, updates ltab free/dirty accounting, and records new branch locations or root location.

`write_cnodes()` repeats the same allocation sequence with `realloc_lpt_leb()`, packs lsave/ltab/cnodes into `c->lpt_buf`, writes aligned chunks, clears `DIRTY_CNODE` and `COW_CNODE` with memory barriers, and advances `nhead_lnum:nhead_offs`.

For small LPT, `make_tree_dirty()` can force the whole tree dirty when space is low. For big LPT, `lpt_gc()` chooses a dirty LPT LEB and `lpt_gc_lnum()` scans its packed LPT nodes, marking still-current nodes dirty so they will be rewritten elsewhere.

Trivial GC marks LPT LEBs that contain only dirty+free space during start-commit and unmaps them after the master node has committed.

`ubifs_lpt_free()` releases write-only buffers, lsave, ltab commit copy, obsolete commit cnodes, loaded LPT tree nodes, heaps, dirty-index heap, ltab, and node buffers.

## Dependencies

Works with the packed LPT format and lazy lookup in `lpt.c`, lprops locking, category/lprops mutation, UBI LEB write/unmap/change, UBIFS authenticated hashing, debug infrastructure, and randomization hooks for lsave debug population.

## Research Notes

The start/end commit split relies on deterministic reallocation: end-commit must consume exactly the LEBs marked by start-commit. Space accounting is heavily asserted because LPT is designed never to run out of space. COW flag transitions and obsolete-node freeing are central to avoiding concurrent mutation of the commit snapshot.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/lpt_commit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/master.c -->
# File Research: sources/os/linux/linux/fs/ubifs/master.c

## Role

Reads, validates, compares, authenticates, and writes the UBIFS master node. The master node records mount-critical filesystem state, including log/index/LPT/orphan/lprops positions and space accounting.

## Key APIs

- `ubifs_compare_master_node()`
- `ubifs_read_master()`
- `ubifs_write_master()`

## Important Behavior

UBIFS keeps two master-node LEBs. `scan_for_master()` scans both, requires matching node counts, offsets, and master contents, and selects the latest valid master node. The comparison ignores the common header and embedded HMAC because sequence numbers, CRCs, and HMACs differ between mirrored writes.

Authenticated mounts validate either the superblock-recorded master hash, when the HMAC field is zero, or the master-node HMAC.

`ubifs_read_master()` allocates `c->mst_node`, scans or recovers the master node, clears the recovery flag in memory, converts little-endian fields into `struct ubifs_info`, copies the root-index hash, detects the no-orphans flag, handles automatic resize growth, validates all loaded values, and initializes old-index debug checking.

`validate_master()` checks sequence/cmt/inode watermarks, log head, root branch, GC LEB, index head, old index size, LPT root/head/ltab/lsave locations, lscan position, and global free/dirty/used/dead/dark space totals.

`ubifs_write_master()` appends the next master node in the first master LEB, wraps by unmapping when needed, writes with HMAC, and mirrors the same node to the second master LEB at the same offset.

## Dependencies

Interacts with scan/recovery code, authenticated hash/HMAC helpers, node write helpers, superblock authentication metadata, LPT geometry fields, and debug old-index validation.

## Research Notes

Master validation is the mount gate for most UBIFS global invariants. Recovery is delegated to `recovery.c` when the mirrored master area is inconsistent but recoverable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/master.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/misc.c -->
# File Research: sources/os/linux/linux/fs/ubifs/misc.c

## Role

Provides shared UBIFS message, error, warning, and assertion-action naming helpers.

## Key APIs

- `ubifs_msg()`
- `ubifs_err()`
- `ubifs_warn()`
- `ubifs_assert_action_name()`

## Important Behavior

`ubifs_msg()` emits normal notices tagged with UBI device and volume IDs. `ubifs_err()` and `ubifs_warn()` include UBI identifiers, current PID, and caller return address, which helps locate the emitting function in diagnostics.

`ubifs_assert_action_name()` maps the configured assertion action to the strings `report`, `read-only`, or `panic`.

## Dependencies

Uses Linux printk helpers, `struct va_format`, current task PID, and UBIFS assertion-action constants from `ubifs.h`.

## Research Notes

This file is small but central to consistent diagnostics. Error and warning helpers intentionally include the call site via `__builtin_return_address(0)`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/misc.h -->
# File Research: sources/os/linux/linux/fs/ubifs/misc.h

## Role

Defines small inline helpers used broadly across UBIFS for znode state, background-thread wakeup, inode conversion, compressor metadata, write-buffer sync, device encoding, lprops locking, LPT/lprops updates, index-node layout, TNC lookup, log wraparound, and xattr limits.

## Key APIs

- Znode flags: `ubifs_zn_dirty()`, `ubifs_zn_obsolete()`, `ubifs_zn_cow()`
- Runtime helpers: `ubifs_wake_up_bgt()`, `ubifs_inode()`
- Compression helpers: `ubifs_compr_present()`, `ubifs_compr_name()`
- I/O/lprops helpers: `ubifs_wbuf_sync()`, `ubifs_add_dirt()`, `ubifs_return_leb()`
- Index helpers: `ubifs_idx_node_sz()`, `ubifs_idx_branch()`, `ubifs_idx_key()`
- TNC/log helpers: `ubifs_tnc_lookup()`, `ubifs_next_log_lnum()`
- Locking: `ubifs_get_lprops()`, `ubifs_release_lprops()`
- Xattr limit: `ubifs_xattr_max_cnt()`

## Important Behavior

The znode helpers are thin wrappers over znode flag bits. `ubifs_wake_up_bgt()` wakes the background thread only when present and not already requested.

`ubifs_wbuf_sync()` locks the write-buffer I/O mutex with the journal-head subclass, calls the no-lock sync helper, and unlocks.

Index helpers encode UBIFS variable key/hash length into index-node and branch pointer arithmetic. `ubifs_tnc_lookup()` is a convenience wrapper over `ubifs_tnc_locate()`.

Lprops helpers centralize lock acquisition/release and include sanity assertions on release. `ubifs_add_dirt()` and `ubifs_return_leb()` route common lprops mutations through the lprops update APIs.

`ubifs_next_log_lnum()` wraps log LEB numbers from `log_last` back to `UBIFS_LOG_LNUM`.

## Dependencies

Depends on UBIFS core types, Linux inode/container helpers, bit operations, mutexes, device encoding helpers, compressor registry, write-buffer code, TNC lookup, and lprops mutation APIs.

## Research Notes

This header is a low-level convenience layer. Several helpers encode important contracts: callers of `ubifs_get_lprops()` must release through `ubifs_release_lprops()`, and index branch arithmetic must stay aligned with the on-flash index format.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/orphan.c -->
# File Research: sources/os/linux/linux/fs/ubifs/orphan.c

## Role

Tracks UBIFS orphan inodes, writes orphan records during commit, deletes recorded orphan inodes after unclean unmounts, clears orphan areas after clean mounts, and provides debug consistency checks.

## Key APIs

- `ubifs_add_orphan()`
- `ubifs_delete_orphan()`
- `ubifs_orphan_start_commit()`
- `ubifs_orphan_end_commit()`
- `ubifs_clear_orphans()`
- `ubifs_mount_orphans()`

## Important Behavior

An orphan is an inode committed with link count zero, commonly an unlinked but still-open file. UBIFS keeps current orphans in an rb-tree plus ordered lists. `ubifs_add_orphan()` inserts a new orphan, enforces `max_orphans`, and tracks it on both the all-orphans and new-orphans lists. `ubifs_delete_orphan()` removes an orphan immediately unless it is currently being committed, in which case it is marked for delayed deletion.

Commit starts by moving all new orphans to a cnext commit list and marking whether the master node should advertise no-orphans. Commit end writes pending orphan nodes if needed, then erases delayed-deletion orphan objects.

Orphan nodes are written sequentially through the fixed orphan area. If available tail space is insufficient, `consolidate()` rewrites all non-new orphans atomically from the first orphan LEB, leaving half the total orphan area available for future additions. The last orphan node for a commit sets the high bit of `cmt_no`.

On mount after an unclean unmount, `kill_orphans()` scans orphan LEBs, recovers corrupt orphan LEBs if needed, honors commit-number ordering and last-node markers, and removes keys for recorded orphan inodes from the TNC when the inode still has `nlink == 0`. This protects relinked `O_TMPFILE` cases.

`ubifs_mount_orphans()` sets `max_orphans`, allocates the orphan buffer for writable mounts, kills orphans after unclean mounts, or clears the orphan area after clean writable mounts.

Debug code scans both the orphan area and the index to verify that zero-link inode nodes are represented either on flash or in the in-memory orphan tree.

## Dependencies

Uses rbtrees, spinlocks, UBIFS scan/recovery, TNC lookup/removal, node write/change/unmap helpers, orphan node format, and debug index walking.

## Research Notes

The orphan write protocol is crash-order sensitive. Consolidation is designed so an unclean unmount cannot lose orphan records. Deletion during commit is deferred to avoid freeing objects still referenced by the commit list.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/recovery.c -->
# File Research: sources/os/linux/linux/fs/ubifs/recovery.c

## Role

Implements UBIFS recovery from unclean unmounts, including master-node recovery, corrupted-tail LEB repair, read-only deferred cleanup, index/LPT head cleanup, GC-LEB recovery, and inode-size repair.

## Key APIs

- `ubifs_recover_master_node()`
- `ubifs_write_rcvrd_mst_node()`
- `ubifs_recover_leb()`
- `ubifs_recover_log_leb()`
- `ubifs_recover_inl_heads()`
- `ubifs_clean_lebs()`
- `ubifs_rcvry_gc_commit()`
- `ubifs_recover_size_accum()`
- `ubifs_recover_size()`
- `ubifs_destroy_size_tree()`

## Important Behavior

Recovery accepts corruption only when it matches UBIFS’s write model: nodes are written sequentially into erased LEBs, and power-cut corruption may affect only the last write unit with empty space afterward. Helpers such as `is_last_write()`, `no_more_nodes()`, `clean_buf()`, and `fix_unclean_leb()` enforce that model.

Master recovery reads both master LEBs, locates the last valid master node while allowing one interrupted write area, compares valid copies, and either writes a recovered master node immediately or stores it for later when mounted read-only. Recovered master writes set `UBIFS_MST_RCVRY` while writing, then restore flags in memory.

`ubifs_recover_leb()` scans a data/journal LEB, tolerates tail corruption only in valid recovery cases, drops incomplete grouped nodes, handles special GC-head min-IO-unit truncation, pads/cleans the rest of the LEB, and either writes the fixed LEB or records it on `unclean_leb_list` for later RW remount.

`ubifs_recover_log_leb()` can recover only the end of the log and verifies the next log LEB is empty or older than the current commit start sequence number.

`ubifs_recover_inl_heads()` cleans stale data at the index and LPT head positions after a half-completed commit.

GC recovery chooses or creates a valid `gc_lnum`, runs a commit so replay order is stable on future mounts, and may garbage-collect a dirty LEB into the GC head before unmapping the retained old GC LEB.

Size recovery accumulates inode sizes seen during journal replay. It removes data nodes for nonexistent inodes and fixes inode size upward either in place or by loading and journaling the inode, with read-only mounts pinning inodes until RW remount.

## Dependencies

Interacts with scan code, master code, journal replay, orphan recovery, TNC lookup/removal, inode journal writes, GC, lprops, write buffers, UBI LEB change/unmap, and authenticated node preparation.

## Research Notes

The power-cut corruption tests are intentionally strict; non-tail or non-empty-following corruption returns `-EUCLEAN`. Read-only mounts defer required media writes, so remount paths must call cleanup. GC recovery ordering is delicate because committing before/after GC changes how later mounts see orphan and GC operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/replay.c -->
# File Research: sources/os/linux/linux/fs/ubifs/replay.c

## Role

Implements UBIFS journal replay during mount. It scans log LEBs for bud references, scans/recover/authenticates buds, builds sorted replay entries, applies them to the TNC, fixes lprops for replayed buds, and seeds budgeting state.

## Key APIs

- `ubifs_replay_journal()`
- `ubifs_validate_entry()`

## Important Behavior

Replay first marks the index head LEB as taken and validates that the master-recorded index-head offset matches lprops free space.

`replay_log_leb()` scans the log from `lhead_lnum`, requires the first node to be a commit-start node for the current commit, records `cs_sqnum`, initializes and updates the log hash, validates reference nodes, and adds buds to the replay list. It stops when it reaches an empty/out-of-date log LEB.

`add_replay_bud()` creates a `ubifs_bud`, snapshots the current log hash state into the bud, inserts the bud into UBIFS bud tracking, and records the bud in replay order.

`replay_bud()` scans each bud. If recovery is needed and the bud is the last in its journal head, it uses `ubifs_recover_leb()` so power-cut tail corruption can be repaired. It authenticates nodes when authentication is enabled, accepts unauthenticated trailing nodes only on the last bud, builds replay entries for inode/data/dentry/xentry/truncation nodes, and calculates bud dirty/free space.

Replay entries are sorted by sequence number before application. Directory and xattr entries use name-aware TNC operations. Deletions remove keys, truncation replay removes affected data-node ranges, and inode deletion removes all inode keys unless a later replay entry relinks the inode, which handles `O_TMPFILE` relink cases.

When recovery is active, applied replay entries feed `ubifs_recover_size_accum()` so inode sizes can later be reconciled.

`set_bud_lprops()` updates lprops after replay. It accounts for buds that started at offset zero after garbage collection without an intervening commit, marks bud LEBs taken, and seeks journal-head write buffers to the replayed endpoint.

Finally, `ubifs_replay_journal()` initializes `bi.uncommitted_idx` from dirty znode count and clears replay lists/bud lists before returning.

## Dependencies

Uses log scanning/recovery, authentication hash/HMAC helpers, bud management, TNC add/remove APIs, lprops dirty lookup/change, write-buffer seek, recovery size accumulation, list sorting, and key/name helpers.

## Research Notes

Replay ordering is sequence-number based because journal heads race with each other. Authentication permits missing trailing auth coverage only on the last bud, matching the power-cut model. Lprops correction after replay is essential because bud data may include dirty padding, deletions, truncations, and overwritten nodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/replay.c -->