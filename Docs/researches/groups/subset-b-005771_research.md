# subset-b-005771 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/lpt.c

## Purpose
`lpt.c` implements the read-side, formatting, packing, validation, lookup, hashing, and scan mechanics for UBIFS's LEB Properties Tree (LPT). The LPT is a flash-resident wandering tree that stores per-main-LEB free/dirty/index-category metadata in pnodes, internal nnode branches, an LPT-area lprops table (`ltab`), and, for big LPTs, an `lsave` table of useful main-area LEBs to pre-load at mount.

## Important APIs, Types, and Functions
Key exported functions are `ubifs_calc_lpt_geom()`, `ubifs_create_dflt_lpt()`, `ubifs_pack_pnode()`, `ubifs_pack_nnode()`, `ubifs_pack_ltab()`, `ubifs_pack_lsave()`, `ubifs_unpack_bits()`, `ubifs_unpack_nnode()`, `ubifs_read_nnode()`, `ubifs_get_nnode()`, `ubifs_get_pnode()`, `ubifs_pnode_lookup()`, `ubifs_lpt_lookup()`, `ubifs_lpt_lookup_dirty()`, `ubifs_lpt_calc_hash()`, `ubifs_lpt_init()`, `ubifs_lpt_scan_nolock()`, and debug validator `dbg_check_lpt_nodes()`. The major in-memory objects are `struct ubifs_nnode`, `struct ubifs_pnode`, `struct ubifs_lprops`, `struct ubifs_lpt_lprops`, and `struct lpt_scan_node`.

## Control Flow
Geometry setup starts with `do_calc_lpt_geom()`, which derives tree height, pnode/nnode counts, packed bit widths, and total LPT size. `ubifs_calc_lpt_geom()` validates an existing superblock geometry, while `calc_dflt_lpt_geom()` iteratively chooses default small or big LPT sizing for formatting. `ubifs_create_dflt_lpt()` then writes initial pnodes, builds parent nnodes bottom-up, records root/ltab/lsave/head locations, computes the LPT hash, and initializes the first root/index/inode LEB properties.

Runtime reads are lazy. `ubifs_pnode_lookup()` descends from `c->nroot`, using `ubifs_read_nnode()` and `read_pnode()` only when an nnode or pnode is absent from memory. A zero flash branch is treated as an unwritten all-empty subtree. Dirty lookups use `ubifs_lpt_lookup_dirty()`, which performs copy-on-write through `dirty_cow_nnode()` and `dirty_cow_pnode()` when commit has marked existing cnodes with `COW_CNODE`.

## State and Persistence
Packed LPT nodes do not use normal UBIFS common headers. Bitfields are compacted by `pack_bits()` and `ubifs_unpack_bits()`, with crc16 stored at the front. Pnodes persist per-main-LEB `free`, `dirty`, and `LPROPS_INDEX`; category flags are reconstructed in memory by `ubifs_categorize_lprops()`. Nnodes persist branch `(lnum, offs)` pairs. `ltab` persists free/dirty accounting for the LPT area itself. `lsave` persists a small cache of main LEB numbers. `ubifs_lpt_calc_hash()` hashes packed pnodes for authenticated mounts and is checked by `lpt_check_hash()` against the master node.

## Dependencies and Integration Points
The file depends on UBI IO helpers (`ubifs_leb_read()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`), LEB-property category helpers (`ubifs_add_to_cat()`, `ubifs_replace_cat()`, `ubifs_ensure_cat()`), cryptographic hash helpers, CRC16, allocation wrappers, and master-node fields (`c->mst_node->hash_lpt`). `find.c`, `lprops.c`, replay, GC, and budgeting consume `ubifs_lpt_lookup*()` and `ubifs_lpt_scan_nolock()`.

## Risks and Test Signals
High-risk areas are bit-width math, CRC/type validation, big-vs-small numbering, automatic resize handling in `read_lsave()`, COW parent replacement during commit, and category-list replacement after pnode copy. Tests should stress format/mount on small and large volumes, authenticated mount hash mismatch, corrupt LPT CRC/type/branch offsets, resize with stale lsave values, concurrent lprops updates during commit, and full LPT scans that request `LPT_SCAN_ADD` while validating category lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt_commit.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/lpt_commit.c

