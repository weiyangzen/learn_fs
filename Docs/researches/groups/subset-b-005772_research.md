# subset-b-005772 research

Grouped research report for UBIFS files under `sources/distributed-fs/ceph-client/fs/ubifs`. Each file section is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/sb.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/sb.c

## Purpose
`sb.c` owns the UBIFS superblock media contract. It can create a default filesystem on an empty UBI volume, read and validate an existing superblock, authenticate it when UBIFS authentication is enabled, update persistent superblock flags, and perform the one-time free-space fixup needed for images whose free areas were programmed as literal `0xff` bytes instead of being truly erased.

The file treats the superblock as mostly immutable UBIFS geometry: LEB size/count, log/LPT/orphan/main area layout, fanout, journal sizing, default compressor, reserved pool, feature flags, format version, UUID, encryption, double-hash, big-LPT, and authentication metadata.

## Important APIs, Types, And Functions
`get_default_compressor()` chooses ZSTD, LZO, ZLIB, then none based on compiled compressor availability. `create_default_filesystem()` formats an empty volume by synthesizing and writing the superblock, master nodes, root index node, root inode, LPT, and initial commit-start node. `validate_sb()` checks superblock-derived state in `struct ubifs_info` against UBI geometry, minimum area sizes, journal constraints, fanout, LPT save table sizing, feature/version rules, compression type, reserved-pool bounds, and time granularity.

`ubifs_read_superblock()` is the mount-time entry point. It optionally formats an empty volume, reads `UBIFS_SB_LNUM`, fills `struct ubifs_info`, handles forward format versions and read-only compatibility, selects key hash and key format, validates authentication and feature flags, performs automatic resize to the UBI volume limit, computes area boundaries, and calls `validate_sb()`.

`ubifs_write_sb_node()` rewrites the aligned superblock LEB after preparing HMAC metadata. `ubifs_fixup_free_space()` performs the first-mount free-space rewrite and clears `UBIFS_FLG_SPACE_FIXUP` in memory, deferring persistent write through `c->superblock_need_write`. `ubifs_enable_encryption()` is the ioctl-facing persistent feature enable path: it validates kernel support, writeability, and format version, sets `UBIFS_FLG_ENCRYPTION`, writes the superblock immediately, and flips `c->encrypted`.

## Control Flow
On empty mount, `create_default_filesystem()` computes journal/log/orphan/LPT/main-area sizes, asks `ubifs_create_dflt_lpt()` for LPT geometry, allocates aligned node buffers, initializes superblock and master fields, creates root inode/index content, calculates hashes, writes the superblock/master nodes with HMAC where needed, writes the root inode/index, and writes an initial commit-start node into the log. On normal mount, `ubifs_read_superblock()` reads the superblock, populates `c`, authenticates, may auto-resize, derives area offsets, and validates. One-time space fixup later walks master, log, LPT, orphan, and main areas to unmap empty LEBs or rewrite used prefixes with `ubifs_leb_change()`.

## State And Persistence
Persistent state is the on-flash superblock, initial master nodes, root inode, root index, LPT, and log commit-start node. `c->sup_node` keeps the in-memory copy. `c->superblock_need_write` bridges state changes made during mount, such as auto-resize, authentication HMAC conversion, or space-fixup flag clearing, to a later safe superblock rewrite. Feature flags are high risk because they gate compatibility and later mount behavior: authentication and encryption require support/key material, double hash requires format version 5+, and unknown flags reject the mount.

## Dependencies And Integration Points
This file integrates with UBI IO wrappers (`ubifs_leb_read`, `ubifs_leb_change`, `ubifs_leb_unmap`, `ubifs_write_node*`), media definitions from `ubifs-media.h`, key helpers, compressor registration, LPT creation and lookup, authentication/HMAC/signature helpers, mount setup in `super.c`, and encryption enablement through `ioctl.c`. `ubifs_read_superblock()` is called from `mount_ubifs()`, while `ubifs_fixup_free_space()` is called during mount and remount-rw when the superblock flag requires it.

