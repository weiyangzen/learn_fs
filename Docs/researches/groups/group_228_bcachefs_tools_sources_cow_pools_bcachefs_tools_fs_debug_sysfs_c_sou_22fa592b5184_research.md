# Group Research: group_228_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_debug_sysfs_c_sou_22fa592b5184

Scope: learn_fs subset A, source tree `sources/cow-pools/bcachefs-tools`. I read each listed source file completely and summarized its role, APIs, control flow, state, dependencies, and repair/debug risks.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.c

## Purpose

Implements bcachefs sysfs attribute handlers for filesystem-wide state, internal debug state, counters, time stats, filesystem options, per-device state, and debug/test triggers. It is a glue layer: most attributes dispatch into allocator, btree, journal, recovery, compression, counter, device, and dirent helpers.

## Main Interfaces

- `bch2_fs_sysfs_ops`, `bch2_fs_counters_sysfs_ops`, `bch2_fs_internal_sysfs_ops`, `bch2_fs_opts_dir_sysfs_ops`, `bch2_fs_time_stats_sysfs_ops`, `bch2_fs_time_stats_json_sysfs_ops`, `bch2_dev_sysfs_ops`.
- Attribute arrays exported for kobject setup: `bch2_fs_files`, `bch2_fs_counters_files`, `bch2_fs_internal_files`, `bch2_fs_opts_dir_files`, `bch2_fs_time_stats_files`, `bch2_fs_time_stats_json_files`, `bch2_dev_files`.
- Binary sysfs attribute `bin_attr_btree_trans_stats_json`.
- `bch2_opts_create_sysfs_files()` dynamically creates option attributes for filesystem or device scopes.

## Behavior

`SHOW()` and `STORE()` macros wrap text conversion and parsing into sysfs-compatible callbacks, normalize errors through `bch2_err_class()`, and cap show output to a page. The filesystem show path exposes selected public attributes plus internal diagnostics such as journal state, btree caches, open buckets, discards, replicas, disk groups, moving contexts, recent counters, and filldir64 specialization.

The filesystem store path handles debug triggers: GC, discards, invalidates, journal commits/flushes/writes, btree cache shrinkers, write buffer flush, freelist wakeup, capacity recalculation, reconcile wakeups, snapshot deletion, emergency read-only, and optional `perf_test`. Most write actions require the filesystem to be started; mutating triggers use `enumerated_ref_tryget(&c->writes, BCH_WRITE_REF_sysfs)` to reject read-only state.

Option show/store maps sysfs filenames to `bch2_opt_table` entries. Device-backed options are intentionally not duplicated at FS scope when an FS/device option would alias ambiguously. Option writes parse text, take write refs and option-change locking, update superblock/member-backed or runtime options, and run pre/post hooks.

The JSON btree transaction stats bin attribute caches multi-page JSON under a mutex and regenerates only at offset zero to avoid inconsistent reads across kernfs chunks.

## State And Side Effects

This file mutates global filesystem/device runtime state through sysfs writes: journal flushing, GC scheduling, discard/invalidate work, counters, time-stat resets, device labels, IO error resets, and mount/device options. Per-device show handlers expose UUIDs, bucket ranges, group labels, device data types, IO counters/errors, latency stats, congestion, alloc debug, open buckets, discard state, and read/write refs.

## Dependencies

Depends broadly on bcachefs core modules: alloc, btree, data movement/compression/reconcile, fs dirent/inode, journal, init/recovery, superblock counters/errors/io, enumerated refs, Linux sysfs, blockdev, sorting, and scheduler clock. `CONFIG_BCACHEFS_TESTS` adds the `perf_test` attribute, and latency accounting gates `congested`.

## Risks And Notes

The file is intentionally privileged and sharp-edged: sysfs writes can force major maintenance work or emergency read-only. Error class conversion matters because many internal bcachefs errors have custom classes. The option scope filtering for mixed FS/device options prevents silent no-op writes and ambiguous reads. The transaction stats JSON cache is important for correctness with multi-page sysfs bin reads.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.h

## Purpose

Declares the sysfs entry points and attribute lists implemented by `debug/sysfs.c`.

