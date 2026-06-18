# Group Research: UBIFS LPT, Master, Orphans, Recovery, and Replay

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/lpt.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/lpt.c

## Role

Implements the UBIFS LEB Properties Tree (LPT): geometry calculation, default on-flash creation, compact bit-level node packing, lazy loading, lookup, dirty copy-on-write, authentication hashing, range scanning, and debug validation.

## Core Flow

The LPT is a miniature wandering tree stored between the log and orphan areas. It records free/dirty/index state for main-area LEBs and maintains its own LPT-area lprops table (`ltab`). The file supports:

- The small model, where the whole LPT can be rewritten.
- The big model, where LPT GC and the saved-LEB table (`lsave`) avoid full scans at mount.

`ubifs_calc_lpt_geom()` and `calc_dflt_lpt_geom()` derive tree height, pnode/nnode counts, bit widths, packed node sizes, `ltab`/`lsave` sizes, and space requirements. The default creation path writes initial pnodes, nnodes, optional `lsave`, and `ltab`, while calculating the authenticated LPT hash.

## Packing and Lookup

LPT nodes do not use normal UBIFS common headers. `pack_bits()` and `ubifs_unpack_bits()` encode dense bit fields with CRC16. Pnodes store main-area free/dirty/index state, nnodes store child LPT locations, `ltab` stores LPT-area free/dirty state, and `lsave` stores useful main-area LEB numbers.

Runtime lookup lazily reads nnodes and pnodes from flash, validates node numbers, branch ranges, offsets, free/dirty alignment, and category invariants, then inserts loaded pnode lprops into category heaps/lists.

`ubifs_lpt_lookup_dirty()` walks the same path but marks nodes dirty. If a cnode is currently being committed, it performs copy-on-write and replaces category pointers so concurrent commit state remains consistent.

## Scanning and Authentication

`ubifs_lpt_calc_hash()` hashes packed pnodes for authenticated UBIFS and `lpt_check_hash()` compares that hash with the master-node value.

`ubifs_lpt_scan_nolock()` scans lprops across a requested LEB range with wraparound support. The callback may request that scanned path nodes be materialized into the in-memory tree and category structures.

## Research Notes

This file is the runtime core of LPT. Its correctness depends on exact geometry agreement with superblock/master metadata, bit-level packing compatibility, CRC/type validation, and careful COW during commit. Most higher lprops selection, GC, budgeting, and replay code depends on these lookups returning category-consistent lprops.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/lpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/lpt_commit.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/lpt_commit.c

## Role

Implements commit-time handling for the UBIFS LPT: collecting dirty cnodes, assigning their new locations, writing them, maintaining LPT-area free/dirty accounting, running LPT garbage collection, and freeing LPT resources.

## Commit Flow

`ubifs_lpt_start_commit()` freezes dirty LPT state under `lp_mutex`. It validates debug accounting, handles free-space checks, starts trivial GC, dirties the full tree for small-LPT low-space cases, populates `lsave` for big LPT, builds the circular dirty-cnode list, lays out new locations, computes the LPT hash into the master node, and snapshots `ltab` into `ltab_cmt`.

`layout_cnodes()` assigns future locations for dirty pnodes/nnodes, `ltab`, and optional `lsave` without writing. `write_cnodes()` repeats the same allocation sequence via `realloc_lpt_leb()`, packs nodes into `lpt_buf`, writes aligned chunks, clears `DIRTY_CNODE`/`COW_CNODE` with memory barriers, and updates the LPT head.

`ubifs_lpt_end_commit()` writes the frozen dirty cnodes and frees obsolete COW copies. `ubifs_lpt_post_commit()` completes trivial GC and, for big LPT, runs LPT GC until enough free space exists.

## LPT Garbage Collection

Big-LPT GC selects a dirty LPT LEB, scans it for valid LPT nodes using type/CRC recognition, and marks still-current nodes dirty. Obsolete nodes are ignored. After a later commit rewrites current nodes elsewhere, the selected LEB becomes reusable.

Trivial GC marks LPT LEBs containing only dirty/free bytes reusable after the master node has committed.

## Debug and Cleanup

The file includes extensive debug checks for `ltab` consistency, LPT free space, written size, node dirtiness, and LPT LEB dumps. `ubifs_lpt_free()` frees write-only resources first, then loaded tree nodes, heaps, `ltab`, and node buffers.

## Research Notes

The critical invariant is that layout-time allocation and write-time allocation must match exactly. The file also owns the commit-facing side of LPT COW, so flag ordering and memory barriers are part of correctness, not just optimization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/lpt_commit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/master.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/master.c

## Role

