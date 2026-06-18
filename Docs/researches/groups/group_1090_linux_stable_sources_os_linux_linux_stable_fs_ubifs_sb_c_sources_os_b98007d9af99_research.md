# Group Research: UBIFS superblock, scanning, shrinker, mount, sysfs, and TNC paths

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/sb.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/sb.c

## Purpose
Implements UBIFS superblock handling: empty-volume default formatting, superblock reading/writing, validation, authentication checks, resize bookkeeping, free-space fixup, and enabling encryption.

## Key Behavior
- `create_default_filesystem()` builds a minimal UBIFS image on an empty UBI volume: superblock, two master nodes, root index node, root inode, LPT metadata, and initial commit-start log node.
- Default geometry is derived from volume size, LEB size, minimum journal/log/orphan/LPT constraints, and reserved-pool defaults.
- `ubifs_read_superblock()` reads the on-flash superblock, fills `struct ubifs_info`, enforces format compatibility, handles automatic LEB-count growth, and derives area boundaries.
- `validate_sb()` rejects inconsistent geometry, unsupported key formats, invalid journal/fanout/LEB counts, bad compression IDs, invalid time granularity, and incompatible encryption/double-hash combinations.
- `authenticate_sb_node()` supports authenticated mounts through either superblock HMAC or an offline signature node following the superblock.
- `ubifs_fixup_free_space()` performs first-mount NAND free-space rewrite/unmap when `UBIFS_FLG_SPACE_FIXUP` is set, then clears the flag for future mounts.
- `ubifs_enable_encryption()` sets `UBIFS_FLG_ENCRYPTION` after checking crypto support, R/W state, and format version.

## Important Dependencies
- Uses UBI LEB operations through UBIFS wrappers: `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_read()`.
- Calls LPT creation/lookup paths: `ubifs_create_dflt_lpt()`, `ubifs_get_lprops()`, `ubifs_lpt_lookup()`.
- Depends on authentication helpers such as `ubifs_hmac_wkm()`, `ubifs_node_verify_hmac()`, and `ubifs_sb_verify_signature()`.
- Exposes state consumed by mount, budgeting, LPT, journal, and TNC initialization.

## Invariants and Risks
- The superblock is normally immutable during UBIFS operation; only controlled updates such as resize, free-space-fixup clearing, authentication HMAC conversion, and encryption enablement rewrite it.
- Format-version checks are central: newer writable formats are rejected unless read-only compatibility permits R/O mounting.
- Geometry validation protects downstream code from impossible LEB layouts and malformed index/node size assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/scan.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/scan.c

## Purpose
Provides generic logical eraseblock scanning used by journal replay, garbage collection, TNC in-the-gaps commit, and debug validation.

## Key Behavior
- `ubifs_scan_a_node()` classifies the next bytes in an LEB as empty space, padding bytes, a valid node, a corrupt node, or a bad padding node.
- Padding is accepted only when it uses `UBIFS_PADDING_BYTE`, has nonzero length, and is 8-byte aligned.
- `ubifs_start_scan()` allocates a scan descriptor and reads the requested LEB range into the caller-provided scan buffer.
- `ubifs_scan()` walks nodes until empty space or corruption, adds each valid scanned node to `sleb->nodes`, then validates that the remaining empty space is all `0xff`.
- `ubifs_add_snod()` records scanned node metadata: sequence number, type, offset, length, and key for keyed leaf nodes.
- `ubifs_scanned_corruption()` reports the failing LEB offset and dumps up to 8192 bytes for diagnostics.
- `ubifs_scan_destroy()` frees scan-node descriptors but not the scan buffer, which belongs to the caller.

## Important Dependencies
- Uses `ubifs_check_node()` for node validation.
- Uses `ubifs_leb_read()` for raw LEB reads.
- Scan results are consumed by recovery, GC, debug checks, and `tnc_commit.c` gap layout.

## Invariants and Risks
- Empty space must begin at a min-I/O aligned offset; otherwise the LEB is treated as needing recovery.
- `-EUCLEAN` signals corruption/recovery-needed rather than ordinary I/O failure.
- Integrity read errors from UBI may be ignored during the initial read because UBIFS validates nodes with CRC/hash checks afterward.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/shrinker.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/shrinker.c

## Purpose
Implements the global Linux VM shrinker for UBIFS TNC znodes, freeing clean cached index subtrees under memory pressure.