## Risks And Edge Cases
Geometry arithmetic must avoid overflow and preserve UBIFS minimum-area invariants. Bad format-version handling could accidentally allow writes to incompatible media. Auto-resize mutates the superblock path only after validation and requires a later write; failure before that write can leave resize pending. Authentication mode mismatches are hard failures. Free-space fixup rewrites or unmaps broad media ranges and must not run on read-only mounts. Encryption enablement is persistent and irreversible for old kernels, so it strictly requires format version 5 and write access.

## Test Signals
Useful signals include mounting an empty UBI volume and checking default layout/root inode creation, mounting malformed superblocks for each `validate_sb()` branch, authentication mount combinations with and without keys, auto-resize on a grown UBI volume, `space_fixup` first-mount behavior followed by flag clearing, encryption ioctl behavior on unsupported/read-only/old-format filesystems, and fault injection around `ubifs_write_sb_node()` and LEB rewrite/unmap operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/sb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/scan.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/scan.c

## Purpose
`scan.c` implements the generic UBIFS logical eraseblock scanner. It converts raw bytes from one LEB into a `struct ubifs_scan_leb` containing ordered `struct ubifs_scan_node` descriptors for valid nodes, while distinguishing valid padding, erased space, garbage, corrupt nodes, and corrupt empty space. Replay, recovery, garbage collection, LPT checks, master reading, orphan handling, authentication, debugging, and TNC in-the-gaps commit all depend on this scanner.

## Important APIs, Types, And Functions
`ubifs_scan_a_node()` classifies one candidate buffer position using common-header magic, node validation, padding-node validation, and raw padding-byte detection. Return values are the `SCANNED_*` enum values from `ubifs.h`, with positive values meaning padding bytes to skip. `ubifs_start_scan()` allocates and initializes `struct ubifs_scan_leb`, reads the LEB tail into the caller-provided scan buffer, and tolerates `-EBADMSG` because node CRCs are checked individually.

`ubifs_add_snod()` appends a `struct ubifs_scan_node` with sequence number, type, offset, length, raw node pointer, and key for keyed nodes. `ubifs_scan()` is the main scanner: it loops over nodes/padding, stops at erased space, enforces min-I/O alignment for the empty-space boundary, verifies that the remainder is all `0xff`, and returns either a scan list or `ERR_PTR(-EUCLEAN)` for recoverable corruption. `ubifs_scan_destroy()` frees only scan descriptors and the `sleb`; the raw buffer remains caller-owned.

## Control Flow
The scanner reads the target LEB once, then advances by either padding length or aligned node length. Valid node headers become scan nodes. Empty space stops node scanning and triggers strict tail verification. Garbage, corrupt nodes, and bad padding go through the corruption path, optionally dumping the first bytes of the corrupt region via `ubifs_scanned_corruption()`. Non-quiet callers get detailed diagnostics; quiet callers can probe during recovery without noisy logs.

## State And Persistence
The scanner does not mutate flash. It builds transient metadata over a caller-owned LEB-sized buffer. Each `snod->node` points into that buffer, so callers must consume or copy data before reusing/freeing the scan buffer. The `endpt` field records the min-I/O-aligned endpoint of valid content and is used by recovery and replay to decide where writes or cleanup can resume.

## Dependencies And Integration Points
Core dependencies are `ubifs_leb_read()`, `ubifs_check_node()`, key parsing helpers, UBIFS node layout definitions, kernel lists, and debug dump helpers. Callers include `replay.c`, `recovery.c`, `gc.c`, `log.c`, `master.c`, `orphan.c`, `auth.c`, `lprops.c`, `debug.c`, and `tnc_commit.c`. The scanner is therefore a shared correctness boundary between raw flash contents and higher-level recovery, commit, and GC decisions.

## Risks And Edge Cases
Padding handling is subtle: raw padding bytes must be non-zero and 8-byte aligned, while padding nodes must not run past LEB end and must align the combined node-plus-padding length. The empty-space start must align to `min_io_size`; otherwise the LEB is considered corrupt. `-EBADMSG` during the initial read is intentionally tolerated, but CRC/hash validation later must catch damaged nodes. Because scan nodes point into `sbuf`, stale pointers are possible if callers keep them after buffer reuse.