## Main Interfaces

Exports attribute arrays for filesystem, counter, internal, option, time-stat, JSON time-stat, and device directories. Exports the corresponding `struct sysfs_ops` objects, `bin_attr_btree_trans_stats_json`, and `bch2_opts_create_sysfs_files()`.

## Dependencies

Includes Linux sysfs declarations and forward-declares `struct attribute` and `struct sysfs_ops`.

## Notes

This header is purely declarative. It defines the contract consumed by bcachefs kobject setup code and keeps sysfs registration decoupled from the large implementation file.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/tests.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/tests.c

## Purpose

Provides optional btree unit/performance tests compiled under `CONFIG_BCACHEFS_TESTS`. The tests are invoked from sysfs `perf_test` and exercise btree insertion, lookup, deletion, iteration, extent overwrite behavior, snapshot filtering, and deliberately corrupted extent cases.

## Main Interfaces

- `bch2_btree_perf_test(struct bch_fs *c, const char *testname, u64 nr, unsigned nr_threads)`.
- Internal named tests selected by string: random insert/multi-insert/lookup/mixed/delete, sequential insert/lookup/overwrite/delete, delete tests, forward/reverse iteration, slot iteration, extent overwrite variants, overlapping extent creation, duplicate physical extent injection, and snapshot filtering.

## Behavior

The file deletes prior test keys from `extents` and `xattrs`, inserts cookie keys or extents, and validates iterator behavior with `BUG_ON()` assertions. Extent overwrite tests insert overlapping logical ranges and rely on btree update semantics. Snapshot tests create snapshot nodes and verify lookup filtering.

Performance tests run a selected function across one or more kthreads. A shared `test_job` synchronizes thread start with atomics and a waitqueue, records `sched_clock()` timing, waits for completion, and prints total time, nanoseconds per iteration, and throughput.

## State And Side Effects

Tests mutate live btrees, especially `BTREE_ID_xattrs` and `BTREE_ID_extents`, and can inject intentionally malformed duplicate physical extents for fsck repair validation. They flush journal pins in `test_delete_written()` and may create snapshot nodes. The code is not a passive diagnostic; it is a destructive/internal test harness.

## Dependencies

Uses bcachefs btree update/iterator APIs, bucket allocation headers, journal reclaim, snapshot creation, kernel kthreads, random bytes, and the test declaration header.

## Risks And Notes

Many failures use `BUG_ON()`, so this is for controlled testing only. `bch2_btree_perf_test()` rejects zero iterations or zero threads with custom `EINVAL_test_*` errors. Unknown test names are also custom error returns.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/tests.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/tests.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/tests.h

## Purpose

Declares the optional test harness API.

## Main Interfaces

When `CONFIG_BCACHEFS_TESTS` is enabled, exports:

- `int bch2_btree_perf_test(struct bch_fs *, const char *, u64, unsigned);`

When tests are disabled, it exports no fallback function.

## Notes

This header keeps sysfs test invocation conditional and avoids exposing test code in non-test builds.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/tests.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/trace.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/trace.c

## Purpose

Instantiates bcachefs tracepoints.

## Behavior

Includes required bcachefs types and subsystem headers, defines `CREATE_TRACE_POINTS`, then includes `debug/trace.h`. This causes the tracepoint declarations in the header to emit definitions in this compilation unit.

## Dependencies

Pulls in alloc, btree cache/iter/key-cache/locking/interior, keylist, move types, six locks, and Linux blktrace API so tracepoint argument types and helpers are visible.

## Notes

There is no runtime logic beyond tracepoint definition instantiation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/trace.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/debug/trace.h

## Purpose

Defines bcachefs tracepoint declarations for string-valued filesystem events.

## Main Interfaces

- Trace system name: `bcachefs`.
- Event class `fs_str(struct bch_fs *c, const char *str)` records filesystem name and string payload.
- Tracepoint sets:
  - Persistent counters via `BCH_PERSISTENT_COUNTERS()`.
  - Non-counter tracepoints such as `accounting_mem_insert`, `journal_entry_close`, `extent_trim_atomic`, and btree iterator events.
  - Optional path tracepoints under `CONFIG_BCACHEFS_PATH_TRACEPOINTS`.