## Purpose
`lpt_commit.c` implements commit-time persistence and garbage collection for the LPT. It freezes dirty LPT cnodes, lays them out in free LPT space, writes packed nodes plus `ltab`/`lsave`, frees obsolete COW copies, and keeps enough LPT free space available through trivial GC and big-LPT node relocation.

## Important APIs, Types, and Functions
The public entry points are `ubifs_lpt_start_commit()`, `ubifs_lpt_end_commit()`, `ubifs_lpt_post_commit()`, `ubifs_lpt_free()`, `dbg_check_ltab()`, `dbg_chk_lpt_free_spc()`, `dbg_chk_lpt_sz()`, and `ubifs_dump_lpt_lebs()`. Core private functions include `get_cnodes_to_commit()`, `layout_cnodes()`, `write_cnodes()`, `make_tree_dirty()`, `need_write_all()`, `lpt_tgc_start()`, `lpt_tgc_end()`, `populate_lsave()`, `lpt_gc()`, and `lpt_gc_lnum()`.

## Control Flow
Commit begins in `ubifs_lpt_start_commit()`. Under `lp_mutex`, it runs debug checks, optionally performs big-LPT GC until there is enough future free space, marks trivial-GC LEBs, makes the whole tree dirty for small LPTs when free space is low, populates `lsave`, builds a circular `cnext` list of currently dirty cnodes, and calls `layout_cnodes()` to assign new flash addresses. It then computes the LPT hash into the master node and snapshots `c->ltab` into `c->ltab_cmt`.

`ubifs_lpt_end_commit()` writes the frozen cnode list with `write_cnodes()`. This function repeats the same LEB allocation decisions using `realloc_lpt_leb()`, packs each nnode/pnode, writes aligned chunks, and clears `DIRTY_CNODE`/`COW_CNODE` with memory barriers so readers/writers see a coherent post-commit state. `ubifs_lpt_post_commit()` unmaps trivially collected LPT LEBs and, for big LPTs, runs relocation GC until `need_write_all()` is false.

## State and Persistence
The commit path maintains `c->lpt_cnext`, `dirty_nn_cnt`, `dirty_pn_cnt`, `lpt_drty_flgs`, `ltab[].free/dirty/tgc/cmt`, `ltab_cmt`, `lsave`, `nhead_lnum/off`, and root/ltab/lsave locations. Start commit is a planning/freeze phase; end commit is the physical write phase. Nodes obsolete because of COW are kept until after successful writing, then `free_obsolete_cnodes()` releases them.

## Dependencies and Integration Points
The file depends on packing functions from `lpt.c`, lazy node lookup helpers, UBI write/unmap operations, lprops locking, category state, cryptographic LPT hashing, and UBIFS commit orchestration in `commit.c`. `recovery.c` cleans the LPT head after failed commits, and `master.c` persists the new LPT root/head/table locations and hash.

## Risks and Test Signals
The main risks are divergence between `layout_cnodes()` and `write_cnodes()`, wrong `ltab` accounting, failure to clear COW after writes, LPT out-of-space loops, and GC mistaking current nodes for obsolete nodes. Useful tests include power-cut injection across start/end/post commit, forced small-LPT whole-tree rewrite, big-LPT GC with fragmented LPT area, random `lsave` debug population, corrupted LPT padding/CRC during debug scans, and memory-failure paths in obsolete-node cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/master.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/master.c

## Purpose
`master.c` reads, validates, authenticates, and writes the UBIFS master node. The master node is the mount-time root of durable filesystem state: log head, index root, LPT root/head/table positions, GC LEB, counters, orphan flag, space statistics, and authentication hashes.

## Important APIs, Types, and Functions
Public functions are `ubifs_compare_master_node()`, `ubifs_read_master()`, and `ubifs_write_master()`. Private helpers are `mst_node_check_hash()`, `scan_for_master()`, and `validate_master()`. Important persistent type is `struct ubifs_mst_node`; important in-memory targets are fields in `struct ubifs_info` such as `zroot`, `lhead_lnum/off`, `ihead_lnum/off`, `lpt_lnum/off`, `nhead_lnum/off`, `ltab_lnum/off`, `lsave_lnum/off`, `lscan_lnum`, `lst`, `bi.old_idx_sz`, `cmt_no`, and `highest_inum`.