## Test Signals
Tests should cover valid mixed-node LEBs, raw padding bytes, padding nodes, empty LEBs, corrupt magic, bad CRC/hash, bad pad lengths, empty space starting at non-min-I/O offsets, non-`0xff` bytes in the tail, quiet versus non-quiet diagnostics, and callers that sort or replay scan lists. Recovery tests should confirm `-EUCLEAN` is produced for corruption that can be handled by recovery code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/shrinker.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/shrinker.c

## Purpose
`shrinker.c` connects UBIFS TNC memory usage to the Linux VM shrinker. It frees clean znodes from mounted UBIFS instances when the kernel asks for reclaim and nudges background commits when no clean znodes are available but dirty znodes could become reclaimable after commit.

## Important APIs, Types, And Functions
Global state includes `ubifs_infos`, protected by `ubifs_infos_lock`, `shrinker_run_no` for fair per-run iteration, and `ubifs_clean_zn_cnt`, the global clean-znode estimate used by the shrinker count path. `shrink_tnc()` walks one filesystem's TNC in level order, freeing old enough clean subtrees with `ubifs_destroy_tnc_subtree()` and updating both global and per-filesystem clean counts. `shrink_tnc_trees()` iterates all mounted filesystems, try-locking `umount_mutex` and `tnc_mutex`, moving processed instances to the list tail for fairness.

`kick_a_thread()` looks for mounted writable filesystems with dirty znodes and a resting commit state, then requests a background commit so dirty znodes can later become clean and reclaimable. `ubifs_shrink_count()` reports the global clean-znode count, tolerating temporary negative values by returning `1`. `ubifs_shrink_scan()` is the registered scan callback: it first tries old znodes, then young znodes, then any clean znodes, and returns `SHRINK_STOP` on contention with no progress.

## Control Flow
The VM asks for a count through `ubifs_shrink_count()` and a scan through `ubifs_shrink_scan()`. If no clean znodes exist, UBIFS may request a background commit and tells VM to retry later. If clean znodes exist, reclaim proceeds across mounted instances. Each instance is protected from unmount with `umount_mutex`, and its TNC is protected with `tnc_mutex`. Subtrees are reclaimed only when their root is clean, not in the commit `cnext` list, and old enough for the current age pass.

## State And Persistence
The shrinker mutates only memory-resident cache state: TNC znodes and clean-znode counters. It does not alter persistent media. However, by kicking background commits it can indirectly cause future commit IO. It must respect commit state because clean znodes on `c->cnext` have just been written but are still owned by the commit-end cleanup path.

## Dependencies And Integration Points
`super.c` registers the shrinker during module init and maintains `ubifs_infos` membership during mount/unmount. `tnc_misc.c` provides `ubifs_tnc_levelorder_next()` and subtree destruction. TNC commit code manipulates `cnext`, dirty/clean flags, and clean counters that the shrinker observes. Commit code and background thread handling provide `ubifs_request_bg_commit()` and commit state transitions.

## Risks And Edge Cases
The global and per-filesystem clean counters can be temporarily inconsistent or negative because commit cleanup and dirtying are concurrent. Reclaim must avoid znodes in `cnext` because that list is intentionally not protected by the normal TNC mutex. Try-lock failure should signal contention rather than blocking VM reclaim on unmount or TNC mutation. Freeing a subtree assumes level-order age monotonicity: if a root is old and clean, descendants are also old enough. Any bug in counter updates can lead to under-reporting reclaimable memory or `WARN_ON()` at module exit.

