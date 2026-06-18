# Group Research: group_211_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_debug_sysfs_c_source_a1f7b18b13df

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.c

Implements bcachefs sysfs/debug interfaces for filesystem objects, internal debug state, counters, options, time stats, transaction stats JSON, and per-device status/settings.

Key entry points:
- `bch2_fs_show()` / `bch2_fs_store()` expose top-level filesystem attributes and trigger manual maintenance/debug actions.
- `bch2_fs_counters_show()` reports persistent counters since mount and since filesystem creation.
- `bch2_fs_internal_show()` / `bch2_fs_internal_store()` wrap the main fs handlers for the internal sysfs directory.
- `bch2_btree_trans_stats_json_read()` / `bch2_btree_trans_stats_json_write()` expose/reset btree transaction timing and memory stats as a binary JSON attribute.
- `sysfs_opt_show()` / `sysfs_opt_store()` implement generic fs/device option read/write handling through `bch2_opt_table`.
- `bch2_opts_create_sysfs_files()` creates sysfs files for visible options by option type.
- `bch2_fs_time_stats_show()` / JSON variant expose/reset `BCH_TIME_STATS()`.
- `bch2_dev_show()` / `bch2_dev_store()` expose per-device UUID, bucket ranges, labels, data classes, IO counters/errors, latency stats, allocation debug, discards, refs, and device options.

Core mechanics:
- Local macros generate sysfs attributes and `sysfs_ops`, normalize show output through `printbuf`, and map bcachefs-specific errors back to class errno values with `bch2_err_class()`.
- Write-only trigger attributes call GC, discard, invalidate, journal, btree cache shrink, write-buffer flush, reconcile, snapshot cleanup, capacity recalculation, and emergency read-only paths.
- Mutating fs triggers acquire `BCH_WRITE_REF_sysfs` to reject read-only state cleanly.
- Option writes parse text, take option-change locking, run pre/post hooks, update superblock-backed or runtime fs options, and clear mount-option override bits when appropriate.
- Transaction stats JSON is cached across kernfs chunked reads so one user read sees consistent JSON even when output exceeds one page.
- Device sysfs paths reuse the same option helpers with a `struct bch_dev *` when an option is per-device.

Important invariants:
- Sysfs show handlers must fit the copied result to `PAGE_SIZE - 1`.
- Internal trigger writes require the filesystem to be started.
- FS-level sysfs files skip options that are also device/member options to avoid ambiguous or no-op FS writes.
- Option changes must run under `PF_MEMALLOC_NOFS`, option-change locking, and opt-change hook scope.
- JSON transaction stats reads regenerate only at offset zero.

Filesystem relevance:
- This is the operator-facing diagnostics and control surface for bcachefs runtime state. It bridges core allocator, btree, journal, GC, counters, latency, and device subsystems into sysfs.

Notable risks:
- Several sysfs writes invoke powerful maintenance or emergency paths and rely on sysfs permissions plus started/read-only checks.
- Generic option exposure must keep option flags correct, or a device-only option could be exposed at the wrong scope.
- Cached JSON output correctness depends on offset-zero read sequencing and the shared stats lock.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.h

Declares the sysfs attribute lists and operation tables implemented by `debug/sysfs.c`.

Key declarations:
- Attribute arrays: `bch2_fs_files`, `bch2_fs_counters_files`, `bch2_fs_internal_files`, `bch2_fs_opts_dir_files`, `bch2_fs_time_stats_files`, `bch2_fs_time_stats_json_files`, and `bch2_dev_files`.
- Sysfs ops: `bch2_fs_sysfs_ops`, counter/internal/options/time-stats variants, and `bch2_dev_sysfs_ops`.
- Binary attribute: `bin_attr_btree_trans_stats_json`.
- Helper: `bch2_opts_create_sysfs_files(struct kobject *, unsigned)`.

Core mechanics:
- The header exposes only Linux sysfs-facing objects, not implementation details.
- Consumers can attach the correct attribute arrays and `sysfs_ops` to kobjects for fs, internal, options, time stats, and device directories.

Filesystem relevance:
- This is the public registration contract for bcachefs sysfs debug/control files.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.c

Implements optional `CONFIG_BCACHEFS_TESTS` btree iterator, update, snapshot, extent-overwrite, and performance tests callable through the sysfs `perf_test` attribute.