## Behavior

When path tracepoints are disabled, inline no-op `trace_*()` and `trace_*_enabled()` stubs are provided for path tracepoints so callers compile away cleanly.

## Dependencies

Uses Linux tracepoint infrastructure and must be included through `trace/define_trace.h` with `TRACE_INCLUDE_PATH` pointing to `../../fs/bcachefs/debug`.

## Notes

Tracepoints accept free-form strings rather than structured bcachefs objects. This keeps instrumentation lightweight but places formatting responsibility on callers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/debug/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/errcode.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/errcode.c

## Purpose

Implements bcachefs custom error-code naming, hierarchy matching, class reduction, and conversions from block and zstd errors.

## Main Interfaces

- `const char *bch2_err_str(int err)`.
- `bool __bch2_err_matches(int err, int class)`.
- `int __bch2_err_class(int bch_err)`.
- `const char *bch2_blk_status_to_str(blk_status_t status)`.
- `enum bch_errcode blk_status_to_bch_err(blk_status_t err)`.
- `enum bch_errcode zstd_err_to_bch_err(ZSTD_ErrorCode err)`.
- `int __bch2_err_throw(struct bch_fs *c, int err)`.

## Behavior

`BCH_ERRCODES()` generates string and parent-class tables. `bch2_err_str()` returns custom names for bcachefs errors, Linux `errname()` for standard errno values, and explicit invalid/no-error strings. Matching walks parent classes until the requested class or a root is found. Class reduction maps a custom error back to its top-level standard errno-like class.

Block status and zstd errors are converted through generated switch statements. `__bch2_err_throw()` increments the persistent `error_throw` counter and emits `trace_error_throw()` before returning the negative error.

## Dependencies

Depends on `errcode.h`, Linux `errname`, block status strings, zstd error enums, persistent counters, and tracepoints.

## Notes

The hierarchy lets code test broad classes like `ENOENT` or bcachefs-specific classes while preserving detailed leaf errors for diagnostics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/errcode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/errcode.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/errcode.h

## Purpose

Defines the complete bcachefs custom error-code namespace and helper APIs.

## Main Interfaces

- `enum bch_errcode` starts custom values at `BCH_ERR_START = 2048`.
- `BCH_ERRCODES()` x-macro lists all custom errors with parent classes.
- Helper macros/functions:
  - `bch2_err_matches(err, class)`.
  - `bch2_err_class(err)`.
  - block and zstd conversion declarations.

## Error Families

The macro covers block-device status, zstd failures, option parsing, allocation and ENOSPC sites, missing objects, btree transaction restarts, no-btree-node conditions, btree insert failures, fsck outcomes, recovery scheduling, bucket/data-update conditions, user permission errors, ioctl validation, invalid superblocks/bkeys, journal/blocking states, btree/data read-write failures, stripe/erasure-coding failures, decompression/read retry cases, no-promote outcomes, nocow failures, shutdown errors, and many targeted `EINVAL`/`EROFS` cases.

## Behavior

Each entry is written as `x(parent_class, leaf_name)`. Parents can be standard errno values or other bcachefs custom codes, allowing hierarchical matching and class reduction in `errcode.c`.

## Dependencies

Includes Linux block types and zstd error declarations after defining the enum.

## Risks And Notes

This file is central to error semantics. Adding, renaming, or reparenting entries changes string output, trace output, class matching, and user-visible/sysfs/ioctl error behavior. The enum order also backs generated lookup tables.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/errcode.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/acl.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/acl.c

## Purpose

Implements bcachefs POSIX ACL encoding, decoding, xattr conversion, VFS get/set hooks, and chmod ACL updates.

## Main Interfaces

- `bch2_acl_to_text()` prints on-disk ACL xattr values.
- Under `!NO_BCACHEFS_FS`:
  - `bch2_get_acl()`.
  - `bch2_set_acl_trans()`.
  - `bch2_set_acl()`.
  - `bch2_acl_chmod()`.

## Behavior