## Test Signals
Signals include memory pressure causing clean znode reclamation, reclaim during unmount, reclaim during commit with `cnext` populated, dirty-only TNCs causing background commit requests, fairness across multiple mounted volumes, age-threshold behavior, negative global clean-count tolerance, and module exit warnings for non-empty `ubifs_infos` or nonzero `ubifs_clean_zn_cnt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/shrinker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/super.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/super.c

## Purpose
`super.c` implements UBIFS module initialization, filesystem registration, VFS superblock operations, fs_context parsing, mount/remount/unmount lifecycle, inode allocation/loading/freeing, writeback hooks, statfs/sync behavior, and the top-level orchestration of all UBIFS subsystems. It is the main bridge between Linux VFS/UBI and UBIFS internals.

## Important APIs, Types, And Functions
The VFS inode path is centered on `ubifs_iget()`, `validate_inode()`, `ubifs_alloc_inode()`, `ubifs_free_inode()`, `ubifs_write_inode()`, `ubifs_evict_inode()`, and `ubifs_dirty_inode()`. These functions translate UBIFS inode nodes into VFS inodes, validate on-flash fields, install file/dir/symlink/special inode operations, handle xattr and symlink inline data, write dirty inodes through the journal, and delete orphaned inodes.

Mount setup is handled by `init_constants_early()`, `init_constants_sb()`, `init_constants_master()`, `alloc_wbufs()`, `check_volume_empty()`, and `mount_ubifs()`. `mount_ubifs()` coordinates debugging, sysfs registration, empty-volume formatting, buffer allocation, authentication, superblock/master/LPT reads, recovery, journal replay, orphan mounting, free-space checks, log consolidation, GC LEB reservation, debugfs, and `ubifs_infos` registration.

Remount/unmount paths are `ubifs_remount_rw()`, `ubifs_remount_ro()`, `ubifs_reconfigure()`, `ubifs_put_super()`, and `ubifs_umount()`. VFS registration and fs_context paths are `open_ubi()`, `alloc_ubifs_info()`, `ubifs_fill_super()`, `ubifs_get_tree()`, `kill_ubifs_super()`, `ubifs_init_fs_context()`, and `ubifs_free_fc()`. Module lifecycle is `ubifs_init()` and `ubifs_exit()`, which create the inode slab, register the shrinker, initialize compressors/sysfs/debugfs, and register/unregister the filesystem.

## Control Flow
First mount parses options into `struct ubifs_fs_context`, opens the UBI volume read-only for identity lookup, allocates `struct ubifs_info`, and either reuses an existing superblock or calls `ubifs_fill_super()`. `ubifs_fill_super()` reopens UBI read-write, sets VFS fields, and calls `mount_ubifs()` under `umount_mutex`. After the internal mount succeeds, it reads the root inode, creates `s_root`, and publishes UUID/sysfs names.

`mount_ubifs()` is staged with matching cleanup labels. It initializes immutable UBI-derived constants, registers per-mount sysfs, detects empty volumes, allocates mount buffers, initializes authentication if requested, reads/creates the superblock, validates compressors and derived constants, allocates commit/write buffers and journal heads, starts the background thread for writable mounts, reads master/LPT state, performs recovery or marks the master dirty, writes pending superblock changes, replays the journal, mounts orphans, checks free/log space, handles GC LEB state, adds the instance to `ubifs_infos`, and runs debug checks.

Remount-rw allocates write-only resources that read-only mounts skip, completes deferred recovery, writes the master dirty flag, writes pending superblock changes, starts the background thread, initializes writable LPT state, and unmaps or commits the GC LEB. Remount-ro stops the thread, syncs write buffers, clears the dirty master flag, records no-orphans and GC LEB state, frees writable-only buffers, and drops writable LPT resources. Unmount follows a similar clean path unless the filesystem has already entered read-only error mode.

## State And Persistence
`struct ubifs_info` is the core in-memory state object. `alloc_ubifs_info()` initializes locks, wait queues, trees, lists, default mount settings, UBI geometry, and baseline logical positions. Persistent state affected by this file includes inode nodes written through journal operations, master-node dirty/no-orphans/gc fields, superblock writes delegated to `sb.c`, LPT state, log consolidation, recovery writes, and GC LEB unmapping. Mount flags such as `ro_mount`, `ro_media`, `need_recovery`, `ro_error`, `remounting_rw`, and `mounting` control which operations may write media and how aggressively node CRCs are checked elsewhere.

## Dependencies And Integration Points
The file integrates with VFS (`super_operations`, inode operations, fs_context, `sget_fc`, `kill_anon_super`), UBI open/close and sync APIs, Linux writeback and shrinker APIs, fscrypt, xattrs, sysfs/debugfs, compressors, authentication, journal, replay, recovery, LPT, master node handling, orphan handling, budgeting, GC, TNC, and background commit threads. It exports `ubifs_super_operations` and registers the `ubifs` filesystem type with `MODULE_ALIAS_FS("ubifs")`.

## Risks And Edge Cases
Mount and remount error unwinding is complex because different resources are allocated depending on read-only state, authentication, recovery need, and mount progress. Clean unmount must write master state unless the filesystem is already in read-only error mode. Deferred recovery for read-only mounts must complete correctly on later remount-rw. Option parsing ignores authentication changes on remount, so callers must not expect key replacement there. Empty volumes cannot be formatted if the mount or media is read-only. Inode validation prevents malformed media from creating impossible VFS state; bypassing it risks memory safety and filesystem corruption.

## Test Signals
Important tests include empty-volume formatting, normal mount, read-only mount, static/corrupt UBI volume handling, remount ro/rw with and without deferred recovery, mount option persistence and display, authentication options, bulk-read allocation failure fallback, inode loading for each file type, writeback of dirty inodes, orphan inode eviction, syncfs committing and UBI sync, statfs reserved-pool accounting, mount failure at each staged allocation point, and module init/exit registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/sysfs.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/sysfs.c

## Purpose
`sysfs.c` exposes per-mounted-UBIFS error counters under the kernel `/sys/fs/ubifs/...` hierarchy. It creates one kobject per mounted UBIFS instance and provides read-only attributes for magic, node, and CRC error counters stored in `struct ubifs_stats_info`.

## Important APIs, Types, And Functions
`enum attr_id_t` identifies supported attributes. `struct ubifs_attr` wraps a kernel `struct attribute` with the UBIFS attribute id. `UBIFS_ATTR_FUNC()` declares `errors_magic`, `errors_crc`, and `errors_node` as mode `0444`. `ubifs_attr_show()` maps each attribute id to a `sysfs_emit()` of `sbi->stats` counters.

`ubifs_sysfs_register()` allocates `c->stats`, constructs the per-volume name from `UBIFS_DFS_DIR_NAME`, initializes `c->kobj` under the global `ubifs_kset`, and publishes the per-instance attribute group. `ubifs_sysfs_unregister()` deletes and puts the kobject, waits for the release completion, and frees stats. `ubifs_sysfs_init()` registers the global `ubifs` kset below `fs_kobj`; `ubifs_sysfs_exit()` unregisters it.

## Control Flow
Module init calls `ubifs_sysfs_init()` before filesystem registration. Each successful mount path calls `ubifs_sysfs_register()` early in `mount_ubifs()`, before most media reads that may increment counters. On mount failure or unmount, `ubifs_sysfs_unregister()` tears down the kobject and stats allocation. The kobject release callback completes `c->kobj_unregister`, allowing unregister to wait until sysfs has dropped the object.

## State And Persistence
All state is in memory. The exposed counters are not persistent across mount cycles. The kobject lifetime is tied to `struct ubifs_info`; the release completion protects teardown from freeing `c->stats` and proceeding while sysfs still owns the kobject.

## Dependencies And Integration Points
This file depends on kernel kobject/kset/sysfs APIs, `fs_kobj`, and UBIFS mount state (`c->vi`, `c->kobj`, `c->stats`). `super.c` calls global init/exit and per-mount register/unregister. Lower-level IO and validation code update `c->stats` counters that this file exposes.

## Risks And Edge Cases
The generated sysfs name must fit `UBIFS_DFS_DIR_LEN`; overflow returns `-EINVAL`. Register failure must call `kobject_put()` and wait for release before freeing stats. Unregister assumes registration succeeded and should be paired with the mount paths that allocated `c->stats`. Attribute reads return zero for unknown ids, but only known attributes are installed.

## Test Signals
Signals include `/sys/fs/ubifs` kset creation/removal at module init/exit, per-volume directory creation on mount, read-only output for the three error attributes, counter changes after injected magic/node/CRC errors, long-name bounds checks, and fault injection for stats allocation or `kobject_init_and_add()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/tnc.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/tnc.c