Key entry points:
- `bch2_btree_perf_test()` parses a named test, iteration count, and thread count, launches one or more kernel threads, times execution, and prints throughput.
- Unit-style tests cover delete idempotency, delete after journal flush, forward/reverse iteration, slots iteration, extent slot iteration, end peeking, extent overwrite cases, overlapping snapshot extents, and snapshot filtering.
- Performance tests include random insert, multi-insert, lookup, mixed lookup/update, delete, sequential insert, lookup, overwrite, and delete.
- `delete_test_keys()` clears test data from extents and xattrs btrees before many unit tests.

Core mechanics:
- Tests primarily use synthetic `bkey_i_cookie` keys in `BTREE_ID_xattrs` and `BTREE_ID_extents`.
- Iterator tests assert exact offsets, slot/deleted-key behavior, and reverse traversal ordering with `BUG_ON()`.
- Extent overwrite tests insert overlapping extents and rely on btree update behavior to split/overwrite correctly.
- Snapshot tests create snapshot nodes and verify unrelated snapshot keys are skipped as expected.
- Perf tests coordinate start/finish with atomics, wait queues, and completions so threads begin together and timing spans all workers.

Important invariants:
- `nr` and `nr_threads` must be nonzero.
- Unknown test names return `EINVAL_test_unknown_test`.
- Many checks intentionally use `BUG_ON()`, so this code is for controlled debug/test builds.
- Threaded tests divide iterations across `nr_threads`.

Filesystem relevance:
- Provides in-kernel stress and correctness coverage for bcachefs btree iteration/update semantics, especially areas that affect metadata lookup, extents, snapshots, and hash-table-like xattr/dirent behavior.

Notable risks:
- Test cleanup deletes broad key ranges in extents and xattrs btrees, so it is not a normal production data path.
- `BUG_ON()` assertions can crash a kernel when a test fails.
- Tests are compiled only under `CONFIG_BCACHEFS_TESTS` and exposed through sysfs only in that configuration.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.h

Declares the optional bcachefs debug test entry point.

Key declaration:
- Under `CONFIG_BCACHEFS_TESTS`, exposes `bch2_btree_perf_test(struct bch_fs *, const char *, u64, unsigned)`.

Core mechanics:
- Outside `CONFIG_BCACHEFS_TESTS`, the header provides no fallback implementation; callers are expected to guard use with the same config option.

Filesystem relevance:
- Connects sysfs debug test dispatch to the optional in-kernel btree test implementation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.c

Instantiates bcachefs tracepoints.

Key behavior:
- Includes core bcachefs, allocator, btree, data, and utility headers needed by tracepoint format code.
- Defines `CREATE_TRACE_POINTS` before including `debug/trace.h`, causing tracepoint definitions to be emitted in this compilation unit.

Filesystem relevance:
- Provides the concrete tracepoint objects used by bcachefs runtime tracing and debugging.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.h

Defines bcachefs tracepoint events for persistent counters, non-counter debug events, and optional btree path tracing.

Key elements:
- `TRACE_SYSTEM bcachefs` sets the Linux trace subsystem name.
- `DECLARE_EVENT_CLASS(fs_str)` defines common trace payload: filesystem name and string message.
- `BCH_NOCOUNTER_TRACEPOINTS()` lists debug-only tracepoints such as accounting insert, journal close, extent trim, and iterator/path events.
- `__BCH_PATH_TRACEPOINTS()` lists detailed path lifecycle/locking tracepoints.
- `BCH_PATH_TRACEPOINTS()` expands only when `CONFIG_BCACHEFS_PATH_TRACEPOINTS` is enabled.
- For disabled path tracepoints, inline no-op `trace_*()` and `trace_*_enabled()` stubs are provided.
- `BCH_PERSISTENT_COUNTERS()` also becomes trace events using the shared `fs_str` event class.

Important invariants:
- The trace include path/file block must remain outside the include guard per Linux tracepoint conventions.
- Disabled path tracepoints must compile away while preserving call-site availability.

Filesystem relevance:
- This header is bcachefs’s lightweight observability hook set for counters, journal/btree activity, and optional path-level btree tracing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/errcode.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/errcode.c

Implements bcachefs-specific error stringification, error-class matching, top-level errno class conversion, and block/ZSTD error mapping.

Key entry points:
- `bch2_err_str()` returns a printable string for standard errno values, bcachefs extended errors, zero, and invalid codes.
- `__bch2_err_matches()` walks the parent chain of a bcachefs extended error to test membership in an error class.
- `__bch2_err_class()` maps an extended negative error to its top-level standard errno-style class.
- `bch2_blk_status_to_str()` special-cases `BLK_STS_REMOVED` and otherwise delegates to block-layer status strings.
- `blk_status_to_bch_err()` maps block status values into typed bcachefs errors.
- `zstd_err_to_bch_err()` maps ZSTD error codes into typed bcachefs errors.