On-disk ACLs begin with `bch_acl_header` version `BCH_ACL_VERSION`, then short or long entries. Short entries are used for object/mask/other tags; long entries include UID/GID for user/group entries.

`bch2_acl_from_disk()` validates version, size, entry tags, and entry boundaries, counts entries, allocates a Linux `posix_acl`, and converts little-endian ids/perms to kernel IDs. `bch2_acl_to_xattr()` performs the reverse conversion into a `KEY_TYPE_XATTR_INDEX_POSIX_ACL_*` xattr key.

`bch2_get_acl()` hashes and looks up the ACL xattr, converts it, caches it in the VFS inode, and returns NULL on ENOENT. Set paths reject default ACLs on non-directories, use hash set/delete for ACL xattrs, update mode for access ACLs, write inode ctime/mode changes, commit, update the in-memory inode, and refresh cached ACLs. `bch2_acl_chmod()` loads an access ACL, applies `__posix_acl_chmod()`, and updates the xattr.

## State And Side Effects

ACL changes modify xattr btrees and inode metadata. VFS-facing paths take `ei_update_lock`, use btree transactions, and update cached ACLs.

## Dependencies

Uses xattr hashing, inode operations, bcachefs transactions, VFS inode wrappers, Linux POSIX ACL APIs, and allocation helpers that can drop btree locks.

## Risks And Notes

Malformed on-disk ACLs return `-EINVAL`. Allocation failures use the custom `ENOMEM_acl` error. The `NO_BCACHEFS_FS` build excludes VFS functions and leaves transaction helpers stubbed in the header.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/acl.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/acl.h

## Purpose

Defines bcachefs on-disk ACL structures and declares ACL helper APIs.

## Main Interfaces

- `BCH_ACL_VERSION`.
- On-disk structs: `bch_acl_entry`, `bch_acl_entry_short`, `bch_acl_header`.
- `bch2_acl_to_text()`.
- Under `!NO_BCACHEFS_FS`: get/set/chmod ACL APIs.
- Under `NO_BCACHEFS_FS`: no-op stubs for transactional set/chmod helpers.

## Notes

The header separates portable ACL format handling from VFS-only behavior, allowing tools/userspace builds to compile without Linux VFS ACL operations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check.c

## Purpose

Implements the core bcachefs fsck metadata passes for root, inodes, dirents, xattrs, unreachable inodes, reflink padding migration, and online/offline fsck ioctls. It also provides shared snapshot-visibility and inode-walking helpers used by specialized check files.

## Main Interfaces

- Repair/message helpers: `bch2_dirent_inode_mismatch_msg()`, `bch2_reattach_inode()`, `bch2_fsck_update_backpointers()`.
- Snapshot helpers: `bch2_snapshots_seen_update()`, `bch2_key_visible_in_snapshot()`, `bch2_ref_visible()`, `bch2_ref_visible2()`.
- Inode walker: `bch2_walk_inode()`.
- Passes: `bch2_check_inodes()`, `bch2_check_unreachable_inodes()`, `bch2_check_dirents()`, `bch2_check_xattrs()`, `bch2_check_root()`, `bch2_fix_reflink_p()`.
- Fsck status/ioctl helpers: `bch2_fs_fsck_errcode()`, `bch2_ioctl_fsck_offline()`, `bch2_ioctl_fsck_online()`.

## Behavior

The file reconstructs or repairs filesystem namespace relationships. It can create `lost+found`, find or reconstruct subvolumes, reconstruct missing inodes from extents/dirents/xattrs, repair inode hash info, clear or update bad dirent backpointers, correct child-snapshot flags, handle unlinked inode/deleted-inode state, repair subvolume parent links, and remove bad dirents.

Snapshot visibility is tracked with `struct snapshots_seen`; this determines whether an older key remains visible after newer overwrites. `struct inode_walker` gathers all inode versions or visible inode versions for a given inode number, plus whiteouts/deletes, so dirent/xattr/extent passes can validate keys against the right snapshot-visible inode.