## Purpose
`tnc.c` implements the UBIFS Tree Node Cache, the in-memory cache and mutation layer for UBIFS indexing B-tree nodes. It handles lookup, insertion, replacement, removal, range deletion, hash-collision resolution, leaf-node caching, GC race handling, old-index tracking for recovery, and debug validation. It is the main authority for mapping UBIFS keys to on-flash node locations.

## Important APIs, Types, And Functions
Old-index tracking uses `insert_old_idx()`, `insert_old_idx_znode()`, `ins_clr_old_idx_znode()`, and `destroy_old_idx()` to preserve references to index nodes that belonged to the last committed index but may no longer be discoverable by key. Copy-on-write and dirtying are handled by `copy_znode()`, `dirty_cow_znode()`, `dirty_cow_bottom_up()`, `replace_znode()`, and `add_idx_dirt()`.

Lookup primitives include `ubifs_lookup_level0()`, `lookup_level0_dirty()`, `tnc_next()`, `tnc_prev()`, `get_znode()`, `ubifs_tnc_locate()`, `ubifs_tnc_lookup_nm()`, `ubifs_tnc_lookup_dh()`, and `ubifs_tnc_next_ent()`. Hash-collision helpers are `matches_name()`, `resolve_collision()`, `fallible_matches_name()`, `fallible_resolve_collision()`, `resolve_collision_directly()`, `search_dh_cookie()`, and `do_lookup_dh()`. Leaf node caching is managed by `lnc_add()`, `lnc_add_directly()`, `lnc_free()`, and `tnc_read_hashed_node()`.