Core mechanics:
- `BCH_ERRCODES()` generates parallel name and parent arrays.
- Extended error codes live at `BCH_ERR_START` and form parent-child chains ending in standard errno classes or zero-class internal control errors.
- Public sysfs/ioctl paths can call `bch2_err_class()` to avoid leaking internal error identities where only standard errno should be returned.

Important invariants:
- Parent arrays and string arrays must remain generated from the same macro list.
- Callers pass negative errors to matching/class helpers; helpers normalize with `abs()` internally where appropriate.
- `BUG_ON()` guards assume invalid codes are programming errors.

Filesystem relevance:
- Provides consistent diagnostics and errno classification across bcachefs metadata, IO, recovery, fsck, compression, device, journal, and ioctl paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/errcode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/errcode.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/errcode.h

Defines the bcachefs extended error namespace and helpers for matching, classifying, and converting error types.

Key elements:
- `BLK_STS_REMOVED` reserves a custom block status value.
- `BLK_ERRS()` and `ZSTD_ERRS()` list block-layer and ZSTD errors that are wrapped as bcachefs errors.
- `BCH_ERRCODES()` is the central macro table for extended errors, including memory allocation sites, ENOSPC variants, lookup errors, transaction restart causes, fsck outcomes, recovery, device/state validation, ioctl validation, topology repair, EOPNOTSUPP cases, read-only/shutdown states, operation blocking, invalid superblocks, btree/data/journal IO errors, decompression/read/write errors, nocow failures, and shutdown-with-errors states.
- `enum bch_errcode` starts at `BCH_ERR_START = 2048` and expands the macro table to `BCH_ERR_MAX`.
- `bch2_err_matches()` requires a compile-time constant class and tests hierarchical error membership.
- `bch2_err_class()` converts negative extended errors to their top-level class.

Core mechanics:
- Each macro entry has a parent/class and a leaf error name. Parents may be standard errno values, zero-class control groups, or other bcachefs errors.
- The same table drives string generation, parent lookup, and enum values in `errcode.c`.
- Inline helpers preserve normal positive return values and only classify negative errors.

Important invariants:
- New errors must be added to `BCH_ERRCODES()` with the correct parent class, or matching/classification semantics become wrong.
- Error classes used with `bch2_err_matches()` must be constants so the build-time assertion works.
- Header guard closing comment contains a typo, but the actual guard macro is `_BCACHEFS_ERRCODE_H`.

Filesystem relevance:
- This file is the error taxonomy for bcachefs. It lets internal paths distinguish fine-grained causes while external APIs can still report stable errno classes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/errcode.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.c

Implements POSIX ACL serialization/deserialization, VFS get/set ACL hooks, ACL xattr updates, and chmod ACL adjustment.

Key entry points:
- `bch2_acl_to_text()` formats on-disk ACL xattr payloads for diagnostics.
- `bch2_get_acl()` looks up ACL xattrs, converts them to `struct posix_acl`, and caches them on the VFS inode.
- `bch2_set_acl_trans()` sets or deletes ACL xattrs in a btree transaction.
- `bch2_set_acl()` is the VFS-facing setter with inode update locking and transaction retry handling.
- `bch2_acl_chmod()` updates an access ACL after mode changes.

Core mechanics:
- On-disk ACLs start with `bch_acl_header` version `BCH_ACL_VERSION`, followed by short entries for owner/group/mask/other and long entries for named user/group.
- `bch2_acl_from_disk()` validates size, version, tags, and entry boundaries before allocating a POSIX ACL.
- `bch2_acl_to_xattr()` counts short/long entries, allocates a bcachefs xattr key, writes little-endian ACL entries, and rejects oversized values.
- ACLs are stored as xattrs using `KEY_TYPE_XATTR_INDEX_POSIX_ACL_ACCESS` or `KEY_TYPE_XATTR_INDEX_POSIX_ACL_DEFAULT`.
- Default ACLs are accepted only for directories; clearing a default ACL on a non-directory is a no-op.
- Access ACL set calls `posix_acl_update_mode()` and writes the updated mode/ctime back to the inode.