## Key Behavior
- Maintains global `ubifs_infos` list and global clean znode counter `ubifs_clean_zn_cnt`.
- `shrink_tnc()` walks a filesystem’s TNC level-order and frees clean znodes old enough for the requested age threshold.
- Whole clean subtrees can be dropped because children of an old clean root are also old enough.
- Znodes on `c->cnext` during commit are skipped because commit state is intentionally not protected by the same mutation path.
- `shrink_tnc_trees()` iterates mounted UBIFS instances fairly, using `umount_mutex` and `tnc_mutex` trylocks to avoid racing unmount and active TNC work.
- `kick_a_thread()` asks a mounted filesystem to start background commit when no clean znodes are currently reclaimable but dirty znodes may become clean.
- `ubifs_shrink_count()` and `ubifs_shrink_scan()` are the shrinker callbacks registered from `super.c`.

## Important Dependencies
- Uses traversal/destruction helpers from `tnc_misc.c`: `ubifs_tnc_levelorder_next()` and `ubifs_destroy_tnc_subtree()`.
- Coordinates with commit state from TNC and journal code through `c->cnext`, `c->cmt_state`, and dirty/clean znode counters.
- Protected by `ubifs_infos_lock`, `c->umount_mutex`, and `c->tnc_mutex`.

## Invariants and Risks
- Clean znode counters may be temporarily negative during commit accounting; count callback clamps this behavior.
- Shrinker must not block heavily or race unmount, so it uses trylocks and reports contention.
- No LRU is maintained by design, avoiding fast-path overhead at the cost of approximate reclaim ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/shrinker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/super.c

## Purpose
Implements UBIFS VFS integration, mount/remount/unmount lifecycle, inode allocation/read/write/evict behavior, mount option parsing, module initialization, shrinker registration, and filesystem type registration.

## Key Behavior
- `ubifs_iget()` loads inode nodes from the TNC, validates them, initializes VFS inode operations by file type, and handles inline symlink/xattr/device data.
- Inode lifecycle hooks manage dirty inode writeback, orphan deletion, page truncation on eviction, fscrypt state, and budget release.
- `init_constants_early()`, `init_constants_sb()`, and `init_constants_master()` derive UBIFS runtime geometry, node ranges, watermarks, budgeting constants, journal limits, and statfs reporting values.
- Mount option parsing supports unmount mode compatibility flags, bulk read, data CRC checking, compressor override, assert action, and authentication parameters.
- `mount_ubifs()` is the central mount sequence: basic UBI checks, sysfs/debug init, empty-volume detection, buffer allocation, authentication init, superblock/master read, LPT init, free-space fixup, recovery, journal replay, orphan handling, GC LEB reservation, and global mount registration.
- R/W mounts mark the master dirty early; clean unmount and remount-R/O clear dirty/orphan flags and write the master node.
- `ubifs_remount_rw()` completes deferred recovery, allocates R/W-only resources, starts the background thread, reinitializes LPT writable state, and handles GC/log readiness.
- `ubifs_remount_ro()` stops the background thread, syncs write buffers, writes a clean master node, frees R/W-only buffers, and switches LPT to R/O state.
- `open_ubi()` parses device-path and nodev mount syntaxes such as `ubiX_Y`, `ubiY`, `ubiX:NAME`, and `ubi:NAME`.
- Module init creates inode slab, registers shrinker, initializes compressors/debugfs/sysfs, and registers the `ubifs` filesystem.

## Important Dependencies
- Calls into nearly every UBIFS subsystem: superblock, master, LPT, log, journal replay, recovery, orphan, GC, TNC, budgeting, authentication, debugfs, sysfs, compressors, and fscrypt.
- Uses VFS `fs_context`, `super_operations`, inode slab cache, shrinker API, and UBI volume open/close APIs.
- Uses global shrinker structures from `shrinker.c` and sysfs helpers from `sysfs.c`.

## Invariants and Risks
- `umount_mutex` is the mount/unmount/remount exclusion point and also protects against shrinker races.
- R/O and R/W mount modes allocate different resources; remount paths must mirror allocation and cleanup precisely.
- Recovery ordering is security-sensitive under authentication: size recovery is split around authenticated GC commit.
- `ubifs_fill_super()` transfers ownership of authentication option strings from fs context to `ubifs_info`.
- Mount failure paths are staged and must unwind only resources initialized up to the failure point.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/sysfs.c