Mutation APIs are `ubifs_tnc_add()`, `ubifs_tnc_add_nm()`, `ubifs_tnc_replace()`, `ubifs_tnc_remove()`, `ubifs_tnc_remove_nm()`, `ubifs_tnc_remove_dh()`, `ubifs_tnc_remove_range()`, and `ubifs_tnc_remove_ino()`. Bulk read APIs are `ubifs_tnc_get_bu_keys()` and `ubifs_tnc_bulk_read()`. GC/debug integration includes `ubifs_tnc_has_node()`, `ubifs_dirty_idx_node()`, `is_idx_node_in_tnc()`, and `dbg_check_inode_size()`. Cleanup is `ubifs_tnc_close()`.

## Control Flow
Lookups acquire `c->tnc_mutex`, lazily load missing znodes from flash via `ubifs_load_znode()`, binary-search zbranches, and descend to level 0. Non-hashed unique keys can often drop `tnc_mutex` before reading the leaf node, then retry safely if GC may have moved the LEB. Hashed dent/xent keys keep the mutex while resolving collisions by comparing names or double-hash cookies and may use the leaf-node cache.

Mutations use `lookup_level0_dirty()` to load and dirty the path from root to leaf. Dirtying respects in-progress commits: if a znode has `COW_ZNODE`, it is copied, the old instance is marked obsolete, and old on-flash positions are recorded. Insertions split full znodes, possibly splitting the root and correcting parent lower-bound keys. Deletions remove zbranches, add obsolete leaf space to lprops dirt, collapse empty znodes, and may reduce tree height. Range and inode removal repeatedly find and delete all keys in the requested range, including xattr entries and xattr inodes.

Bulk read first collects consecutive data-node zbranches for one inode in one LEB, respecting buffer length, holes, page-boundary coverage, and `UBIFS_MAX_BULK_READ`. The actual bulk read then reads one contiguous media range, checks for a GC race with `maybe_leb_gced()`, and validates every data node.

## State And Persistence
TNC state is memory-resident but mirrors persistent index nodes. Zbranches hold keys, LEB/offset/length, hash, optional child znode pointer, and optional cached leaf pointer. Dirty znodes represent index updates that must be committed by `tnc_commit.c`. `c->old_idx` protects the last committed index from being overwritten before a new commit completes. `c->dirty_zn_cnt`, `c->clean_zn_cnt`, and global `ubifs_clean_zn_cnt` feed budgeting and shrinker behavior. Lprops dirt is updated when old leaf or index locations become obsolete.

## Dependencies And Integration Points
This file depends on key encoding/comparison helpers, IO helpers, write-buffer reads, CRC/hash validation, lprops dirt accounting, TNC znode loading from `tnc_misc.c`, commit behavior from `tnc_commit.c`, GC sequence tracking, replay mode semantics, fscrypt names, journal callers that add/remove nodes, GC callers that replace moved nodes, directory/xattr code that uses name lookups, and debug code. The shrinker reclaims clean znodes created and counted by this file.