## Control Flow
`ubifs_read_master()` allocates `c->mst_node`, calls `scan_for_master()`, falls back to `ubifs_recover_master_node()` on `-EUCLEAN`, clears the recovery flag, copies little-endian master fields into `ubifs_info`, handles volume auto-resize, validates all ranges and counters, and initializes old-index debug checking. `scan_for_master()` scans both master LEBs, requires matching last master nodes at the same offset, ignores common headers and embedded HMAC differences when comparing, and verifies either the superblock master hash or node HMAC for authenticated filesystems.

`ubifs_write_master()` advances `c->mst_offs` by aligned master-node size, unmaps both master LEBs when wrapping, updates `highest_inum` and root-index hash, and writes the same master node to the two master LEBs with HMAC support.

## State and Persistence
Two master copies are maintained for recovery. The common header sequence number and CRC intentionally differ, so comparisons exclude that region; authenticated comparisons also account for HMAC differences. The master node stores the authoritative persistent pointers used by LPT, replay, orphan recovery, and index loading. The `UBIFS_MST_NO_ORPHS` flag becomes `c->no_orphs`; resize updates empty/free/dark totals in memory and in the master buffer for the next write.

## Dependencies and Integration Points
This file depends on scan/recovery (`ubifs_scan()`, `ubifs_recover_master_node()`), node/HMAC/hash helpers, dump/debug helpers, and validation constants from `ubifs.h`. Mount code in `super.c` calls `ubifs_read_master()` before LPT/replay/orphan processing and writes the master during mount/remount/unmount and commit completion.