## Purpose
Adds UBIFS sysfs support under `/sys/fs/ubifs`, exposing per-mounted-volume read-only error counters.

## Key Behavior
- Defines read-only attributes: `errors_magic`, `errors_node`, and `errors_crc`.
- `ubifs_attr_show()` maps attributes to `sbi->stats` counters and emits decimal values.
- `ubifs_sysfs_register()` allocates `ubifs_stats_info`, formats the per-volume directory name, initializes the mount kobject, and adds it to sysfs.
- `ubifs_sysfs_unregister()` deletes and puts the kobject, waits for release completion, and frees stats.
- `ubifs_sysfs_init()` registers the top-level `ubifs` kset below `fs_kobj`.
- `ubifs_sysfs_exit()` unregisters the kset.

## Important Dependencies
- Called during mount/unmount from `super.c`.
- Relies on `struct ubifs_info` embedding a `kobject`, completion, UBI volume identifiers, and stats pointer.
- Counter updates are elsewhere in UBIFS I/O/validation code.

## Invariants and Risks
- Register failure calls `kobject_put()` and waits for the release callback before freeing stats.
- Directory name length is checked against `UBIFS_DFS_DIR_LEN`.
- Attributes are read-only; this file does not implement tuning or mutation interfaces.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/tnc.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/tnc.c

## Purpose
Implements the UBIFS Tree Node Cache: lookup, mutation, collision resolution, leaf-node cache, bulk reads, deletion, GC membership checks, and dirtying of index nodes.

## Key Behavior
- TNC is a cached B-tree of index znodes protected by `c->tnc_mutex`.
- Old index nodes are tracked in `c->old_idx` RB-tree so crash recovery can keep the previous committed index intact until the new commit succeeds.
- Dirtying uses copy-on-write when a znode is part of an active commit (`COW_ZNODE`), preserving commit consistency while foreground mutations continue.
- Leaf-node cache (`zbr->leaf`) stores copied dirent/xattr leaf nodes for readdir and hash collision resolution.
- `ubifs_lookup_level0()` finds the level-0 znode and slot for a key, loading missing znodes from flash as needed.
- Hashed keys require extra collision resolution by full name (`resolve_collision()`), fallible replay-aware matching, direct location matching for GC moves, or double-hash cookie lookup.
- `ubifs_tnc_locate()` supports lock-dropping reads for non-hash keys, with GC sequence checks and safe retry if the LEB may have moved.
- Bulk-read support finds adjacent data nodes in one LEB, reads through write-buffer overlap when necessary, and validates every returned data node.
- Insertions split full znodes, update parent keys, and record altered old-index references when split/leftmost-key changes may make old nodes hard to find.
- Deletions remove branches, free LNC entries, add obsolete space to dirt, collapse empty znodes, and may collapse the root.
- Range, inode, xattr, and directory-entry removal APIs build on lookup/delete primitives.
- GC-facing APIs answer whether index or leaf nodes still belong to TNC and dirty index nodes before collection.

## Important Dependencies
- Uses znode load/read helpers from `tnc_misc.c`.
- Commit integration depends on `c->cnext`, `COW_ZNODE`, `DIRTY_ZNODE`, obsolete flags, dirty/clean counters, and old-index tracking.
- Uses UBIFS node read/hash validation, lprops dirt accounting, write-buffer reads, key comparison helpers, and fscrypt names.

## Invariants and Risks
- The main concurrency rule is simple but broad: tree traversal and mutation require `c->tnc_mutex`; selected read paths briefly drop it only with GC race detection.
- Hash collisions are first-class: duplicate keys are legal only for hashed dent/xent keys and must be disambiguated before mutation.
- During replay, dangling branches may exist because GC and unclean commits can leave references to nodes no longer on media; fallible matching handles this.
- Parent key correction is delicate because GC may need to find old index nodes by old key/address; the old-index RB-tree covers cases where lookup by key becomes unreliable.
- Clean znode counters intentionally interact with shrinker and commit accounting and may be temporarily inconsistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/tnc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/tnc_commit.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/tnc_commit.c

## Purpose
Implements TNC commit mechanics: collecting dirty znodes, assigning on-flash index positions, optionally writing into obsolete gaps, writing index nodes, updating hashes/lprops, and finalizing clean/obsolete znode state.