Important invariants:
- ACL xattr values must use the exact version and entry layout expected by the parser.
- `bch2_acl_from_disk()` may allocate while dropping transaction locks.
- Inode mode/ctime and ACL xattr updates are committed atomically in `__bch2_set_acl()`.
- Cached VFS ACLs are updated after successful commit.

Filesystem relevance:
- Provides bcachefs support for POSIX ACL permissions through the filesystem xattr btree and VFS ACL interface.

Notable risks:
- Malformed ACL xattrs return errors and print diagnostic messages.
- UID/GID conversion uses `init_user_ns`.
- Chmod ACL updates depend on the existing access ACL xattr being found and rewritten at the current hash position.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.h

Defines bcachefs on-disk ACL structures and declares ACL helper APIs.

Key elements:
- `BCH_ACL_VERSION` is the on-disk ACL format version.
- `bch_acl_header`, `bch_acl_entry_short`, and `bch_acl_entry` define the serialized ACL xattr format.
- Declares `bch2_acl_to_text()`.
- When filesystem/VFS support is enabled, declares `bch2_get_acl()`, `bch2_set_acl_trans()`, `bch2_set_acl()`, and `bch2_acl_chmod()`.
- Under `NO_BCACHEFS_FS`, transaction ACL set/chmod helpers are inline no-ops.

Filesystem relevance:
- This is the ACL format/API contract shared by xattr formatting, VFS hooks, and inode mode update code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.c

Implements the central bcachefs fsck logic for inode, dirent, xattr, root, subvolume, snapshot-visibility, backpointer, reflink migration, and online/offline fsck ioctl handling.

Key entry points:
- `bch2_check_inodes()` validates inode records, snapshot hash info, dirent backpointers, unlinked state, child-snapshot flags, subvolume links, and journal sequence bounds.
- `bch2_check_unreachable_inodes()` reattaches reachable-but-disconnected inodes to `lost+found`.
- `bch2_check_dirents()` validates dirents, hash-table placement, target inode/subvolume links, directory subdir counts, and overwritten snapshot targets.
- `bch2_check_xattrs()` validates xattr hash placement and inode ownership.
- `bch2_check_key_has_inode()` is shared by extents/dirents/xattrs to ensure a key belongs to an existing inode of the right mode, reconstructing or deleting when repair policy allows.
- `bch2_check_root()` recreates missing root subvolume/root directory metadata.
- `bch2_fix_reflink_p()` migrates old reflink pointer padding fields for pre-fix metadata versions.
- `bch2_fs_fsck_errcode()` translates fixed/unfixed/fatal filesystem flags into fsck command return bits.
- `bch2_ioctl_fsck_offline()` and `bch2_ioctl_fsck_online()` run fsck through `thread_with_stdio`.

Core mechanics:
- `snapshots_seen` tracks snapshot IDs already seen at a btree position so visibility through snapshot ancestry can be evaluated.
- `inode_walker` caches all inode versions/whiteouts for an inode number and supports cross-pass checking by extents, dirents, and xattrs.
- Missing `lost+found` directories are created in the root snapshot of a snapshot tree before reattaching inodes.
- `bch2_reattach_inode()` creates a lost+found dirent, updates inode backpointers, adjusts lost+found nlink, fixes subvolume parent metadata, and handles child snapshots with backpointer updates or whiteouts.
- Missing inodes may be reconstructed from extents, dirents, or xattrs, with mode inferred from the btree and size inferred from extent end.
- Missing subvolume records may be reconstructed when the subvolume btree lost data and a leaf snapshot/root inode context exists.
- Dirent checks distinguish normal inode targets from `DT_SUBVOL` targets, repairing parent subvolumes and subvolume root backpointers separately.
- Online fsck restricts recovery passes to those marked online-capable and temporarily switches fsck options/stdout state under the recovery run lock.

Important invariants:
- Snapshot visibility is ancestry-based and also considers overwrites already seen at the same logical position.
- Keys in extents/dirents/xattrs must have matching inode versions in the same snapshot or a valid visible ancestor, otherwise the checker repairs by writing missing versions, reconstructing, or deleting.
- Subvolume root handling is special because older versions of renamed subvolume roots may intentionally lack valid dirents.
- Unlinked inodes are not always deleted offline; they may be preserved on the deleted list until logged operations resume.
- Repair commits often deliberately return transaction restart errors to force callers to rescan after structural changes.
- `lost+found` is created in one transaction because creation can force restart behavior.

Filesystem relevance:
- This is the fsck coordination layer for bcachefs namespace and inode consistency. It ties together inodes, dirents, xattrs, subvolumes, snapshots, and repair policy.