## Risks And Edge Cases
Hash collisions are the dominant lookup edge case: parent boundary keys can point to adjacent znodes with equivalent hashed keys, so lookups often need to scan left and right. Replay can encounter dangling branches after GC, so fallible lookup paths must distinguish missing media from hard IO failures. GC can move a leaf after `tnc_mutex` is dropped; sequence checks and retry-under-lock avoid returning stale data. Commit copy-on-write requires precise ordering of `DIRTY_ZNODE`, `COW_ZNODE`, obsolete flags, old-index records, and clean counters. Tree split/collapse bugs can break parent keys and make old index nodes unrecoverable after power loss.

## Test Signals
Signals include unique-key lookup/add/remove, dent/xent hash-collision lookup and removal, double-hash cookie lookup/removal, replay with dangling branches, insertion split/root split behavior, deletion collapse/root collapse behavior, range and inode removal including xattrs, GC replacement by exact location, stale read retry after GC sequence changes, bulk-read grouping and `-EAGAIN`, dirty/clean counter balance, old-index RB-tree cleanup, shrinker interaction, and `dbg_check_tnc()`/`dbg_check_inode_size()` failures under debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/tnc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/tnc_commit.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/tnc_commit.c

## Purpose
`tnc_commit.c` implements the TNC-specific portion of UBIFS commit. It selects dirty znodes, assigns new on-flash positions, optionally reuses holes left by obsolete index nodes, writes new index nodes, updates index-head state, and frees obsolete in-memory znodes after commit. Its core invariant is that the old committed index remains intact until the new committed index is durably written.

## Important APIs, Types, And Functions
`ubifs_tnc_start_commit()` is the start-commit entry point. It checks the TNC, builds the circular dirty-znode commit list with `get_znodes_to_commit()`, allocates empty index LEBs via `alloc_idx_lebs()`, lays out dirty znodes through `layout_commit()`, updates budgeting/index-size state, destroys previous old-index records, returns the new root zbranch, and saves dirty index LEB numbers.

Layout helpers include `layout_in_empty_space()`, `layout_in_gaps()`, `layout_leb_in_gaps()`, `fill_gap()`, `is_idx_node_in_use()`, and `get_leb_cnt()`. `make_idx_node()` materializes an index node into a gap and updates parent/root zbranches and hashes under the TNC mutex. `write_index()` writes nodes placed in empty space and clears dirty/COW flags with memory barriers. `ubifs_tnc_end_commit()` returns temporary gap LEBs, writes the index, frees obsolete znodes, frees allocated LEB arrays, and clears `c->cnext`.

## Control Flow
Start commit locks `c->tnc_mutex`, finds all dirty znodes in a deterministic dirty traversal, marks them `COW_ZNODE`, and chains them through `cnext`. It estimates required empty LEBs and asks lprops for index LEBs. If insufficient empty space exists, it scans dirty index LEBs and fills gaps where obsolete index nodes can be safely overwritten. Remaining nodes are assigned to empty index-head space or newly allocated index LEBs. Lprops and index size accounting are updated before the wider commit proceeds.

End commit first clears `LPROPS_TAKEN` from in-gap LEBs. `write_index()` then rebuilds each index node in the commit buffer, updates branch hashes in both commit-parent and live-parent views, verifies the planned location matches the actual write position, clears `DIRTY_ZNODE` before `COW_ZNODE`, writes aligned buffers to flash, and advances `c->ihead_lnum`/`c->ihead_offs`. Finally, under `tnc_mutex`, obsolete znodes are freed and non-obsolete committed znodes are returned to clean-count accounting.

## State And Persistence
Persistent outputs are new UBIFS index nodes written to index LEBs and the root zbranch later recorded by the broader commit machinery. Temporary in-memory commit state includes `c->cnext`, `c->enext`, `c->ilebs`, `c->ileb_cnt`, `c->ileb_nxt`, `c->gap_lebs`, `c->calc_idx_sz`, and debug new-index-head positions. Lprops state is updated for free/dirty/taken/index flags. The old-index RB-tree from `tnc.c` is consumed to avoid overwriting nodes still needed for recovery.

## Dependencies And Integration Points
This file uses scanner output from `scan.c` to inspect index LEB gaps, TNC old-index lookup from `tnc.c`, lprops allocation and accounting APIs, UBIFS node preparation/hash helpers, index node sizing helpers, debug check hooks, and write APIs (`ubifs_leb_change`, `ubifs_leb_write`). The broader `commit.c` calls `ubifs_tnc_start_commit()` and `ubifs_tnc_end_commit()` around master/log commit work.

