# Group Research: group_848_linux_sources_os_linux_linux_fs_ubifs_sb_c_sources_os_linux_linux_fs_9fdcebd7e04e

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/os/linux/linux`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/sb.c -->
# File Research: sources/os/linux/linux/fs/ubifs/sb.c

Read completely: 956 lines.

This file implements UBIFS superblock handling, including default filesystem creation on an empty UBI volume, superblock parsing and validation, authentication checks, free-space fixup, and enabling encryption.

Main entry points: `ubifs_read_superblock`, `ubifs_write_sb_node`, `ubifs_fixup_free_space`, and `ubifs_enable_encryption`.

Key behavior: `create_default_filesystem` formats an empty volume by deriving default journal/log/LPT/orphan/main-area geometry, creating the superblock, master node, root index node, root inode, and initial commit-start node. It also initializes authentication fields when authenticated mounting is requested and records hashes for LPT and root index metadata.

Superblock read path: `ubifs_read_superblock` reads the on-flash superblock, handles read-only compatibility for future format versions, chooses the key hash and key format, copies geometry and mount defaults into `struct ubifs_info`, authenticates the node, rejects unknown feature flags, auto-resizes to the UBI volume size when allowed, derives area boundaries, and calls `validate_sb`.

Validation and feature checks: `validate_sb` verifies min I/O and LEB size against the real UBI device, checks minimum counts for log/LPT/orphan/main areas, validates journal and fanout limits, checks reserved-pool and time-granularity bounds, and enforces format-version requirements for double hashing and encryption.

Authentication: `authenticate_sb_node` enforces consistency between mount authentication options and on-flash authentication flags, verifies hash algorithm selection, supports either superblock HMAC or an offline image signature node, and validates the well-known-message HMAC against the supplied key.

Free-space fixup: `ubifs_fixup_free_space` rewrites or unmaps LEBs containing free space when `UBIFS_FLG_SPACE_FIXUP` is set, then clears the flag and marks the superblock for rewrite. This protects NAND parts where apparent `0xff` free space may have been programmed with non-erased ECC.

Encryption enablement: `ubifs_enable_encryption` requires fscrypt support, read-write media, and format version 5 or newer, then sets `UBIFS_FLG_ENCRYPTION` in the superblock and writes it immediately.

Important interactions: `super.c` calls this file during mount and remount; LPT creation and lprops lookup are used for default formatting and space fixup; authentication helpers are supplied by UBIFS auth code; low-level node I/O and HMAC writing come from `io.c`.

Reliability notes: the superblock is normally immutable after formatting except for controlled flag/count updates. This file is therefore the gatekeeper for on-flash compatibility and must reject inconsistent geometry before later mount code trusts derived LEB ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/scan.c -->
# File Research: sources/os/linux/linux/fs/ubifs/scan.c

Read completely: 366 lines.

This file implements the generic UBIFS logical eraseblock scanner. It identifies valid UBIFS nodes, padding nodes/bytes, empty space, and corrupt regions within one LEB.

Main entry points: `ubifs_scan_a_node`, `ubifs_start_scan`, `ubifs_end_scan`, `ubifs_add_snod`, `ubifs_scanned_corruption`, `ubifs_scan`, and `ubifs_scan_destroy`.

Key behavior: `ubifs_scan` reads a full LEB into a caller-provided buffer, then walks from the requested offset in 8-byte-aligned increments. Valid nodes are added to a `struct ubifs_scan_leb` list as `struct ubifs_scan_node` records; padding nodes or padding bytes advance the scan; empty space terminates node scanning and is then verified as all `0xff`.

Node classification: `ubifs_scan_a_node` recognizes erased space by `0xffffffff` magic, validates UBIFS common headers through `ubifs_check_node`, handles `UBIFS_PAD_NODE` length and alignment checks, and returns scanner status codes that distinguish valid nodes, corrupt nodes, bad padding, padding bytes, empty space, and garbage.

Scanned-node records: `ubifs_add_snod` records sequence number, type, offset, length, backing node pointer, and key for inode/dentry/xentry/data nodes. Non-keyed nodes receive an invalid key marker.

Error handling: scan corruption returns `-EUCLEAN` after optionally dumping up to 8192 bytes from the corrupt offset. Other I/O or allocation errors return their negative errno and destroy partial scan state.

Important interactions: journal replay, garbage collection, in-the-gaps TNC commit, and debug checks use this scanner to reason about LEB contents. It depends on `io.c` validation and uses caller-owned scan buffers, so scan-node `node` pointers refer into `sleb->buf`.

Reliability notes: integrity read errors from UBI are tolerated at `ubifs_start_scan` time because individual UBIFS nodes are CRC checked. Empty-space alignment to `min_io_size` is enforced before the trailing `0xff` verification.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/shrinker.c -->
# File Research: sources/os/linux/linux/fs/ubifs/shrinker.c

Read completely: 319 lines.

This file implements the global UBIFS VM shrinker for reclaiming clean TNC znodes across all mounted UBIFS instances.

Main entry points: `ubifs_shrink_count` and `ubifs_shrink_scan`. Global state includes `ubifs_infos`, `ubifs_infos_lock`, `ubifs_clean_zn_cnt`, and the per-run `shrinker_run_no`.

Key behavior: `shrink_tnc` walks a filesystem's TNC in level-order and frees clean znodes older than the requested age. Because old clean subtree roots imply old clean descendants, entire subtrees can be detached and destroyed through `ubifs_destroy_tnc_subtree`.

Global scan policy: `shrink_tnc_trees` iterates mounted UBIFS instances, protects unmount races with `ubifs_infos_lock` and `c->umount_mutex`, uses `mutex_trylock` for both unmount and TNC locks, moves visited filesystems to the tail for fairness, and stops once enough znodes are reclaimed.

Commit prompting: when no clean znodes are globally available, `kick_a_thread` looks for a mounted writable filesystem with dirty znodes and a resting commit state, then requests background commit so dirty znodes may become clean and reclaimable later.

Age policy: `ubifs_shrink_scan` first tries `OLD_ZNODE_AGE`, then `YOUNG_ZNODE_AGE`, then age zero. If no nodes are freed but lock contention occurred, it returns `SHRINK_STOP`; otherwise it returns the number freed.

Important interactions: `super.c` registers the shrinker at module init and maintains `ubifs_infos` during mount/unmount. `tnc_misc.c` supplies level-order traversal and subtree destruction. `tnc_commit.c` updates clean/dirty znode counters after commit.

Reliability notes: znodes on the commit `cnext` ring are deliberately skipped because that list is not protected by the normal TNC mutex during commit. The clean-znode counters may briefly be negative by design, so `ubifs_shrink_count` clamps negative values to a nonzero retry hint.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/shrinker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/super.c -->
# File Research: sources/os/linux/linux/fs/ubifs/super.c

Read completely: 2515 lines.

This file implements UBIFS module initialization, filesystem context parsing, VFS superblock/inode operations, mount/remount/unmount orchestration, and most per-mount resource allocation and teardown.

Main entry points: `ubifs_iget`, `ubifs_super_operations`, `ubifs_init_fs_context`, `ubifs_get_tree` through `ubifs_context_ops`, module init `ubifs_init`, and module exit `ubifs_exit`.

Inode handling: `ubifs_iget` reads an inode node from the TNC, initializes VFS inode fields, validates UBIFS inode metadata, assigns operations by file type, loads xattr/symlink/device inline data, sets UBIFS inode flags, and unlocks the inode. `ubifs_write_inode`, `ubifs_evict_inode`, `ubifs_dirty_inode`, `ubifs_drop_inode`, and slab allocation/free functions implement VFS inode lifecycle and UBIFS dirty-budget release.

Superblock operations: `ubifs_statfs` reports free space after reserved-pool adjustment; `ubifs_show_options` prints active mount options; `ubifs_sync_fs` synchronizes all journal write buffers, runs a commit, and calls `ubi_sync`.

Constants and geometry: `init_constants_early` derives UBI geometry, node length ranges, write sizes, watermarks, bulk-read buffer limits, and basic device validity before reading the superblock. `init_constants_sb` derives fanout-dependent index sizes, journal limits, budgeting constants, background-commit thresholds, and LPT geometry. `init_constants_master` computes minimum index LEBs, reported reserved-pool size, and `statfs` block count after master-node load.

Mount options: the fs-context parser handles legacy unmount mode, bulk read, data CRC checking, compressor override, assertion action, authentication key name, and authentication hash name. `ubi` and `vol` parameters are accepted as ignored compatibility strings.

Mount flow: `mount_ubifs` initializes debugging and sysfs, checks whether the UBI volume is empty, allocates buffers, initializes optional authentication, reads the superblock and master node, initializes LPT/lprops, performs free-space fixup and recovery as needed, writes dirty master/superblock updates, replays the journal, mounts orphans, reserves/cleans the GC LEB, adds the instance to the global shrinker list, initializes debugfs, and logs geometry.

Unmount and remount: `ubifs_put_super` cleanly stops the background thread, syncs write buffers, writes a clean master node unless a fatal read-only error occurred, and calls `ubifs_umount`. `ubifs_remount_rw` allocates write-only resources and completes deferred recovery, while `ubifs_remount_ro` syncs buffers, writes a clean master node, frees write-only resources, and releases LPT write state.

UBI source parsing: `open_ubi` accepts device paths plus `ubiX_Y`, `ubiY`, `ubiX:NAME`, `ubi:NAME`, and `!` separator variants. `ubifs_get_tree` opens a volume read-only for probing, uses `sget_fc` to share existing mounts, and lets `ubifs_fill_super` reopen it read-write for actual mounting.

Module lifecycle: `ubifs_init` checks node-size invariants, creates the inode slab, allocates/registers the shrinker, initializes compressors, debugfs, sysfs, and registers the filesystem. `ubifs_exit` checks that no mounts or clean znodes remain, tears down debugfs/sysfs/compressors/shrinker, waits for RCU inode frees, destroys the slab, and unregisters the filesystem.

Important interactions: this file ties together nearly every UBIFS subsystem: superblock handling, auth, LPT/lprops, master nodes, journal replay/commit, GC, orphan handling, TNC, compressors, debugfs, sysfs, shrinker, and fscrypt.

Reliability notes: mount has a long staged cleanup path matching allocation order. Read-only media, static UBI volumes, corrupted UBI volumes, format incompatibility, missing authentication support, compressor absence, and insufficient free space are all detected before exposing a usable root dentry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/sysfs.c -->
# File Research: sources/os/linux/linux/fs/ubifs/sysfs.c

Read completely: 156 lines.

This file implements UBIFS sysfs registration and per-mount read-only error counters under the global `fs/ubifs` kset.

Main entry points: `ubifs_sysfs_register`, `ubifs_sysfs_unregister`, `ubifs_sysfs_init`, and `ubifs_sysfs_exit`.

Exposed attributes: `errors_magic`, `errors_node`, and `errors_crc`, each read-only. `ubifs_attr_show` maps them to `sbi->stats->magic_errors`, `node_errors`, and `crc_errors`.

Per-mount registration: `ubifs_sysfs_register` allocates `struct ubifs_stats_info`, formats the mount object name from UBI device and volume IDs, attaches the kobject to `ubifs_kset`, initializes the unregister completion, and calls `kobject_init_and_add`.

Teardown: `ubifs_sysfs_unregister` deletes and puts the per-mount kobject, waits for its release callback to complete, and frees the stats structure. The release callback completes `c->kobj_unregister`.

Global lifecycle: `ubifs_sysfs_init` names and registers the `ubifs` kset under `fs_kobj`; `ubifs_sysfs_exit` unregisters it.

Important interactions: `super.c` initializes global sysfs during module init and registers each mount early in `mount_ubifs`; `io.c` node validation increments these counters when stats are allocated.

Reliability notes: name length is checked against `UBIFS_DFS_DIR_LEN`. Registration failure paths call `kobject_put`, wait for completion where appropriate, free stats, and log the failed `ubifs<ubi>_<vol>` object.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/tnc.c -->
# File Research: sources/os/linux/linux/fs/ubifs/tnc.c

Read completely: 3575 lines.

This file implements the UBIFS Tree Node Cache (TNC), the in-memory cache and mutation layer for the UBIFS indexing B-tree. It handles lookups, cached leaf nodes, hash-collision resolution, copy-on-write znode dirtying, insertion, replacement, deletion, range removal, bulk-read discovery, and GC/commit membership queries.

Main entry points include `ubifs_lookup_level0`, `ubifs_tnc_locate`, `ubifs_tnc_get_bu_keys`, `ubifs_tnc_bulk_read`, `ubifs_tnc_lookup_nm`, `ubifs_tnc_lookup_dh`, `ubifs_tnc_add`, `ubifs_tnc_replace`, `ubifs_tnc_add_nm`, `ubifs_tnc_remove`, `ubifs_tnc_remove_nm`, `ubifs_tnc_remove_dh`, `ubifs_tnc_remove_range`, `ubifs_tnc_remove_ino`, `ubifs_tnc_next_ent`, `ubifs_tnc_close`, `is_idx_node_in_tnc`, `ubifs_tnc_has_node`, `ubifs_dirty_idx_node`, and `dbg_check_inode_size`.

Old-index protection: `insert_old_idx_znode`, `ins_clr_old_idx_znode`, and `destroy_old_idx` maintain an RB-tree of old index-node positions that must not be overwritten until a successful commit. This protects recovery by preserving the last complete committed index while dirty znodes are being rewritten.

Copy-on-write mutation: `dirty_cow_znode` and `dirty_cow_bottom_up` ensure any znode being committed is copied before modification. They update dirty and clean znode counters, clear on-flash position fields for dirty branches, add obsolete index dirt, and replace old znodes with copies when `COW_ZNODE` is set.

Leaf node cache: hashed leaf nodes such as directory and xattr entries may be copied into `zbr->leaf` to avoid repeated media reads during collision resolution and readdir-like walks. `lnc_add`, `lnc_add_directly`, `lnc_free`, and `tnc_read_hashed_node` manage this small per-branch cache.

Lookup behavior: `ubifs_lookup_level0` descends the TNC, lazily loading missing znodes, and handles the special case where equivalent hashed keys can live to the left of the nominal search path. `lookup_level0_dirty` performs the same search while dirtying the path for mutation.

Collision handling: `resolve_collision`, `fallible_resolve_collision`, and `resolve_collision_directly` scan left/right among equal hashed keys to match by full name or by exact flash position. Fallible variants tolerate dangling branches during journal replay, where a referenced node may have been garbage-collected before commit.

Reads and bulk reads: `ubifs_tnc_locate` can drop `tnc_mutex` for non-hashed node reads and retries safely if GC may have moved the LEB. Bulk-read helpers collect consecutive data-node zbranches for the same inode and same LEB, then read and validate the combined region while detecting GC races with `gc_seq`.

Insert/update/delete: `tnc_insert` inserts zbranches and splits full znodes, including root splits and parent-key correction. `ubifs_tnc_add` replaces unique-key entries or inserts new ones; `ubifs_tnc_add_nm` handles full-name collision semantics. `tnc_delete` removes leaf branches, collapses empty znodes and single-child roots, and records old index positions as needed.

Removal APIs: single-key, name-qualified, double-hash cookie-qualified, key-range, and whole-inode removal paths all converge on dirtying the affected znode and deleting branches while adding obsolete node dirt. `ubifs_tnc_remove_ino` also walks xattr entries and removes their xattr inodes.

Iteration and GC support: `ubifs_tnc_next_ent` walks directory/xattr entries in key order with collision handling. `lookup_znode`, `is_idx_node_in_tnc`, `is_leaf_node_in_tnc`, `ubifs_tnc_has_node`, and `ubifs_dirty_idx_node` let GC and in-the-gaps commit decide whether on-flash nodes remain part of the current or old index.

Important interactions: journal write paths update TNC after writing nodes; GC uses replace and membership checks while moving nodes; `tnc_commit.c` uses the dirty znode lists and old-index records; `tnc_misc.c` supplies load/read/traversal primitives; `shrink_tnc` may reclaim clean subtrees.

Reliability notes: the TNC is serialized by `c->tnc_mutex`, but selected read paths deliberately race with GC and use sequence checks to retry. Correctness depends on preserving old index nodes until commit completion, updating dirty/clean counters consistently, and clearing leaf-cache entries whenever a branch changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/tnc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/tnc_commit.c -->
# File Research: sources/os/linux/linux/fs/ubifs/tnc_commit.c

Read completely: 1112 lines.

This file implements the TNC commit algorithm: selecting dirty znodes, assigning on-flash locations for rewritten index nodes, optionally writing into obsolete gaps, writing the new index, and finalizing clean/obsolete znode state.

Main entry points: `ubifs_tnc_start_commit` and `ubifs_tnc_end_commit`.

Index-node construction: `make_idx_node` serializes a dirty znode into an on-flash `UBIFS_IDX_NODE`, copies child keys/locations/hashes, prepares the node, calculates its hash, records old index position, updates the parent/root zbranch, adjusts calculated index size, clears dirty/COW flags, and decrements the dirty count.

In-the-gaps commit: `layout_leb_in_gaps` scans a dirty index LEB, determines which existing index nodes are still in use via `is_idx_node_in_use`, fills obsolete gaps with new index nodes using `fill_gap`, pads remaining space, updates lprops, and atomically changes the LEB. `layout_in_gaps` repeats this while insufficient empty LEBs are available, growing the `gap_lebs` array if index LEB count increases during allocation.

Empty-space layout: `layout_in_empty_space` places remaining dirty znodes into the index head or newly allocated empty index LEBs, updates parent/root positions, lprops, calculated index size, and debug expected index-head position without writing the index bytes yet.

Dirty znode selection: `find_first_dirty`, `find_next_dirty`, and `get_znodes_to_commit` build a circular `cnext` list of dirty znodes, set `COW_ZNODE` to freeze them against concurrent mutation, store commit-parent information, reset `alt`, and assert the count matches `dirty_zn_cnt`.

LEB allocation: `alloc_idx_lebs` estimates required empty LEBs and obtains them with `ubifs_find_free_leb_for_idx`; `free_unused_idx_lebs` and `free_idx_lebs` release excess allocations. Debug index checking can force an artificial `-ENOSPC` to exercise in-the-gaps layout.

Start commit: `ubifs_tnc_start_commit` checks TNC consistency, builds the commit znode list, allocates and lays out index locations, frees unused index LEBs, destroys the old-index RB-tree, returns the new root zbranch, saves dirty index LEB numbers, and updates budgeting state to treat the new index size as committed.

Write phase: `write_index` serializes index nodes to `c->cbuf`, writes them to the laid-out LEB offsets, updates hashes in both commit-parent and live-parent branches under `tnc_mutex`, and clears dirty before COW with memory barriers so concurrent dirtying sees a valid state.

End commit: `ubifs_tnc_end_commit` returns in-gap LEBs, writes index nodes, frees obsolete znodes, converts committed znodes to clean by updating clean counters, clears `cnext`, and frees allocated index-LEB arrays.

Important interactions: this file consumes dirty znode state prepared by `tnc.c`, uses `scan.c` for in-gap LEB scans, relies on lprops/find code for index LEB selection and accounting, and feeds the commit subsystem with the new root index location.

Reliability notes: the commit path maintains the invariant that a complete old index remains intact until the new index is safely written. Dirty and COW bit ordering in `write_index` is explicitly synchronized to prevent races with `dirty_cow_znode`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/tnc_commit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/tnc_misc.c -->
# File Research: sources/os/linux/linux/fs/ubifs/tnc_misc.c

Read completely: 517 lines.

This file contains shared TNC helper functions for znode traversal, branch searching, subtree destruction, loading index znodes from flash, and reading leaf nodes by zbranch.

Main entry points: `ubifs_tnc_levelorder_next`, `ubifs_search_zbranch`, `ubifs_tnc_postorder_first`, `ubifs_tnc_postorder_next`, `ubifs_destroy_tnc_subtree`, `ubifs_destroy_tnc_tree`, `ubifs_load_znode`, and `ubifs_tnc_read_node`.

Traversal helpers: `ubifs_tnc_levelorder_next` supports breadth/level-order traversal from a subtree root and is used by the shrinker to reclaim old clean subtrees. `ubifs_tnc_postorder_first` and `ubifs_tnc_postorder_next` support postorder traversal for safe subtree freeing.

Branch search: `ubifs_search_zbranch` performs binary search inside a znode and returns either an exact match or the closest-left insertion position, using `-1` when the searched key is smaller than every branch key.

Tree destruction: `ubifs_destroy_tnc_subtree` frees all connected znodes below a subtree root and counts clean znodes freed. `ubifs_destroy_tnc_tree` destroys the whole TNC and subtracts the per-filesystem clean count from the global shrinker counter.

Index loading: `read_znode` reads an on-flash index node, verifies its node hash, child count, level, branch LEB/offset/length bounds, key types, leaf target length ranges, and key ordering. It rejects duplicate non-hashed keys and dumps bad index nodes before returning `-EINVAL`.

Lazy znode loading: `ubifs_load_znode` allocates a fanout-sized znode, fills it via `read_znode`, increments per-filesystem and global clean-znode counters, attaches it to the parent zbranch, stamps its access time, and records `iip`.

Leaf reads: `ubifs_tnc_read_node` reads a non-index node from either a journal write-buffer or flash, validates node type/length through low-level I/O, verifies the node key matches the zbranch key, and checks the stored node hash.

Important interactions: `tnc.c` relies on these helpers for lazy tree descent, branch search, leaf reads, and shutdown cleanup. `shrinker.c` uses level-order traversal and subtree destruction. `tnc_commit.c` and GC logic depend on index-node validation and hash propagation matching these helpers.

Reliability notes: all loaded index and leaf nodes are checked against both structural constraints and stored hashes. The global clean-znode counter is intentionally updated after per-mount counter updates and may be briefly inconsistent, which the shrinker design tolerates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/tnc_misc.c -->