`bch2_check_inodes()` validates inode self-consistency, parent dirents, unlink state, directory sizes, child snapshot flags, subvolume references, and journal sequence bounds. `bch2_check_unreachable_inodes()` reattaches non-unlinked inodes without valid backpointers to `lost+found`. `bch2_check_dirents()` validates directory keys against directory inodes, hash correctness, target inodes/subvolumes, overwritten inode snapshots, and subdirectory nlink counts; it may require a second pass after hash repairs. `bch2_check_xattrs()` validates xattr ownership and hash placement. `bch2_check_root()` creates missing root subvolume/inode. `bch2_fix_reflink_p()` clears old reflink padding fields before the metadata-version fix.

## State And Side Effects

Fsck passes modify btrees transactionally: create inodes and subvolumes, insert/delete dirents, write inode updates, add whiteouts, update subvolume trees, and schedule transaction restarts after structural changes. Online fsck temporarily adjusts fsck options, stdio routing, and `BCH_FS_in_fsck`.

## Dependencies

Depends on btree transactions/updates/cache, dirent/namei/xattr/inode helpers, init recovery/progress/pass machinery, snapshots/subvolumes, VFS declarations, darrays, thread-with-stdio, ioctl structs, and user-copy/capability checks when chardev support is enabled.

## Risks And Notes

This file is deeply snapshot-aware. Most repairs must choose whether to update the current snapshot, an ancestor, a descendant, or insert whiteouts. Several repair paths return transaction restart errors intentionally after committing changes. Online fsck is constrained to passes marked online-capable; offline fsck opens devices read-only through a stdio thread.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check.h

## Purpose

Declares fsck/check pass APIs and shared data structures for snapshot-aware metadata walking.

## Main Interfaces

- `struct snapshots_seen`: current position plus snapshot ID list for overwrites.
- `struct inode_walker_entry`: unpacked inode/whiteout plus accumulated counts.
- `struct inode_walker`: cached inode versions/deletes for one inode number.
- RAII classes for snapshots and inode walkers.
- Shared helper declarations for snapshot visibility, inode walking, reattach, backpointer updates, key-has-inode validation, all check passes, fsck error-code translation, and fsck ioctls.

## Notes