Reads, validates, authenticates, recovers through the recovery path, and writes the replicated UBIFS master node.

## Core Flow

UBIFS stores two master-node copies in adjacent LEBs. `scan_for_master()` scans both master LEBs and accepts them only when node counts, offsets, and master payloads agree. `ubifs_compare_master_node()` deliberately skips the common node header and embedded HMAC because sequence numbers, CRCs, and HMACs differ between the two copies.

On `-EUCLEAN`, `ubifs_read_master()` delegates to `ubifs_recover_master_node()`. After a valid master is selected, it copies fields into `struct ubifs_info`: sequence numbers, commit number, root index branch, log head, GC LEB, index head, LPT root/head/table/save locations, lprops totals, and resize information.

## Validation and Writes

`validate_master()` checks sequence-number watermarks, inode-number limits, log/index/LPT/orphan-related positions, lprops totals, and main-area space accounting.

`ubifs_write_master()` writes the current master node to both master LEBs. It advances within the master LEB until space runs out, unmaps when wrapping to offset zero, updates `highest_inum`, stores the root-index hash, and writes HMAC-protected nodes when authentication is enabled.

## Research Notes

The master node is the bridge between mount-time discovery and every persistent UBIFS subsystem. Its validation protects LPT, log, replay, GC, and index code from using impossible persisted coordinates or accounting totals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/master.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/misc.c

## Role

Provides UBIFS message helpers and assertion-action naming.

## Core Flow

`ubifs_msg()`, `ubifs_err()`, and `ubifs_warn()` wrap kernel logging with UBIFS volume identity. Error and warning helpers include the current PID and caller return address, which makes failure reports traceable to the subsystem call site.

`ubifs_assert_action_name()` maps assertion actions to readable names: report, read-only, and panic.

## Research Notes

This file is small but globally visible. Its logging helpers are used throughout UBIFS recovery, replay, LPT, journal, and validation paths to produce consistent diagnostics tied to the UBI volume.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/misc.h -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/misc.h

## Role

Defines small shared UBIFS inline helpers used across TNC, journal, lprops, compression, write-buffer, index, and log code.

## Key Helpers

The file provides:

- Znode flag checks for dirty, obsolete, and COW state.
- Background-thread wakeup.
- TNC child lookup and VFS inode to UBIFS inode conversion.
- Compressor presence/name helpers.
- Locked write-buffer sync wrapper.
- Device-number encoding for special files.
- Lprops helpers for adding dirty space and returning taken LEBs.
- Index node sizing and branch/key pointer helpers.
- `ubifs_tnc_lookup()` wrapper around `ubifs_tnc_locate()`.
- Lprops lock acquire/release helpers.
- Circular log LEB advancement.
- Xattr count limit calculation tied to orphan capacity.

## Research Notes

This header concentrates cross-subsystem glue rather than policy. Several helpers encode assumptions used elsewhere, especially index node layout, lprops locking assertions, log wraparound, and the relationship between xattr inode count and orphan capacity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/orphan.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/orphan.c

## Role

Implements UBIFS orphan tracking for inodes committed with link count zero, including in-memory rb-tree/list management, commit-time orphan-area writes, mount-time orphan recovery, and debug verification.

## Runtime Tracking

`ubifs_add_orphan()` inserts an inode number into the orphan rb-tree, global orphan list, and new-orphan list. It enforces `max_orphans` and rejects duplicate orphaning.

`ubifs_delete_orphan()` removes an orphan when the inode is finally deleted. If the orphan is currently part of a commit, deletion is deferred through `orph_dnext` until commit end.

`ubifs_orphan_start_commit()` freezes new orphans into the commit list, clears the new list, records `cmt_orphans`, and updates the `no_orphs` flag.

## On-Flash Orphan Area

The orphan area is a fixed set of LEBs between the LPT and main areas. Orphan nodes contain arrays of inode numbers. The last orphan node for a commit sets the high bit of `cmt_no`.

`commit_orphans()` writes all frozen orphans. If available tail space is insufficient, `consolidate()` rewrites all non-new orphans atomically from the beginning of the orphan area. `ubifs_clear_orphans()` unmaps the orphan area after clean mounts when mounted read-write.

## Recovery

On unclean mount, `kill_orphans()` scans orphan LEBs. `do_kill_orphans()` validates orphan nodes, tracks commit ordering and last-node markers, and removes zero-link inode trees from the TNC. It protects O_TMPFILE rebirth by checking the inode node before deleting.

Out-of-date orphan LEBs are detected by commit-number ordering after a flagged last node.

## Debug

Debug code scans orphan nodes into a check tree, walks the index, and verifies that every zero-link inode is represented either on flash or in the in-memory orphan tree.