## Risks And Edge Cases
Power-cut safety depends on not overwriting old-index nodes that are still part of the last committed index. The in-the-gaps method must correctly distinguish obsolete, dirty-old, and clean-in-use index nodes. `c->lst.idx_lebs` can grow while selecting dirty index LEBs, so `gap_lebs` may need dynamic enlargement. Dirty/clean znode counters are intentionally updated at different phases; temporary negative clean counts must be tolerated by the shrinker. Clearing dirty/COW flags without the required ordering can cause redundant copies or missed copy-on-write during concurrent TNC mutations.

## Test Signals
Signals include commits with no dirty znodes, commits fitting in current index head, commits needing new empty index LEBs, forced `-ENOSPC` into in-the-gaps layout, gap filling around clean in-use and dirty old nodes, LEB accounting after no nodes fit a selected gap, commit failure before end-commit cleanup, dirty/clean znode counter balance, index-head consistency checks, power-cut recovery using the old index, and debug mode forcing in-the-gaps behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/tnc_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/tnc_misc.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/tnc_misc.c

## Purpose
`tnc_misc.c` contains shared TNC support code that does not belong to one logical TNC submodule. It provides znode traversal, zbranch binary search, subtree destruction, znode loading from flash, and leaf-node reads with key/hash validation.

## Important APIs, Types, And Functions
Traversal helpers are `ubifs_tnc_levelorder_next()`, `ubifs_tnc_postorder_first()`, and `ubifs_tnc_postorder_next()`. `ubifs_search_zbranch()` performs binary search inside one znode and returns exact match or closest-left slot. Destruction helpers are `ubifs_destroy_tnc_subtree()` and `ubifs_destroy_tnc_tree()`, used by the shrinker and unmount cleanup.

`read_znode()` reads and validates one on-flash index node into an allocated znode: it checks hash, child count, level, branch address bounds, key types, leaf target lengths, and sorted key order. `ubifs_load_znode()` allocates a znode, calls `read_znode()`, increments clean-znode counters, attaches parent/iip/time metadata, and stores the pointer in the zbranch. `ubifs_tnc_read_node()` reads a leaf node either through an overlapping write buffer or normal media IO, validates the key, and checks the node hash.

## Control Flow
Lookup code in `tnc.c` calls `ubifs_search_zbranch()` while descending. When a child znode is absent from memory, it calls `ubifs_load_znode()`, which reads the index node from the branch's LEB/offset/length, validates it, attaches it to the parent branch, and records it as a clean znode. Reclaim and teardown use traversal helpers to walk and free znodes without touching cached leaf nodes directly.

## State And Persistence
This file reads persistent index and leaf nodes but does not write flash. It mutates in-memory zbranch pointers, znode parent/index metadata, access timestamps, and clean-znode counters. `ubifs_destroy_tnc_tree()` subtracts the destroyed clean count from the global counter and clears `c->zroot.znode`.

## Dependencies And Integration Points
It depends on `ubifs_read_node()`, `ubifs_read_node_wbuf()`, `ubifs_get_wbuf()`, key helpers, node hash helpers, znode flag helpers, and the global shrinker counter from `shrinker.c`. The main TNC lookup/mutation code relies on znode loading and searching here; the shrinker relies on level-order traversal and subtree destruction; commit and unmount cleanup depend on postorder destruction semantics.

## Risks And Edge Cases
Index-node validation is a security boundary for malformed media: bad branch addresses, invalid key types, impossible child counts, bad target lengths, unsorted keys, and non-hash duplicate keys must reject the mount/read path. Clean counter increments must match later destruction or shrinker accounting drifts. `ubifs_tnc_read_node()` must read through write buffers when a node is still buffered in a bud; normal media reads would otherwise miss recent journal data. Traversal code must handle sparse loaded subtrees because not every child znode is resident.

## Test Signals
Tests should include loading valid and malformed index nodes, hash mismatch detection, branch bounds checks, sorted-key enforcement including duplicate hash keys, lazy load during lookup, write-buffer-overlapping leaf reads, subtree destruction counts, full TNC destruction at unmount, shrinker level-order traversal over partially loaded trees, and postorder traversal over sparse child pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/tnc_misc.c -->