The header exposes exactly the shared machinery needed by `check.c`, `check_extents.c`, `check_dir_structure.c`, and `check_nlinks.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check_dir_structure.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check_dir_structure.c

## Purpose

Implements fsck passes for subvolume path structure and directory-loop detection.

## Main Interfaces

- `bch2_check_subvolume_structure(struct bch_fs *c)`.
- `bch2_check_directory_structure(struct bch_fs *c)`.

## Behavior

Subvolume checking walks each subvolume’s `fs_path_parent` chain back to `BCACHEFS_ROOT_SUBVOL`, detects missing parents and loops, and repairs by removing the existing backpointer/dirent and reattaching the subvolume root through `bch2_reattach_inode()`.

Directory structure checking walks parent backpointers from each live directory toward a subvolume root. It detects missing parent dirents, parent lookup failures, and loops. On loops, it removes the offending backpointer dirent and reattaches the inode. It also repairs `bi_depth` along the traversed path when parent depths are inconsistent.

## State And Side Effects

Can delete dirents, reattach inodes under `lost+found`, and rewrite inode `bi_depth` values. Uses btree transactions with commit/restart handling.

## Dependencies

Uses `fs/check.h`, `fs/namei.h`, progress reporting, dirent lookup/removal, subvolume lookup, and inode find/write helpers.

## Risks And Notes

This pass assumes previous inode/dirent checks have already repaired basic backpointer validity. It focuses on graph-level correctness: no unreachable subvolumes and no directory cycles.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check_dir_structure.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check_extents.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check_extents.c

## Purpose

Implements fsck passes for extent ownership, extent overlap, inode sector counts, stale pointer removal, encoded extent size diagnostics, and indirect reflink extents.

## Main Interfaces

- `bch2_check_extents(struct bch_fs *c)`.
- `bch2_check_indirect_extents(struct bch_fs *c)`.

## Behavior

The extent pass walks `BTREE_ID_extents` across all snapshots, uses `inode_walker` to validate that each extent belongs to a visible regular-file or symlink inode, and accumulates allocated sectors to check `bi_sectors`.

`extent_ends` tracks the latest visible extent ends per snapshot. `check_overlapping_extents()` compares each extent against visible prior ends and, when overlapping extents are found, chooses which extent to overwrite or convert from `extent_whiteout` to `whiteout`. It updates snapshot visibility state so scanning can continue after repairs.

The pass also detects extents past inode size and punches them out, warns about encoded extents larger than the current maximum, and drops stale pointers. After each commit, visible allocation extents contribute to inode sector counts. At inode boundaries, `check_i_sectors()` recomputes and repairs inode sector totals unless marked dirty.

The indirect extent pass walks `BTREE_ID_reflink`, checks encoded size, and drops stale pointers.

## State And Side Effects

Can overwrite/delete extents, punch ranges, update inode `bi_sectors`, drop stale extent pointers, consume disk reservations, and trigger transaction restarts.

## Dependencies

Uses bucket/extent/io helpers, inode walker and snapshot visibility from `check.h`, name/path formatting, progress reporting, disk reservations, and btree extent update APIs.

## Risks And Notes

Overlap repair is snapshot-sensitive and must distinguish same-snapshot overwrite, ancestor/descendant visibility, and extent whiteouts. The code notes older non-nested restart behavior in sector counting, making restart boundaries important.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check_nlinks.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check_nlinks.c

## Purpose

Repairs hardlink counts for non-directory inodes.

## Main Interfaces

- `bch2_check_nlinks(struct bch_fs *c)`.

## Behavior

The pass builds an in-memory `nlink_table` for inodes that are non-directories and have nonzero `bi_nlink`. It then walks all dirents and increments link counts for visible dirents pointing to in-range non-directory targets, using snapshot visibility rules from `bch2_ref_visible()`. Finally it walks inode keys again and updates inode nlink fields when the stored count differs from the counted value, or when unlinked state conflicts with nonzero nlink.

To bound memory, it processes inode ranges. If table allocation fails while collecting hardlink candidates, it records the next range boundary and finishes the current range before continuing.

## State And Side Effects

Allocates a growable `kv*` table, sorts it by inode number, scans dirents, and transactionally rewrites inode nlink fields.

## Dependencies

Uses `check.h`, Linux `bsearch`, btree iteration/commit helpers, inode unpack/write helpers, and snapshot visibility tracking.

## Notes

Directories are excluded because directory nlink/subdirectory counts are handled by the dirent/directory structure checks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/check_nlinks.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/dirent.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/dirent.c

## Purpose

Implements bcachefs directory entry hashing, validation, formatting, creation, lookup, rename, readdir, casefold support, and fsck dirent removal.

## Main Interfaces

- Hash descriptor `bch2_dirent_hash_desc`.
- Casefold/name helpers: `bch2_casefold()`, `bch2_dirent_get_name()`, `bch2_dirent_init_name()`.
- Validation/printing: `bch2_dirent_validate()`, `bch2_dirent_to_text()`.
- Creation: `bch2_dirent_create_key()`, `bch2_dirent_create_snapshot()`, `bch2_dirent_create()`.
- Target/rename/lookup: `bch2_dirent_read_target()`, `bch2_dirent_rename()`, `bch2_dirent_lookup_snapshot()`, `bch2_dirent_lookup_trans()`, `bch2_dirent_lookup()`.
- Directory operations: `bch2_empty_dir_snapshot()`, `bch2_empty_dir_trans()`, `bch2_readdir()`.
- Initialization/debug: `bch2_dirent_init()`, `bch2_filldir64_specialization_to_text()`.
- Fsck helper: `bch2_fsck_remove_dirent()`.

## Behavior

Dirents are indexed by a 64-bit string hash stored in key offset, with linear probing and whiteouts for collision deletion. The hash descriptor supplies key/bkey hash, comparisons, and a subvolume-aware visibility filter.

Validation rejects empty names, oversized names, embedded NULs, dot/dotdot, slash, self-pointing non-subvolume dirents, and invalid casefold blocks. Name initialization stores either a plain name or a packed original + casefolded name block.

Creation builds a max-sized dirent key, fills target fields for regular targets or `DT_SUBVOL`, initializes names, then inserts through the string-hash layer. Rename handles normal, overwrite, and exchange modes; it preserves hash-table correctness around collisions, emits whiteouts when needed, and specially deletes subvolume dirents across snapshots because subvolume dirents are not versioned like ordinary dirents.

Lookup optionally casefolds the input name, performs hash lookup in current or specified snapshot, and resolves `DT_SUBVOL` targets through the subvolume table. Readdir walks visible dirents in a subvolume, validates/repairs hash placement, resolves targets, and emits entries.

## Kernel Fast Path

In kernel builds, the file optionally specializes getdents64 emission. It mirrors the private `getdents_callback64` layout when build-time verification succeeded, resolves the static kernel `filldir64` symbol with a kprobe, handles x86 IBT address adjustment, faults in the user buffer, and emits dirents under btree locks using `pagefault_disable()` and unsafe user copies. If unavailable or faulting/buffer-full, it falls back to `bch2_dir_emit_slow()`, which drops transaction locks before `dir_emit()`.

Userspace/non-kernel builds always use the slow path and report the fast path unavailable.

## State And Side Effects

Mutates dirent btrees, may insert hash whiteouts, may delete subvolume dirents from old snapshots, and may repair bad hash entries during readdir through `bch2_str_hash_check_key()`. Kernel initialization sets the global `filldir64_sym`.

## Dependencies

Uses btree key buffers/methods/update, extents, string hash, subvolume lookup, Unicode casefolding when enabled, Linux dcache/readdir/uaccess/kprobes in kernel builds, and generated getdents layout data.

## Risks And Notes

Hash collision handling is subtle. Rename must preserve probe chains even while moving/deleting keys. The getdents fast path intentionally depends on verified private kernel layout; if verification or symbol lookup fails, it silently degrades to the safe slow path.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/dirent.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/dirent.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/dirent.h

## Purpose

Declares dirent hash, validation, creation, lookup, rename, readdir, empty-directory, initialization, and fsck removal APIs.

## Main Interfaces

- `bch2_bkey_ops_dirent` defines key validation, text formatting, and minimum value size.
- Casefold helper `bch2_maybe_casefold()` returns original name when no casefold encoding is configured or calls `bch2_casefold()`.
- `dirent_val_u64s()` computes packed value size for plain or casefolded names.
- `dirent_get_by_pos()` fetches a typed dirent at an exact btree position.
- `vfs_d_type()` maps `DT_SUBVOL` to `DT_DIR` for userspace.
- `enum bch_rename_mode`: normal rename, overwrite, exchange.

## Dependencies

Includes `str_hash.h` and forward-declares VFS and bcachefs structs used by the implementation.

## Notes

The header exposes both core metadata operations and the readdir/sysfs-adjacent filldir specialization status hook.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/dirent_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/dirent_format.h

## Purpose

Defines the on-disk/in-btree dirent value format.

## Format

`struct bch_dirent` contains:

- Base `struct bch_val`.
- Target union:
  - `d_inum` for ordinary entries.
  - `d_child_subvol` and `d_parent_subvol` for `DT_SUBVOL`.
- Bitfield byte with `d_type`, unused bits, and `d_casefold`.
- Name payload:
  - Plain flexible `d_name[]`, or
  - Packed casefold block with original length, casefolded length, and concatenated names.

Constants:

- `DT_SUBVOL = 16`.
- `BCH_DT_MAX = 17`.
- `BCH_NAME_MAX = 512`.

## Notes

The comments explain that dirents and xattrs are indexed by 64-bit string hashes in key offsets with linear probing. Deletions may require whiteouts to preserve probe chains and stable readdir cookies.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/dirent_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/inode.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/inode.c

## Purpose

Implements bcachefs inode packing/unpacking, validation, lookup, write, creation, deletion, nlink mutation, inode option extraction, casefold enablement, deleted-inode cleanup, inode triggers, and legacy inode-generation cleanup.

## Main Interfaces

- Pack/unpack: `bch2_inode_pack()`, `bch2_inode_unpack()`, `bch2_inode_to_v3()`.
- Lookup/find: `__bch2_inode_peek_snapshot()`, `__bch2_inode_peek()`, `bch2_inode_find_by_inum_snapshot()`, `bch2_inode_find_by_inum_snapshot2()`, `__bch2_inode_find_by_inum_trans()`, `bch2_inode_find_by_inum()`, `bch2_inode_find_oldest_snapshot()`.
- Write: `bch2_inode_write_flags()`, `__bch2_fsck_write_inode()`, `bch2_fsck_write_inode()`.
- Validate/text: inode v1/v2/v3 validators and text formatters; inode generation and alloc cursor validators/formatters.
- Snapshot/trigger: `__bch2_inode_has_child_snapshots()`, `bch2_trigger_inode()`.
- Lifecycle: `bch2_inode_init_early()`, `bch2_inode_init_late()`, `bch2_inode_init()`, `bch2_inode_create()`, `bch2_inode_rm()`, `bch2_inode_rm_snapshot()`, `bch2_delete_dead_inodes()`, `bch2_kill_i_generation_keys()`.
- Link/options: `bch2_inode_nlink_inc()`, `bch2_inode_nlink_dec()`, `bch2_inode_opts_to_opts()`, `bch2_inode_opts_get_inode()`, `bch2_inode_set_casefold()`.

## Behavior

The file supports three inode formats. v3 is the fast path: fixed fields store journal sequence, hash seed, flags, sectors, size, version, and mode; optional fields are varint-packed and truncated after the last nonzero field. v1/v2 unpack through slow paths. Decode errors zero the failed and later fields, count `inode_unpack_error`, and schedule explicit recovery passes when damaged fields affect nlinks, subvolumes, parent subvolumes, or casefolded dirent hashing.

Lookup helpers resolve subvolume snapshots and fetch cached inode keys from `BTREE_ID_inodes`. Write helpers repack unpacked inodes into v3 and update or insert through btree transactions. Validators enforce inode key positions, blockdev-reserved ranges, valid string-hash types, and valid v3 field-start offsets.

`bch2_trigger_inode()` maintains side effects during transactional/gc updates: journal sequence assignment on insert, inode count accounting, deleted-inodes btree bits for unlinked inodes, parent child-snapshot flags, and clearing child flags when a snapshot-local inode is created.

Inode creation obtains a logged inode allocation cursor, supports 32-bit and sharded inode-number ranges, scans for an empty slot or reusable inode-generation key, assigns generation, advances cursor, and positions the caller’s iterator. Inode removal checks whether deletion is valid, deletes extent/dirent/xattr keys, removes the inode, and recursively removes unlinked ancestor snapshot inodes when safe.

Deleted-inode cleanup flushes the write buffer, walks `BTREE_ID_deleted_inodes`, validates each entry, removes bogus deleted-inode bits, and deletes dead inode snapshots while avoiding spin-prone restart behavior.

Inode option helpers convert inode-local option overrides to mount-style option structs, fallback unknown future compression/checksum values to filesystem defaults for new writes, and propagate change cookies. Casefold enablement requires Unicode/casefold support, a directory, an empty directory, and the incompat feature.

## State And Side Effects

This file mutates inode, extent, dirent, xattr, logged-ops, deleted-inodes, and accounting btrees. It also updates filesystem error counters and may trigger recovery passes on unpack failures. Link count helpers manipulate `BCH_INODE_unlinked` semantics rather than only numeric nlinks.

## Dependencies

Depends on accounting, buckets, key cache/write buffer, bkey methods/update, compression/extents/extent update, dirent/namei/str_hash, VFS wrappers, init error/pass machinery, snapshots/subvolumes, varint encoding, random bytes, and unaligned helpers.

## Risks And Notes

Inode format compatibility is central here. Decode error recovery must leave a defined unpacked struct while scheduling enough fsck passes to reconstruct derived state. Snapshot parent/child flag maintenance is delicate because inode creation/deletion in one snapshot affects ancestor visibility and fsck semantics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/inode.c -->