Notable risks:
- Online fsck is explicitly racy with some concurrent namespace operations, including hardlink removal comments.
- Some repairs are unimplemented for interior snapshot subvolume reconstruction or missing subvolume roots.
- Wrong inode mode with both extents and dirents is treated as unrecoverable.
- Stdio and option state are temporarily installed on the live filesystem during online fsck and must be restored on exit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.h

Declares fsck shared state types and public checker/repair APIs.

Key elements:
- `struct snapshots_seen` stores the current btree position and a list of snapshot IDs observed there.
- `struct inode_walker_entry` stores an unpacked inode or whiteout plus accumulated counts.
- `struct inode_walker` tracks inode versions, delete snapshots, current inode position, and whether aggregate counts need recalculation.
- RAII-style `DEFINE_CLASS` helpers clean up dynamic arrays for `snapshots_seen` and `inode_walker`.
- Declares snapshot visibility helpers, inode walking, mismatch text formatting, inode reattachment, backpointer update, key-has-inode checking, fsck passes, reflink fixup, fsck errcode conversion, and online/offline fsck ioctl handlers.

Filesystem relevance:
- This header is the shared contract between fsck passes in `check.c`, `check_extents.c`, `check_dir_structure.c`, and `check_nlinks.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_dir_structure.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_dir_structure.c

Implements fsck passes for subvolume path structure and directory loop/depth validation.

Key entry points:
- `bch2_check_subvolume_structure()` walks the subvolumes btree and validates parent path chains.
- `bch2_check_directory_structure()` walks directory inodes and checks parent-backpointer chains for loops.
- `check_subvol_path()` detects subvolume parent loops or unreachable parent subvolume links and reattaches broken subvolumes.
- `check_path_loop()` follows inode dirent backpointers toward a subvolume/root, detects loops, repairs by removing bad backpointers and reattaching, and renumbers `bi_depth` where needed.

Core mechanics:
- Subvolume path checking follows `fs_path_parent` through the subvolume btree until `BCACHEFS_ROOT_SUBVOL`.
- Directory loop checking follows each directory inode’s `bi_dir`/`bi_dir_offset` dirent backpointer and parent inode chain.
- `remove_backpointer()` verifies the dirent points back to the inode, removes the dirent, and clears namespace attachment before reattachment.
- `bch2_bi_depth_renumber()` walks the remembered path in reverse and updates directory `bi_depth` to maintain increasing depth from root.

Important invariants:
- Subvolume parent chains must terminate at the root subvolume without cycles.
- Directory parent chains must not loop and must converge to a subvolume root or a valid root path.
- `bi_depth` should be monotonic along parent chains; bad depths are repaired after traversal.
- Full fsck assumes earlier dirent checks already fixed missing or bad dirent backpointers.

Filesystem relevance:
- Protects namespace tree topology: directories and subvolumes must form an acyclic reachable hierarchy for path lookup and fsck repair to be meaningful.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_dir_structure.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_extents.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_extents.c

Implements fsck checks for extent ownership, inode sector accounting, overlapping extents across snapshots, stale pointers, and overlarge encoded extents.

Key entry points:
- `bch2_check_extents()` walks the extents btree and validates extent/inode relationships.
- `bch2_check_indirect_extents()` walks the reflink btree for stale pointer and encoded-size checks.
- `check_extent()` performs per-extent snapshot, inode, overlap, past-EOF, overbig encoded extent, stale pointer, commit, and sector-count accounting work.
- `check_i_sectors()` / `check_i_sectors_notnested()` reconcile inode `bi_sectors` against counted allocated extent sectors.
- `check_overlapping_extents()` and `overlapping_extents_found()` detect and repair visible overlapping extents in snapshot-aware order.

Core mechanics:
- `snapshots_seen` records overwrites at a position so visibility of older extents in descendant snapshots can be determined.
- `extent_ends` tracks the latest extent end per snapshot and its snapshot visibility context.
- Overlap repair chooses which visible extent to overwrite, handles extent whiteouts specially, updates compressed-sector reservation accounting, and may force nested transaction restarts.
- Past-EOF extents are punched from the affected snapshot unless they are reservations.
- `bch2_bkey_drop_stale_ptrs()` is called after validation to remove stale physical pointers.
- Sector counts are accumulated only for visible allocated extents and later compared with inode `bi_sectors` unless the inode marks sectors dirty.

Important invariants:
- Extent keys must belong to regular-file or symlink inodes.
- Visible extents for the same inode/snapshot lineage must not overlap.
- Encoded extents should not exceed `encoded_extent_max`.
- Sector accounting must ignore whiteouts and respect snapshot visibility.
- Transaction restarts are handled carefully because post-commit accounting cannot use stale key references.

Filesystem relevance:
- This pass validates the data extent namespace and inode size/sector consistency, central to preventing duplicate logical ownership and stale physical references.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_nlinks.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_nlinks.c

Implements fsck reconciliation of hardlink counts for non-directory inodes.

Key entry point:
- `bch2_check_nlinks()` iteratively builds a table of candidate hardlinked inodes, counts dirent references, and updates inode nlink values.

Core mechanics:
- `check_nlinks_find_hardlinks()` scans inode records and records non-directory inodes with stored `bi_nlink` values.
- `check_nlinks_walk_dirents()` scans all dirents, using snapshot visibility to increment target link counts for non-directory/non-subvolume dirents.
- `check_nlinks_update_hardlinks()` walks matching inode ranges and calls `check_nlinks_update_inode()` to repair wrong nlink counts.
- The nlink table is dynamically grown with `kvmalloc_array()` and sorted/searched by inode number.
- The pass processes ranges so memory allocation failure can cap the current range and resume later.

Important invariants:
- Directories are excluded because directory backpointer and subdir count checks cover them.
- Snapshot visibility determines whether a dirent contributes to a given inode version.
- `bch2_inode_nlink_get()` / set semantics include bcachefs’s directory/non-directory bias and unlinked flag behavior.

Filesystem relevance:
- Keeps inode hardlink counts consistent with the dirent graph, affecting link/unlink correctness and deletion eligibility.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_nlinks.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.c

Implements bcachefs dirent hashing, validation, creation, lookup, rename, empty-directory checks, readdir, and fsck dirent removal.

Key entry points:
- `bch2_casefold()` casefolds names when Unicode support and filesystem casefolding are enabled.
- `bch2_dirent_validate()` validates dirent names, casefold data, target self-links, name length, slash/dot entries, and embedded NULs.
- `bch2_dirent_init_name()` initializes normal or casefolded name payloads and shrinks the key value length.
- `bch2_dirent_create_key()`, `bch2_dirent_create_snapshot()`, and `bch2_dirent_create()` allocate and insert dirent keys.
- `bch2_dirent_read_target()` resolves normal inode targets or `DT_SUBVOL` targets into `subvol_inum`.
- `bch2_dirent_rename()` performs rename, overwrite, and exchange while preserving hash-table whiteout requirements and subvolume-dirent special rules.
- `bch2_dirent_lookup_trans()` / `bch2_dirent_lookup()` perform hash lookup with optional casefolding.
- `bch2_empty_dir_snapshot()` / `bch2_empty_dir_trans()` test directory emptiness.
- `bch2_readdir()` emits visible dirents to VFS/FUSE directory context.
- `bch2_fsck_remove_dirent()` removes a dirent through the hash-delete path during fsck.

Core mechanics:
- Dirents use `bch2_dirent_hash_desc` with the dirents btree, key type `KEY_TYPE_dirent`, 64-bit string hash, linear probing, key and bkey comparison callbacks, and subvolume visibility filtering.
- Lookup names are either stored names or casefolded names depending on `d_casefold`.
- Hash values reserve offsets 0 and 1 for dot entries by clamping to at least 2.
- Rename handles collision holes, source deletion whiteouts, overwrite/exchange target creation, and the special rule that subvolume dirents are physically deleted when moving between snapshots.
- `readdir()` copies keys into a `bkey_buf` before dropping transaction locks for `dir_emit()`.

Important invariants:
- `.` and `..` are not stored as normal dirents.
- Names cannot contain `/`, be empty, or exceed `BCH_NAME_MAX` for newly committed keys.
- Casefolded dirs require the filesystem casefold feature/encoding.
- Hash-table deletion must leave whiteouts when linear probing requires them.
- `DT_SUBVOL` dirents are visible only from their recorded parent subvolume.
- `ctx->pos` is updated for FUSE compatibility as well as VFS behavior.

Filesystem relevance:
- This is the namespace directory-entry engine for bcachefs: it maps directory/name pairs to inodes or subvolumes and underpins lookup, rename, readdir, and fsck namespace repair.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.h

Declares dirent hash operations, validation/text hooks, lookup/create/rename/readdir APIs, and small helpers.

Key elements:
- `bch2_dirent_hash_desc` is the shared hash descriptor for dirents.
- `bch2_bkey_ops_dirent` wires validation, text formatting, and minimum value size into bkey operations.
- Casefold APIs are declared when Unicode support exists; otherwise `bch2_casefold()` returns `no_casefolding_without_utf8`.
- `bch2_maybe_casefold()` returns the original string for non-casefolded directories or the folded lookup name otherwise.
- `dirent_val_u64s()` computes the value size for normal and casefolded names.
- `dirent_get_by_pos()` initializes a dirents iterator and fetches a typed dirent at an exact position.
- Declares create, read target, rename, lookup, empty-dir, readdir, and fsck removal helpers.
- `vfs_d_type()` maps bcachefs `DT_SUBVOL` to VFS `DT_DIR`.

Filesystem relevance:
- This is the shared namespace API used by VFS operations, fsck, subvolume handling, and inode backpointer repair.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent_format.h

Defines the on-disk bcachefs dirent value format and directory-name constants.

Key elements:
- Dirent keys store a 64-bit string hash in the key offset and resolve collisions by linear probing.
- `struct bch_dirent` stores either a target inode number or parent/child subvolume IDs for `DT_SUBVOL`.
- `d_type` stores file type bits copied from target inode mode; `d_casefold` indicates the casefolded-name layout.
- Non-casefolded entries store a flexible `d_name`.
- Casefolded entries store original length, folded length, and concatenated original/folded names in `d_cf_name_block`.
- Defines `DT_SUBVOL = 16`, `BCH_DT_MAX = 17`, and `BCH_NAME_MAX = 512`.

Important invariants:
- Linear probing requires hash whiteouts on deletion when collisions exist.
- Dirent values are packed and 8-byte aligned.
- Subvolume dirents encode two 32-bit subvolume IDs instead of an inode number.

Filesystem relevance:
- This is the persistent directory-entry ABI that lookup, rename, readdir, and fsck code interpret.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.c

Implements bcachefs inode packing/unpacking, validation, lookup, writeback, triggers, allocation, deletion, link counts, inode options, casefold enabling, snapshot cleanup, and deleted-inode processing.

Key entry points:
- `bch2_inode_pack()` and `bch2_inode_unpack()` convert between `bch_inode_unpacked` and on-disk v1/v2/v3 inode keys.
- `bch2_inode_validate()`, v2, and v3 variants validate inode key position, field encoding, checksum/compression options, unlinked/nlink state, subvolume-root mode, string hash, and v3 field start.
- `__bch2_inode_peek()`, `bch2_inode_find_by_inum_snapshot()`, and find helpers load inode records through subvolume snapshot resolution.
- `bch2_inode_write_flags()`, `__bch2_fsck_write_inode()`, and `bch2_fsck_write_inode()` write packed inode keys.
- `bch2_trigger_inode()` updates journal sequence, disk accounting, deleted-inodes bits, and parent `has_child_snapshot` flags.
- `bch2_inode_init_early()`, `bch2_inode_init_late()`, and `bch2_inode_init()` initialize new unpacked inodes.
- `bch2_inode_create()` allocates inode numbers using logged inode allocation cursors.
- `bch2_inode_rm()` deletes inode contents, xattrs, inode record, and eligible ancestor snapshot inodes.
- `bch2_inode_nlink_inc()` / `bch2_inode_nlink_dec()` update encoded link count and unlinked flag.
- `bch2_inode_opts_to_opts()` / `bch2_inode_opts_get_inode()` convert inherited inode options into runtime IO options.
- `bch2_inode_set_casefold()` enables directory casefolding after empty-dir and feature checks.
- `bch2_delete_dead_inodes()` drains the deleted-inodes btree and removes eligible unlinked inode snapshots.
- `bch2_kill_i_generation_keys()` deletes obsolete inode generation keys.

Core mechanics:
- v3 inodes store journal sequence, hash seed, flags, sectors, size, version, mode, and variable-length fields encoded with fast varints.
- Older v1/v2 inode formats are unpacked through slow paths and can be converted to v3 with `bch2_inode_to_v3()`.
- Inode allocation uses per-CPU or 32-bit cursor records in `BTREE_ID_logged_ops`, supports sharded inode spaces, wraps with generation increments, and skips existing inode/generation records visible in the target snapshot.
- Inode triggers maintain `BCH_INODE_has_child_snapshot` on parent snapshot inode versions when child versions are inserted/deleted.
- Deleted inode tracking is buffered in `BTREE_ID_deleted_inodes` for unlinked inodes without child snapshots.
- Inode removal deletes extents for non-directories, dirents/whiteouts for directories, xattrs for all, then removes the inode key and cleans up older unlinked ancestors when safe.
- Casefold is a directory-only inode option; enabling it requires the directory to be empty, requests the metadata incompat feature, and propagates case-insensitive state.

Important invariants:
- Filesystem inode keys must have `k.p.inode == 0` and offsets outside the block-device inode range.
- Inode variable fields must decode without overflow into `bch_inode_unpacked`.
- Unlinked inodes encode zero visible nlink through `BCH_INODE_unlinked`.
- Subvolume roots must be directories.
- Inode writes through fsck use internal snapshot-node flags and may force transaction restarts.
- Directories with casefold enabled cannot already contain entries because dirent hashes would need rehashing.

Filesystem relevance:
- This is bcachefs’s inode metadata core. It defines how inode records are encoded, found, mutated, accounted, linked to snapshots, and eventually deleted.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.h

Declares inode bkey operations, the unpacked inode representation, inode lookup/write/create/delete APIs, link-count helpers, inode option helpers, and subvolume inode constants.

Key elements:
- `bch2_bkey_ops_inode`, v2, and v3 wire validation, text formatting, trigger, and minimum value size.
- `bkey_is_inode()` identifies all inode key versions.
- `bch2_bkey_ops_inode_generation` and `bch2_bkey_ops_inode_alloc_cursor` define support key types.
- `struct bch_inode_unpacked` is the in-memory normalized inode representation used by VFS, fsck, and metadata code.
- `struct bkey_inode_buf` provides enough storage to pack a v3 inode plus all variable fields.
- Declares pack/unpack, v3 conversion, text formatting, lookup, oldest-snapshot lookup, write, fsck write, initialization, creation, deletion, nlink, option, casefold, and dead-inode cleanup helpers.
- Inline helpers handle inode option biasing, mode-to-type conversion, `DT_SUBVOL` reporting, flags extraction, casefold inheritance, backpointer presence, and nlink bias.
- Defines `BCACHEFS_ROOT_SUBVOL_INUM` and `subvol_inum_eq()`.

Important invariants:
- Inode options are stored with a +1 bias: zero means inherit filesystem/default option.
- Directory nlink has a different bias than non-directories.
- `bch2_inode_casefold()` falls back to filesystem option when inode option is unset.
- `bch2_inode_has_backpointer()` treats either `bi_dir` or `bi_dir_offset` as a backpointer.

Filesystem relevance:
- This is the main shared inode API surface for bcachefs metadata, VFS, fsck, dirent, ACL, and data-reconciliation code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode_format.h

Defines the persistent bcachefs inode formats, inode variable fields, inode options, inode flags, bitfield accessors, and inode allocation cursor format.

Key elements:
- `BLOCKDEV_INODE_MAX` reserves low inode numbers; `BCACHEFS_ROOT_INO` is 4096.
- `struct bch_inode`, `bch_inode_v2`, and `bch_inode_v3` define three on-disk inode value layouts.
- `struct bch_inode_generation` stores generation keys.
- `BCH_INODE_FIELDS_v2()` and `BCH_INODE_FIELDS_v3()` enumerate variable-length inode fields such as times, uid/gid, nlink, generation, device, checksum/compression, project, replication/target options, dir backpointers, subvolume IDs, nocow, depth, 32-bit inode selection, and casefold.
- `BCH_INODE_OPTS()` identifies the subset of fields treated as inherited inode options.
- `enum inode_opt_id` indexes inode options.
- `BCH_INODE_FLAGS()` defines inode flags including sync, immutable, append, nodump, noatime, dirty size/sectors, unlinked, backptr untrusted, child snapshot, case-insensitive descendant, and 31-bit dirent offset.
- Bitmask macros define packed string-hash, field-count, v3 field-start, and v3 mode fields.
- `struct bch_inode_alloc_cursor` stores allocation cursor bits, generation, and next index.

Important invariants:
- v3 mode is packed into inode flags bits rather than a standalone `bi_mode` field.
- Bits 20 and above in inode flags are reserved for packed field metadata.
- `bi_subvol` and `bi_parent_subvol` are only for subvolume roots.
- On-disk structs are packed and 8-byte aligned.

Filesystem relevance:
- This file is the persistent inode ABI. Inode parsing, validation, fsck repair, and compatibility migration all depend on these layouts and field lists.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode_format.h -->