## Risks and Test Signals
Key risks are accepting mismatched master copies, stale or invalid LPT/index/log pointers, authenticated hash/HMAC regressions, counter overflow near watermarks, resize accounting mistakes, and write wrap-around behavior. Tests should cover single-copy corruption, mismatched offsets, recovery marker handling, authenticated and unauthenticated images, invalid space-stat fields, small master LEB wrap, and resize from older `leb_cnt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/misc.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/misc.c

## Purpose
`misc.c` contains small global UBIFS helpers that do not belong to a larger subsystem: formatted informational, warning, and error logging, plus conversion of the configured assert action to a readable string.

## Important APIs, Types, and Functions
Exported functions are `ubifs_msg()`, `ubifs_err()`, `ubifs_warn()`, and `ubifs_assert_action_name()`. They use `struct ubifs_info` for UBI volume identifiers and assert configuration, Linux `va_format` for varargs logging, `current->pid`, and `__builtin_return_address(0)` for error/warning call-site reporting.

## Control Flow
Each logging function starts a `va_list`, wraps it in `struct va_format`, emits a prefixed kernel log line, and closes the list. `ubifs_msg()` uses `pr_notice()` with `UBIFS (ubiX:Y)`. `ubifs_err()` uses `pr_err()` and includes pid and caller symbol. `ubifs_warn()` uses `pr_warn()` with the same pid/caller context. `ubifs_assert_action_name()` indexes the static `assert_names[]` table by `c->assert_action`.

## State and Persistence
There is no on-flash persistence and no mutable filesystem state except log output. The only local state is the static mapping for `ASSACT_REPORT`, `ASSACT_RO`, and `ASSACT_PANIC`.

## Dependencies and Integration Points
All UBIFS modules use these helpers for consistent diagnostics. The helpers depend on Linux kernel logging APIs and `ubifs_info.vi` fields. They are especially important on recovery and validation paths where the caller location helps identify which consistency check failed.

## Risks and Test Signals
Risk is low but nonzero: out-of-range `assert_action` would index past `assert_names`, and logging macros must be safe in error paths. Test signals are compile coverage, boot/mount logs including correct ubi/volume ids, warning/error caller symbols, and assert-action configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/misc.h -->
# sources/distributed-fs/ceph-client/fs/ubifs/misc.h

## Purpose
`misc.h` provides inline helpers used throughout UBIFS for znode flag checks, background-thread wakeups, inode/container conversion, compressor metadata, write-buffer sync, device encoding, lprops lock/unlock and simple updates, index-node layout calculations, log LEB wraparound, xattr limits, and TNC lookup shorthand.

## Important APIs, Types, and Functions
Important helpers include `ubifs_zn_dirty()`, `ubifs_zn_obsolete()`, `ubifs_zn_cow()`, `ubifs_wake_up_bgt()`, `ubifs_tnc_find_child()`, `ubifs_inode()`, `ubifs_compr_present()`, `ubifs_compr_name()`, `ubifs_wbuf_sync()`, `ubifs_encode_dev()`, `ubifs_add_dirt()`, `ubifs_return_leb()`, `ubifs_idx_node_sz()`, `ubifs_idx_branch()`, `ubifs_idx_key()`, `ubifs_tnc_lookup()`, `ubifs_get_lprops()`, `ubifs_release_lprops()`, `ubifs_next_log_lnum()`, and `ubifs_xattr_max_cnt()`.

## Control Flow
Most helpers are single-purpose wrappers. Flag helpers read bits from znode flags. `ubifs_wake_up_bgt()` sets `need_bgt` and wakes the background thread only when present and not already requested. `ubifs_wbuf_sync()` locks the write-buffer mutex using the journal-head subclass, calls the nolock sync, and unlocks. Lprops helpers encapsulate `lp_mutex`, single-LEB dirty addition, and clearing `LPROPS_TAKEN`. Index helpers compute variable-size index-node branch/key locations using runtime `key_len` and `hash_len`. `ubifs_next_log_lnum()` wraps from `log_last` to `UBIFS_LOG_LNUM`.

## State and Persistence
The header itself persists nothing, but it gates important state transitions: `ubifs_get_lprops()`/`ubifs_release_lprops()` protect LPT/lprops state, `ubifs_add_dirt()` changes free/dirty accounting, `ubifs_return_leb()` returns taken LEBs to allocators, and write-buffer sync can make journal data durable.

## Dependencies and Integration Points
This header is included widely by UBIFS C files. It depends on VFS `struct inode`, UBIFS compressor table, TNC locate, lprops mutation functions, write-buffer operations, Linux device-number encoders, mutex and bit APIs, and core constants from `ubifs.h`. The helpers are used by LPT commit/replay/recovery code in this group.

## Risks and Test Signals
Risks cluster around assumptions hidden by inline wrappers: callers must balance lprops locking, not call `ubifs_wbuf_sync()` while already holding the same mutex, provide valid compressor/action indexes, and pass index child counts that match allocated memory. Test signals include lockdep coverage on lprops and wbuf paths, lprops accounting assertions, index-node size/addressing tests under authentication hash lengths, and log wraparound replay tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/orphan.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/orphan.c

## Purpose
`orphan.c` manages inode numbers whose inode node has reached link count zero but whose storage must survive until open references are closed or crash recovery deletes them. It keeps an in-memory orphan tree/list during runtime, writes orphan nodes during commit, consolidates the fixed orphan area when space is low, and kills persisted orphans after unclean unmount.

## Important APIs, Types, and Functions
Public functions are `ubifs_add_orphan()`, `ubifs_delete_orphan()`, `ubifs_orphan_start_commit()`, `ubifs_orphan_end_commit()`, `ubifs_clear_orphans()`, and `ubifs_mount_orphans()`. Key private functions include `lookup_orphan()`, `orphan_delete()`, `avail_orphs()`, `tot_avail_orphs()`, `write_orph_node()`, `consolidate()`, `commit_orphans()`, `erase_deleted()`, `do_kill_orphans()`, and `kill_orphans()`. Runtime state lives in `c->orph_tree`, `orph_list`, `orph_new`, `orph_cnext`, `orph_dnext`, counters, `ohead_lnum/off`, and `orph_buf`.

## Control Flow
`ubifs_add_orphan()` allocates an orphan, inserts it into an rb-tree keyed by inode number, appends it to global and new lists, and enforces `c->max_orphans`. `ubifs_delete_orphan()` removes or defers deletion depending on whether the orphan is currently in a commit snapshot. Commit begins with `ubifs_orphan_start_commit()`, which moves all new orphans to a `cnext` chain, clears `orph_new`, and updates `no_orphs`.

`ubifs_orphan_end_commit()` writes pending orphan nodes via `commit_orphans()` and then frees delayed deletions. If the tail has insufficient room, `consolidate()` rewrites all non-new orphans from the beginning of the orphan area using atomic LEB changes and unmaps unused LEBs. Mount calls `ubifs_mount_orphans()`: clean writable mounts erase the orphan area, while unclean mounts scan orphan nodes with `kill_orphans()` and remove zero-link inodes from TNC.

## State and Persistence
Persistent orphan nodes contain `cmt_no` plus inode numbers; the high bit of `cmt_no` marks the last orphan node for that commit. This lets recovery ignore out-of-date LEBs after a fully marked newer commit. In-memory flags `new`, `cmt`, and `del` prevent losing orphans across commit/delete races. The fixed orphan area lies between LPT and main area, and `ohead_lnum/off` tracks append position.

## Dependencies and Integration Points
The file integrates with VFS unlink/open semantics, UBIFS commit sequencing, TNC removal (`ubifs_tnc_remove_ino()`), inode lookup (`ubifs_tnc_lookup()`), scanning/recovery (`ubifs_scan()`, `ubifs_recover_leb()`), master `no_orphs`, and debug index walks. Recovery ordering matters with `recovery.c` GC commit and `replay.c` TNC updates.

## Risks and Test Signals
Risks include orphan-area exhaustion, duplicate/missing orphan entries, incorrect `cmt_no` ordering, deletion during commit, O_TMPFILE/linkat rebirth, read-only recovery deferral, and corruption inside orphan LEBs. Tests should cover unlink-open-crash, multiple orphan nodes per commit, consolidation under pressure, clean mount clearing, unclean mount killing, out-of-date orphan LEBs, delayed deletion lists, and debug `dbg_check_orphans()` walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/orphan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/recovery.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/recovery.c

## Purpose
`recovery.c` implements UBIFS crash recovery for master nodes, log/bud LEBs, index/LPT heads, deferred read-only cleanup, GC state, and inode-size inconsistencies. It accepts corruption patterns consistent with interrupted flash writes and rejects patterns that imply older or unrelated corruption.

## Important APIs, Types, and Functions
Public entry points are `ubifs_recover_master_node()`, `ubifs_write_rcvrd_mst_node()`, `ubifs_recover_leb()`, `ubifs_recover_log_leb()`, `ubifs_recover_inl_heads()`, `ubifs_clean_lebs()`, `ubifs_rcvry_gc_commit()`, `ubifs_recover_size_accum()`, `ubifs_recover_size()`, and `ubifs_destroy_size_tree()`. Important private helpers are `get_master_node()`, `write_rcvrd_mst_node()`, `is_last_write()`, `no_more_nodes()`, `fix_unclean_leb()`, `drop_last_group()`, `drop_last_node()`, `recover_head()`, `grab_empty_leb()`, `fix_size_in_place()`, and `inode_fix_size()`.

## Control Flow
Master recovery scans both master LEBs with `get_master_node()`, tolerates one last-write corruption area, chooses the newest valid consistent copy, and either writes a recovery-marked master immediately or stores it for later read-write remount. Generic LEB recovery scans nodes until empty/garbage/bad padding/corruption, verifies the problem is at the last plausible write, drops incomplete grouped nodes and special GC-head min-I/O content, pads/cleans the rest, and writes the fixed LEB unless mounted read-only.

`ubifs_recover_log_leb()` only permits recovery at the log end by comparing the next log LEB against the commit-start sequence. `ubifs_recover_inl_heads()` cleans index and LPT head locations left by half-completed commits. `ubifs_rcvry_gc_commit()` reconstructs a valid GC LEB, runs a commit to persist replay/orphan/size fixes, and may garbage-collect a dirty LEB into the GC head. Size recovery accumulates journal inode/data/truncation observations into an rb-tree, then removes data without an inode or grows inode sizes either in-place or through journal writes.

## State and Persistence
The file manipulates `rcvrd_mst_node`, `unclean_leb_list`, `gc_lnum`, journal-head write buffers, `size_tree`, pinned inodes, and master dirty/recovery flags. It deliberately avoids flash modification during read-only mount, recording pending cleanups for `ubifs_clean_lebs()` and `ubifs_write_rcvrd_mst_node()` when remounted writable.

## Dependencies and Integration Points
Recovery depends on scanner/node validation, UBI read/change/unmap APIs, journal heads, log commit-start nodes, lprops and GC selection, TNC lookup/removal, inode journal writes, LPT/master/orphan replay ordering, and authenticated node preparation. `super.c`, `replay.c`, and `orphan.c` call into these helpers during mount and remount.

## Risks and Test Signals
Risks are over-accepting real corruption, under-accepting valid power-cut tails, mishandling grouped nodes or GC head padding, failing read-only deferral, choosing the wrong master copy, and ordering GC/orphan/size commits incorrectly. Tests should use power-cut/failure-mode emulation across master writes, log tail writes, bud writes, GC head writes, index/LPT head writes, readonly-to-rw remount, orphan deletion, and inode-size replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/replay.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/replay.c

## Purpose
`replay.c` reconstructs the in-memory view of uncommitted journal data during mount. It scans the log for bud references, scans/recover/authenticates bud LEBs, builds sequence-ordered replay entries, applies them to the TNC, updates bud lprops and journal write-buffer heads, and feeds size recovery when the filesystem was not cleanly unmounted.

## Important APIs, Types, and Functions
The main public function is `ubifs_replay_journal()`, with public validator `ubifs_validate_entry()`. Key local types are `struct replay_entry` and `struct bud_entry`. Important helpers include `take_ihead()`, `replay_log_leb()`, `validate_ref()`, `add_replay_bud()`, `replay_buds()`, `replay_bud()`, `authenticate_sleb()`, `insert_node()`, `insert_dent()`, `apply_replay_list()`, `apply_replay_entry()`, `inode_still_linked()`, `trun_remove_range()`, `set_buds_lprops()`, and `set_bud_lprops()`.

## Control Flow
`ubifs_replay_journal()` first marks the index head LEB taken and verifies `ihead_offs` matches LPT free space. It then walks the circular log from `lhead_lnum`, requiring the first node to be a commit-start node with the current commit number. `replay_log_leb()` validates reference nodes, updates the rolling log hash, creates `ubifs_bud` objects, and stops when it reaches old log data or empty space.

Each `replay_bud()` decides whether the bud is the last in its journal head; only last buds are recoverable after power cut. It scans or recovers the LEB, authenticates nodes when configured, converts inode/data/dent/xent/trunc nodes into replay entries, computes used/dirty/free bytes, and records maximum sqnum/inum. After all buds are scanned, entries are sorted by sqnum and applied to TNC. Deletions remove keys, inode deletions remove all inode keys unless a later O_TMPFILE relink exists, and truncation entries remove data-key ranges. Finally bud lprops are updated and journal write buffers seek to the recovered ends.

## State and Persistence
Replay does not directly persist new nodes; it reconstructs in-memory TNC, bud lists, dirty znodes, `max_sqnum`, `highest_inum`, lprops flags/free/dirty, write-buffer positions, `bi.uncommitted_idx`, and `size_tree` entries. Authentication nodes can cause unauthenticated tail nodes on the last bud to be ignored, but reject unauthenticated content in non-last buds.

## Dependencies and Integration Points
Replay depends on log format, scanner/recovery, HMAC/hash helpers, TNC add/remove APIs, lprops locking and LPT dirty lookup, journal-head write buffers, orphan/size recovery, key helpers, and master commit number/log pointers. It runs after master/LPT initialization and before mount completes, and its lprops changes influence GC and budgeting immediately.

## Risks and Test Signals
High-risk areas include log-end detection, duplicate/invalid reference nodes, sequence ordering, authenticated-tail handling, O_TMPFILE relink detection, truncation range math, bud lprops after GC-before-bud cases, and consistency between scan `endpt` and write-buffer seek positions. Tests should cover multi-head journal replay, corrupt last vs non-last buds, authenticated replay with missing auth node, dent/xent validation, unlink/relink sequences, truncation replay, GC'd bud starting at zero, and ENOSPC/budget behavior after replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/replay.c -->