## Research Notes

The orphan file preserves unlink semantics across power loss without scanning the full index in normal recovery. Its safety depends on commit-number markers, atomic consolidation, and deferring deletion of orphans that are being committed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/recovery.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/recovery.c

## Role

Implements mount-time recovery from unclean unmounts: master-node recovery, journal/log LEB cleanup, index/LPT head cleanup, deferred read-only cleanup, GC recovery commit, and inode-size recovery.

## Recovery Model

The file’s central assumption is that UBIFS writes sequentially into erased space. If corruption appears after a power cut, only the min-I/O region being written and later empty space may be damaged. If later non-empty data exists, UBIFS treats it as unrecoverable corruption.

## Master Recovery

`ubifs_recover_master_node()` reads both master LEBs with `get_master_node()`, accepts only valid combinations of last good master nodes and plausible single corruption areas, and writes a recovered master node unless mounted read-only. Read-only recovery stores a copy in `rcvrd_mst_node` and marks the in-memory master dirty so remount-rw completes recovery.

`ubifs_write_rcvrd_mst_node()` writes that deferred recovered master when switching to read-write.

## LEB Recovery

`ubifs_recover_leb()` scans nodes while tolerating corruption only at the writable tail. It drops incomplete grouped nodes, has special GC-head handling that drops all nodes in the corrupted min-I/O unit, pads/cleans the tail, and either fixes the LEB immediately or records it for later read-only cleanup.

`ubifs_recover_log_leb()` restricts log recovery to the log tail and uses commit-start sequence numbers to detect unrecoverable newer data.

`ubifs_clean_lebs()` later writes back LEBs deferred during read-only mount.

## Commit and GC Recovery

`ubifs_recover_inl_heads()` cleans the index and LPT heads after half-completed commits.

`ubifs_rcvry_gc_commit()` reestablishes a GC LEB after unclean unmount. It either grabs an empty LEB before commit or commits first and garbage-collects a dirty LEB into the GC head, preserving replay and orphan-deletion ordering.

## Size Recovery

Replay records possible inode-size discrepancies through `ubifs_recover_size_accum()`. `ubifs_recover_size()` removes data for missing inodes and fixes inode sizes that are smaller than replayed data. It can either journal a corrected inode or patch the inode node in place.

## Research Notes

This file encodes UBIFS’s power-cut boundary rules. It is intentionally conservative: it repairs corruption patterns compatible with interrupted writes and rejects patterns that imply older data was overwritten or unexpected data exists after the corruption point.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/replay.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/replay.c

## Role

Implements UBIFS journal replay at mount. It scans the log, reconstructs bud lists, scans bud LEBs, authenticates journal data when enabled, sorts replay entries by sequence number, applies them to the TNC, updates lprops, and initializes budgeting state.

## Log Replay

`ubifs_replay_journal()` first marks the index head LEB as taken and validates `ihead_offs` against lprops free space. It then walks the circular log from `lhead_lnum`.

`replay_log_leb()` requires the first log node to be the current commit-start node, records `cs_sqnum`, hashes log nodes for authenticated mode, validates bud reference nodes, and adds each bud to both the UBIFS bud tree and the replay-bud list. Older log data is detected by sequence numbers lower than `cs_sqnum`.

## Bud Replay

`replay_bud()` scans each bud. Only the last bud in a journal head may be recovered from power-cut corruption. It authenticates nodes against auth nodes; unauthenticated tail nodes are ignored only on the last bud.

The scanner converts inode, data, dent, xent, and truncation nodes into replay entries. Deletion entries represent zero-link inode nodes, deleted dent/xent nodes, and truncation ranges. It tracks used, dirty, and free bytes for later lprops correction.

`ubifs_validate_entry()` validates dent/xent length, type, key type, name termination, xattr-name constraints, and inode number.

## Applying Replay

Replay entries are sorted by node sequence number. `apply_replay_entry()` then updates the TNC:

- Adds or removes hash-keyed dent/xent nodes with names.
- Removes whole inode trees for deletion inode nodes unless a later inode entry relinks the inode.
- Removes truncation ranges.
- Adds non-deletion nodes by key and physical location.
- Accumulates inode-size recovery data when recovery is active.

`set_buds_lprops()` updates bud LEB free/dirty accounting and seeks journal write buffers to the recovered tail offsets. It includes special handling for buds that started at offset zero after GC without an intervening commit.

## Research Notes

Replay is the mount-time bridge between committed index state and uncommitted journal data. Its ordering depends on sequence numbers, while its safety depends on log reference validation, last-bud recovery limits, authenticated-node handling, and final lprops/write-buffer reconstruction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/replay.c -->