## Key Behavior
- `get_znodes_to_commit()` builds a circular commit list from dirty znodes, marks them COW, stores commit-parent metadata, and verifies dirty count consistency.
- `alloc_idx_lebs()` estimates and reserves empty LEBs for the new index; debug mode can force `-ENOSPC` to test in-the-gaps behavior.
- `layout_in_empty_space()` assigns positions to dirty znodes in the index head and newly allocated index LEBs, updating parent/root references and lprops.
- `layout_in_gaps()` scans dirty index LEBs, identifies obsolete index-node gaps, and writes new index nodes into reusable space when empty LEB allocation is insufficient.
- `make_idx_node()` serializes a znode into an index node, calculates hashes, records old index references, updates parent/root branches, clears dirty/COW state under the TNC mutex, and updates calculated index size.
- `ubifs_tnc_start_commit()` validates TNC, builds the commit list, lays out positions, frees unused index LEBs, saves dirty index LEB numbers, updates budgeting’s committed index size, and returns the new root branch.
- `write_index()` serializes and writes index nodes laid out in empty space, updates branch hashes under `tnc_mutex`, clears dirty/COW flags with memory barriers, and advances the index head.
- `ubifs_tnc_end_commit()` returns gap LEBs, writes the index, frees obsolete znodes, clears `c->cnext`, and frees allocated index LEB arrays.

## Important Dependencies
- Uses `ubifs_scan()` from `scan.c` for in-the-gaps LEB analysis.
- Uses TNC membership helpers from `tnc.c`: `is_idx_node_in_tnc()` and old-index insertion.
- Updates lprops through `ubifs_update_one_lp()`, `ubifs_change_one_lp()`, and dirty-index LEB tracking.
- Depends on commit state shared with foreground TNC mutation and shrinker code.

## Invariants and Risks
- The previous committed index must remain intact until the new index is durably committed; old-index RB-tree tracking enforces this for hard-to-find obsolete nodes.
- Dirty flags must become visible as cleared before COW flags, hence explicit memory barriers in `write_index()`.
- Clean znode counter increments are delayed until obsolete znodes are freed under `tnc_mutex`, avoiding races with foreground dirtying.
- Gap commits require atomic in-place LEB update semantics via `ubifs_leb_change()`.
- Layout and write phases cross-check expected znode positions and index head offsets to catch commit accounting bugs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/tnc_commit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/tnc_misc.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/tnc_misc.c

## Purpose
Provides shared TNC helpers for traversal, zbranch binary search, TNC destruction, loading index znodes from flash, and reading leaf nodes.

## Key Behavior
- `ubifs_tnc_levelorder_next()` supports level-order traversal, mainly used by the shrinker to reclaim clean subtrees.
- `ubifs_search_zbranch()` binary-searches a znode’s sorted branches and returns either exact match or the left-nearest slot.
- `ubifs_tnc_postorder_first()` and `ubifs_tnc_postorder_next()` support safe subtree destruction.
- `ubifs_destroy_tnc_subtree()` frees all znodes in a subtree and returns the number of clean znodes freed.
- `ubifs_destroy_tnc_tree()` destroys the whole cached TNC and adjusts the global clean znode counter.
- `read_znode()` reads an on-flash index node, validates hash, branch count, level, branch addresses, key types, leaf-node length ranges, and sorted key order.
- `ubifs_load_znode()` allocates a znode, fills it from an index node, links it into the parent branch, timestamps it, and increments clean znode counters.
- `ubifs_tnc_read_node()` reads a leaf node through a journal write buffer if needed, validates the key and node hash, and returns errors for mismatches.

## Important Dependencies
- Uses UBIFS key comparison/read/write helpers and node validation/hash helpers.
- Clean znode counters are consumed by `shrinker.c`.
- TNC lookup and mutation paths in `tnc.c` rely on these helpers for lazy loading and tree traversal.

## Invariants and Risks
- Index-node validation rejects malformed branch positions outside the main area, unaligned offsets, invalid key types, impossible lengths, and invalid non-hash duplicate keys.
- Znodes are allocated with size dependent on superblock fanout, so no fixed slab cache is used.
- LNC leaf payloads are ignored by traversal/destruction helpers; leaf cache memory is managed where branches are removed or replaced.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/tnc_misc.c -->