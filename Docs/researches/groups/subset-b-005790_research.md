# Research Group subset-b-005790

This grouped report covers XFS online scrub and repair files from `sources/distributed-fs/ceph-client/fs/xfs/scrub/`. Sections are delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.c

## Purpose
`nlinks.c` implements live filesystem-wide inode link count scrub. Link counts are treated as derived summary metadata: the scrubber builds shadow counts by walking every inode and every directory entry, applies live directory updates via notifier hooks, and compares the resulting observations against `i_nlink` and directory parent/backreference invariants.

## Important APIs, Types, And Functions
The public setup and entry points are `xchk_setup_nlinks` and `xchk_nlinks`. They allocate `struct xchk_nlink_ctrs`, enable directory-entry fsgates, optionally prepare repair state through `xrep_setup_nlinks`, and call `xchk_setup_fs`.

The main phases are `xchk_nlinks_setup_scan`, `xchk_nlinks_collect`, and `xchk_nlinks_compare`. Collection uses `xchk_nlinks_collect_metafiles`, `xchk_nlinks_collect_dir`, `xchk_nlinks_collect_file`, `xchk_nlinks_collect_dirent`, and `xchk_nlinks_collect_pptr`. Comparison uses `xchk_nlinks_compare_inode`, `xchk_nlinks_compare_inum`, and `xchk_nlinks_comparison_read`.

`xchk_nlinks_update_incore` stores `struct xchk_nlink` records in an `xfarray`, using sparse loads and stores keyed by inode number. `careful_add` clamps counters to `U32_MAX` so overlarge observations become detectable without overflowing. `xchk_nlinks_live_update` shadows concurrent directory changes through `xfs_dir_hook`.

## Control Flow
Setup creates an `xfarray` large enough for the highest possible inode, initializes an iscan with retry behavior, installs the dirent hook, and registers deferred cleanup. Collection first accounts superblock-rooted metadata inodes, then cancels the transaction and uses an empty transaction while iterating all allocated inodes. Directories are locked with IOLOCK plus an ILOCK mode capable of reading data and parent-pointer forks, walked through `xchk_dir_walk`, and, on parent-pointer filesystems, xattr-walked for `XFS_ATTR_PARENT` records. Non-directories are only marked visited.

Comparison restarts with an empty transaction, walks allocated inodes through a second iscan, and compares observed totals to live inode state. A second pass walks unscanned shadow records to catch observations for inodes that could not be obtained, using AGI protection to distinguish absent inodes from races.

## State And Persistence Behavior
All observation state is in memory: `xfarray` records, two `xchk_iscan` cursors, a mutex, and the directory hook. Persistent state is not changed by scrub. The file sets scrub state flags such as corrupt, warning, xref corrupt, and incomplete. Cleanup aborts the iscan, removes hooks, destroys the array and mutex, and leaves repair able to reuse the shadow data only if the scrub phase completed enough to keep `sc->buf_cleanup` active.

## Dependencies And Integration Points
This file depends on inode scanning, sparse arrays, directory walking, parent-pointer xattr walking, temporary-file exclusion, tracepoints, scrub transactions, and orphanage/nlinks repair headers. It integrates with `scrub.c` through `xchk_nlinks`, with `nlinks_repair.c` by preserving collected data for repair, and with directory update hooks to maintain consistency on a live filesystem.

## Risks And Edge Cases
The major risk is false corruption from incomplete collection; the code aggressively sets `INCOMPLETE` when collection errors or hooks abort. Parent-pointer filesystems count backreferences from xattrs instead of dotdot entries. Filesystems without filetype information use backrefs as a fallback for directory child counts. Zapped directories or parent-pointer forks return busy/incomplete because repair of lower-level structures must run first. Missing or invalid inode numbers, malformed names, excessive link totals, orphaned linked inodes, and observations for absent inodes are all flagged.

## Test Signals
Useful tests include live rename/link/unlink churn during nlink scrub, parent-pointer and non-parent-pointer filesystems, ftype=0 behavior, corrupted `.` and `..` entries, zapped directory or attr forks, metadata inode accounting, link counts above `XFS_MAXLINK`, and races where an observed inode cannot be iget during comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.h

## Purpose
`nlinks.h` defines the shared in-core data model for live link-count scrub and repair. It is the contract between `nlinks.c` and `nlinks_repair.c`.

## Important APIs, Types, And Functions
`struct xchk_nlink_ctrs` owns the scrub context, shadow `xfarray`, mutex, collection and comparison iscans, directory update hook, orphanage adoption request, and reusable name buffer. `struct xchk_nlink` stores observed parent links, child-directory backreferences, child forward links/dot entries, and record flags.

Flags are `XCHK_NLINK_WRITTEN`, `XCHK_NLINK_COMPARE_SCANNED`, and `XREP_NLINK_DIRTY`. `xchk_nlink_total` computes the effective VFS link count from observed parent links plus directory dot accounting plus child forward links.

## Control Flow
The header has no standalone control flow. Its structures are initialized by setup in `nlinks.c`, filled during filesystem scans and live hook callbacks, read during comparison, and reused by repair to update inode core state and unlinked-list membership.

## State And Persistence Behavior
All state is volatile scrub state. `xchk_nlink_total` deliberately uses a 64-bit accumulator so callers can detect values above XFS link-count limits before updating or reporting corruption.

## Dependencies And Integration Points
It depends on `struct xfs_scrub`, `xfarray`, `xchk_iscan`, `xfs_dir_hook`, and orphanage adoption types. Repair depends on this header for the exact counter semantics; changing the meaning of `parents`, `backrefs`, or `children` would affect both detection and repair.

## Risks And Edge Cases
The subtle behavior is directory accounting: a linked directory contributes one dot link in `xchk_nlink_total`, while `children` tracks forward links from the directory to children and dot-style accounting. Root and metadata-root behavior is handled by callers, not the helper.

## Test Signals
Tests should confirm that directory, non-directory, unlinked directory, root directory, and overflow cases all produce expected totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks_repair.c

## Purpose
`nlinks_repair.c` repairs inode link counts using the shadow data collected by live nlink scrub. It also reconciles unlinked-list membership and can reattach orphaned linked files to `/lost+found`.

## Important APIs, Types, And Functions
`xrep_setup_nlinks` prepares the orphanage if repair might need adoption. `xrep_nlinks` is the public repair entry point. `xrep_nlinks_repair_inode` is the core per-inode repair routine. `xrep_nlinks_is_orphaned` decides when a linked inode with no observed parents should be adopted. `xrep_nlinks_iunlink_remove` removes an inode from the AG unlinked list.

## Control Flow
Repair requires filetype support because it must distinguish subdirectory links accurately. It scans allocated inodes with `xchk_iscan`, cancels the ordinary scrub transaction before each inode, then repairs with either an adoption-capable transaction or a simple link-count transaction. If orphanage adoption is possible, the code takes IOLOCKs for the orphanage and target, allocates adoption resources, computes a unique orphanage name, moves the inode, and reloads the shadow counts because the move itself updates observations through hooks.

After adoption decisions, the routine removes a linked inode from the unlinked list or adds an unlinked inode to it. It sets `i_nlink` to the observed total capped at `XFS_NLINK_PINNED`, logs the inode, commits dirty transactions, and releases all locks.

## State And Persistence Behavior
Persistent changes include directory entries in `/lost+found`, parent pointers from adoption, unlinked-list updates, and inode core link count updates. The repair relies on the scrub phase keeping live hook data active so the shadow counts reflect repairs and concurrent changes. Transactions are carefully shaped around lock order and resource reservations.

## Dependencies And Integration Points
It depends on `nlinks.h`, orphanage adoption helpers, unlinked-list APIs, inode scanning, tracepoints, and XFS transaction helpers. It is invoked by the scrub framework after `xchk_nlinks` reports fixable corruption.

## Risks And Edge Cases
Repair refuses ftype-less filesystems. Non-directories with observed child directory links are considered unfixable in this path. Adoption can be skipped if orphanage setup or reservation fails, in which case simple nlink repair is still attempted. Hook aborts cancel repair to avoid applying incomplete observations. The code must maintain IOLOCK-before-transaction and ILOCK transaction join order.

## Test Signals
Cover orphaned but linked files, orphaned directories, stale unlinked-list membership, zero-link files missing from unlinked lists, adoption name collisions, repair during live directory churn, and failure to allocate orphanage resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/off_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/off_bitmap.h

## Purpose
`off_bitmap.h` provides a small type-safe wrapper around `xbitmap64` for file-offset ranges expressed as `xfs_fileoff_t` and `xfs_filblks_t`.

## Important APIs, Types, And Functions
`struct xoff_bitmap` contains a single `xbitmap64`. Inline helpers are `xoff_bitmap_init`, `xoff_bitmap_destroy`, `xoff_bitmap_set`, and `xoff_bitmap_walk`.

## Control Flow
Callers initialize the wrapper, add file-offset ranges, walk the bitmap with an `xbitmap64_walk_fn`, and destroy it. All real range coalescing and iteration behavior is delegated to `xbitmap64`.

## State And Persistence Behavior
The state is entirely in memory and exists only for scrub or repair bookkeeping. No filesystem metadata is changed directly.

## Dependencies And Integration Points
It depends on `xbitmap64` and XFS file offset types. It is intended for scrub code that wants stronger type signaling than raw 64-bit bitmap helpers.

## Risks And Edge Cases
The wrapper does not add validation beyond the underlying bitmap. Incorrect unit conversion by callers remains possible if callers pass byte offsets instead of file block offsets.

## Test Signals
Tests should exercise empty bitmaps, adjacent range coalescing, large offsets, and callback ordering through `xoff_bitmap_walk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/off_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.c

## Purpose
`orphanage.c` implements online repair support for `/lost+found`. When directory tree damage disconnects files, repair can create or reuse the orphanage, make it root-owned, and adopt orphaned files by adding directory entries, updating dotdot for directories, adding parent pointers, and invalidating stale dentries.

## Important APIs, Types, And Functions
`xrep_orphanage_create` finds or creates `/lost+found`, validates it is a directory, grabs an inode reference, and calls `xrep_chown_orphanage`. Lock helpers are `xrep_orphanage_ilock`, `xrep_orphanage_ilock_nowait`, `xrep_orphanage_iunlock`, `xrep_orphanage_iolock_two`, and `xrep_orphanage_rele`.

Adoption functions are `xrep_adoption_trans_alloc`, `xrep_adoption_compute_name`, `xrep_adoption_move`, and `xrep_adoption_trans_roll`. Internal helpers check and invalidate dcache state and compute attr-fork space for parent-pointer filesystems.

## Control Flow
Creation uses VFS dentries from the root inode, `start_creating_noperm`, and `vfs_mkdir` with mode `0750` if missing. It rejects non-directories and readonly/shutdown cases. Ownership repair allocates root dquots, creates an inode-change transaction, clears suid/sgid/sticky and realtime inheritance bits, updates uid/gid/project, logs the inode, and commits.

Adoption starts with both target and orphanage IOLOCKs. It computes worst-case block reservations for adding the orphanage entry, changing child dotdot, and adding an attr fork if parent pointers require one. It joins both inodes, reserves quota with repair override, chooses a unique numeric name, verifies no positive dcache entry conflicts, creates the name, updates orphanage and child link counts as requested, replaces dotdot for directories, adds a parent pointer when enabled, fires a directory update hook, invalidates dentries, and rolls the transaction clean.

## State And Persistence Behavior
Persistent effects include creating `/lost+found`, changing its ownership and mode bits, adding orphanage directory entries, updating directory dotdot entries, parent-pointer xattrs, link counts, timestamps, quota reservations, and logged inode state. Dcache invalidation is volatile but necessary so VFS lookup state matches repaired metadata.

## Dependencies And Integration Points
The file integrates with VFS dentry helpers, XFS quota, transactions, directory operations, parent-pointer APIs, scrub repair context, tracepoints, and callers in nlink and parent repair. It relies on `sc->orphanage` and `sc->orphanage_ilock_flags` as shared repair context.

## Risks And Edge Cases
Readonly mounts continue without orphanage. Missing root dentry, non-directory root alias, non-directory `/lost+found`, name collisions beyond 10,000 variants, dcache contradictions, attr-fork allocation failure, and quota reservation failure all abort adoption. Lock ordering is critical because scrub may already hold transactions and cannot block on IOLOCK in ordinary order.

## Test Signals
Tests should cover creating `/lost+found`, fixing ownership/project/realtime flags, adopting files and directories, parent-pointer filesystems, dcache aliases, name collisions, readonly mounts, no-space cases, and concurrent lookup/rename during adoption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.h

## Purpose
`orphanage.h` declares the repair-facing orphanage and adoption interface and provides stubs when online repair is disabled.

## Important APIs, Types, And Functions
With `CONFIG_XFS_ONLINE_REPAIR`, it declares orphanage creation, lock helpers, reference release, adoption transaction allocation, name computation, move, and transaction roll functions. `xrep_orphanage_try_create` wraps creation and suppresses nonfatal orphanage unavailability errors. `struct xrep_adoption` carries the scrub context, chosen name, parent-pointer args, block reservations, and whether the child link count should be bumped.

## Control Flow
The inline `xrep_orphanage_try_create` asserts repair mode, calls `xrep_orphanage_create`, and treats `-ENOENT`, `-ENOTDIR`, and `-ENOSPC` as nonfatal because callers can still perform repairs that do not require adoption.

## State And Persistence Behavior
The header itself has no persistence. The adoption object is per-operation mutable state consumed by `orphanage.c`.

## Dependencies And Integration Points
It depends on scrub context, XFS parent args, and repair configuration. Nlink and parent repairs use this API to reconnect disconnected files.

## Risks And Edge Cases
The stub `struct xrep_adoption` is empty when online repair is disabled, so callers must be behind repair configuration guards. Nonfatal orphanage creation failures intentionally degrade repair capability rather than failing all setup.

## Test Signals
Compile coverage should include online repair enabled and disabled. Runtime tests should confirm callers handle `xrep_orphanage_can_adopt` false after suppressed setup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/parent.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/parent.c

## Purpose
`parent.c` validates parent relationships. Without parent pointers, it verifies a directory's `..` entry and the alleged parent directory's forward link. With parent pointers, it validates each parent-pointer xattr against a directory entry, checks dotdot consistency for directories, and compares parent-pointer counts with link counts.

## Important APIs, Types, And Functions
`xchk_setup_parent` and `xchk_parent` are public. Traditional validation uses `xchk_parent_validate`, `xchk_parent_actor`, and `xchk_parent_ilock_dir`. Parent-pointer validation uses `struct xchk_pptr`, `struct xchk_pptrs`, `xchk_parent_scan_attr`, `xchk_parent_dirent`, `xchk_parent_iget`, `xchk_parent_finish_slow_pptrs`, `xchk_parent_pptr_and_dotdot`, and `xchk_parent_count_pptrs`. `xchk_pptr_looks_zapped` identifies attr forks that repair intentionally cleared and that should defer parent-pointer checks.

## Control Flow
Setup optionally prepares parent repair state, then sets up inode contents scrub. On parent-pointer filesystems, scrub allocates scratch `xfarray` and `xfblob` storage for deferred parent pointers. It walks the target's xattrs; each parent pointer is decoded, checked for self-reference, and resolved to a parent directory. If locks can be acquired immediately, it looks up the named child in the parent. If not, it stores the record and name for a slow pass that can cycle locks and revalidate the xattr.

For directories, it also looks up `..` and ensures it matches one of the parent pointers unless the directory is a root or currently unlinked. It then counts parent pointers and compares them to link-count expectations. Without parent pointers, the code loops on `..` lookup and parent validation, retrying when lock ordering required revalidation.

## State And Persistence Behavior
Scrub is read-only. It records only transient deferred parent-pointer names and records in xfile-backed structures, sets scrub corruption/xref/incomplete flags, and releases all scratch state at exit.

## Dependencies And Integration Points
It depends on directory walking and lookup helpers, xattr walking, parent-pointer decoding, xfarray/xfblob, temporary-file detection, and repair setup in `parent_repair.c`. It integrates with directory and xattr scrub health by deferring if those structures look zapped.

## Risks And Edge Cases
Key edge cases include root and metadata root self-parenting, unlinked directories with meaningless dotdot, parent inodes that are missing or not directories, generation mismatches, metadata/non-metadata tree crossing, lock contention requiring slow revalidation, hardlinked non-directories, and superblock-rooted metadata inodes without ordinary parent xattrs.

## Test Signals
Tests should cover corrupt dotdot, parent pointer with missing forward dirent, wrong parent generation, multiple parent pointers on directories, non-directory hardlinks, zapped attr fork deferral, VFS lock contention, and parent pointers crossing metadata tree boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/parent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/parent_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/parent_repair.c

## Purpose
`parent_repair.c` repairs parent relationships. On filesystems without parent-pointer xattrs, it finds the correct directory parent and resets `..`. On parent-pointer filesystems, it rebuilds the target file's parent-pointer xattr structure from all directory entries in the filesystem, preserves non-parent xattrs, atomically exchanges attr forks, adopts parentless files when possible, and fixes nondirectory link counts.

## Important APIs, Types, And Functions
`xrep_setup_parent` creates `struct xrep_parent`, a temporary file, and orphanage context. `xrep_parent` is the public repair entry. The main state object owns parent-pointer staging arrays/blobs, non-parent xattr staging arrays/blobs, temp exchange state, findparent/iscan/hook state, adoption state, name buffers, and counters.

Important routines include `xrep_parent_find_dotdot`, `xrep_parent_scan_dirtree`, `xrep_parent_live_update`, `xrep_parent_replay_updates`, `xrep_parent_reset_dotdot`, `xrep_parent_move_to_orphanage`, `xrep_parent_copy_xattrs`, `xrep_parent_rebuild_pptrs`, `xrep_parent_rebuild_tree`, `xrep_parent_set_nondir_nlink`, and `xrep_parent_setup_scan`.

## Control Flow
Setup enables dirent gates, creates a regular tempfile, and tries to attach orphanage. Without parent pointers, repair uses dcache and filesystem scanning through findparent to choose a parent, then resets dotdot if needed.

With parent pointers, repair allocates buffers and xfile staging, starts an inode scan with a live directory update hook, drops heavy locks and scans all directories for entries pointing to the target. Matching dirents are converted into parent-pointer add records. Live add/remove updates for already scanned directories are stashed too. Staged parent-pointer updates are periodically replayed into the tempfile to cap memory use.

After scanning, it copies all non-parent xattrs from the target to the tempfile, flushing staged xattrs as needed. If parent-pointer updates race with opportunistic flushing, it restarts the copy with stricter locking. It ensures both files have attr forks, allocates an exchange transaction, replays any final parent-pointer updates, swaps attr fork mappings with `xrep_xattr_swap`, resets the tempfile fork, and rolls to a clean transaction. It then discovers whether a parent exists, moves parentless files to the orphanage if allowed, resets dotdot for directories, and updates nondirectory nlink/unlinked-list state from parent-pointer counts.

## State And Persistence Behavior
Persistent effects include replaced parent-pointer attr forks, preserved non-parent xattrs, updated dotdot entries, orphanage adoption, unlinked-list changes, and nondirectory link-count changes. The attr fork replacement is atomic through the temp-exchange path and requires rmapbt plus exchange-range support. Staged state lives in `xfarray`/`xfblob` until flushed or teardown.

## Dependencies And Integration Points
This file integrates with findparent scanning, readdir, tempfile and tempexch helpers, orphanage adoption, xattr repair, parent-pointer APIs, directory update hooks, quota/unlinked-list APIs, and `reap.c` indirectly through xattr fork exchange cleanup. `xrep_parent` is wired as the repair handler for parent scrub.

## Risks And Edge Cases
The most important risks are live rename races, xattr copy races, attr fork absence, memory growth from many hardlinks or xattrs, parentless files when no orphanage is available, metadata-rooted files that intentionally lack parents, and transaction/lock ordering around IOLOCK, ILOCK, tempfile locks, and orphanage locks. Parent-pointer repair is unsupported without rmapbt and exchange-range.

## Test Signals
Tests should include parent-pointer rebuild during concurrent renames, files with many hardlinks, millions of xattrs or remote xattr values, missing attr forks, stale parent pointers, parentless files requiring adoption, nondirectory link count repair, directory dotdot reset, unsupported feature combinations, and interrupted repair before/after CHANGES are committed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/parent_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.c

## Purpose
`quota.c` scrubs the quota metadata file and individual dquot records for one quota type. It checks structural backing mappings, limit/timer consistency, and resource counts that are obviously impossible.

## Important APIs, Types, And Functions
`xchk_quota_to_dqtype` maps scrub types to user, group, or project dquot types. `xchk_setup_quota` validates quota availability, installs the quota inode as the live inode, and locks it. `xchk_quota` drives the full check. `struct xchk_quota_info` tracks the scrub context and monotonic dquot ids. Helpers include `xchk_quota_data_fork`, `xchk_quota_item`, `xchk_quota_item_bmap`, and `xchk_quota_item_timer`.

## Control Flow
Setup rejects disabled quotas, invalid scrub types, and quota types not enabled. Scrub first runs metadata inode fork checks and then walks quota inode extents to reject unwritten, delalloc, or out-of-range mappings. It drops the quota inode ILOCK before using normal dquot iteration. Each dquot is locked after the quota inode ILOCK is acquired in the quota locking order; its file offset and cached disk address are cross-checked against `xfs_bmapi_read`.

The item check validates monotonic id iteration, hard limits relative to filesystem size, soft limit ordering, resource counts against total data/realtime/inode capacity, hard-limit exceedance warnings, and timer presence when usage exceeds soft or hard limits.

## State And Persistence Behavior
Scrub is read-only. It sets corruption or warning flags but does not update dquots. It uses dquot locks and quota inode locks for consistency during checks.

## Dependencies And Integration Points
The file depends on XFS quota manager iteration, dquot locking, bmap reads, metadata inode fork scrub, and scrub setup. It shares the dqtype helper with quota repair.

## Risks And Edge Cases
Reflink filesystems can legitimately show block counts above physical space due to shared accounting, so those become warnings instead of corruption. Root dquot id zero bypasses hard-limit exceedance review. Incorrect lock ordering can deadlock with quota operations, which is why the code explicitly uses ILOCK then dquot lock.

## Test Signals
Tests should cover quota off, one quota type off, unwritten quota file extents, out-of-range extents, dquot block holes, bad cached block address, soft greater than hard, missing or stale timers, reflink over-accounting, and non-monotonic dquot iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.h

## Purpose
`quota.h` exposes the shared quota scrub helper needed by quota repair.

## Important APIs, Types, And Functions
The file declares `xchk_quota_to_dqtype(struct xfs_scrub *sc)`, which converts scrub operation types into `xfs_dqtype_t`.

## Control Flow
There is no internal control flow. Callers use the helper before quota scrub or repair to choose user, group, or project quota metadata.

## State And Persistence Behavior
No state is stored or persisted.

## Dependencies And Integration Points
It depends on `struct xfs_scrub` and quota type definitions. `quota.c` implements the helper, and `quota_repair.c` reuses it.

## Risks And Edge Cases
Callers must handle a zero return as invalid scrub type. There is no compile-time enforcement that only quota scrub types call it.

## Test Signals
Basic coverage should verify all three quota scrub types and the invalid default case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quota_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/quota_repair.c

## Purpose
`quota_repair.c` repairs quota file mappings, verifier-visible dquot block damage, and fixable dquot field inconsistencies. When counters are suspicious, it schedules a full quotacheck.

## Important APIs, Types, And Functions
`xrep_quota` is the public repair entry. `struct xrep_quota_info` tracks whether a later quotacheck is required. Mapping and block repair is handled by `xrep_quota_data_fork`, `xrep_quota_block`, `xrep_quota_item_bmap`, and `xrep_quota_item_fill_bmap_hole`. Dquot field repair is handled by `xrep_quota_item`, `xrep_quota_item_timer`, `xrep_quota_fix_timer`, and `xrep_quota_problems`.

## Control Flow
Repair retakes the quota inode ILOCK, repairs generic metadata inode forks, converts unwritten quota extents, truncates mappings beyond the maximum dquot id, cancels CoW reservations, clears reflink state, and rewrites bad dquot blocks. Verifier failures are repaired by rereading without ops, initializing every dquot in the block with correct magic, version, type, id, UUID, checksum, and timers.

After fork and buffer repair, it finishes deferred work, rolls the transaction, unlocks the quota inode, and iterates dquots through the quota manager. Per-dquot repair fills missing backing blocks, corrects cached file offsets and disk addresses, clamps soft limits to hard limits, caps impossible resource counts to filesystem totals where appropriate, adjusts reservations by the same delta, fixes timers through quota manager helpers, marks dquots dirty, logs them, and rolls.

## State And Persistence Behavior
Persistent changes include quota inode bmap changes, initialized dquot buffers, truncated invalid quota file regions, dquot limits, counters, timers, reservations, and quota CHKD scheduling via `xrep_force_quotacheck`. Transactions are repeatedly rolled to commit buffer and dquot changes safely.

## Dependencies And Integration Points
It depends on quota scrub type conversion, XFS bmap, dquot buffer verifiers, quota manager limit/timer adjustment, reflink cleanup, deferred operations, and transaction repair helpers. It complements `quotacheck_repair.c`, which recomputes exact counters.

## Risks And Edge Cases
Repair does not know exact counts when counters exceed physical limits, so it caps and forces quotacheck. Reflink changes count semantics. Filling sparse quota holes allocates blocks and initializes full dquot clusters. Bad verifier data is repaired at block granularity. Dquot locks must be released only through transaction completion paths when joined.

## Test Signals
Tests should cover sparse quota holes, unwritten extents, mappings past max dquot id, bad dquot magic/type/id/checksum, bigtime timer repair, counters above filesystem size, softlimit greater than hardlimit, reflink quota files, and forced quotacheck after repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quota_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.c

## Purpose
`quotacheck.c` implements live quota counter scrub. It recomputes user, group, and project quota usage by scanning every inode, tracks live quota transaction deltas, and compares the observed counters against incore dquots and quota CHKD flags.

## Important APIs, Types, And Functions
`xchk_setup_quotacheck` allocates `struct xqcheck` and enables quota fsgates. `xchk_quotacheck` runs setup, collection, and comparison. Live transaction tracking uses `struct xqcheck_dqtrx`, `struct xqcheck_dqacct`, `xqcheck_get_dqtrx`, `xqcheck_mod_live_ino_dqtrx`, and `xqcheck_apply_live_dqtrx`. Collection uses `xqcheck_collect_inode` and `xqcheck_collect_counts`; comparison uses `xqcheck_compare_dquot`, `xqcheck_compare_dqtype`, and `xqcheck_walk_observations`.

## Control Flow
Setup creates `xfarray` counter tables for each enabled quota type, initializes an rhashtable keyed by transaction id, starts an inode scan, and installs quota transaction hooks. The mod hook records per-transaction dquot deltas only for quota types being checked and only for inodes already scanned. The apply hook applies committed deltas to shadow counts and frees shadow transaction records when all dquot updates have applied.

Collection cancels the ordinary transaction and scans inodes under an empty transaction. Metadata and quota inodes are skipped. Regular files take IOLOCK and MMAPLOCK; realtime files read data fork extents so data and realtime blocks can be separated. The inode's user/group/project ids update the corresponding shadow dquot counters.

Comparison first checks that the CHKD flag is set for each quota type. It iterates existing dquots and compares inode, data block, and realtime block counts. Then it walks all observed shadow dquots to catch ids that should exist but are missing from the quota file.

## State And Persistence Behavior
Scrub is read-only but uses extensive volatile state: shadow dquot arrays, an iscan cursor, a mutex, quota hooks, and a transaction-id rhashtable. Hook or storage errors abort the iscan and mark scrub incomplete to prevent repair from using partial counts.

## Dependencies And Integration Points
It depends on quota transaction hook infrastructure, inode scanning, block counting, dquot iteration, xfarray, rhashtable, and `quotacheck.h`. Repair in `quotacheck_repair.c` reuses the live observation data.

## Risks And Edge Cases
Missing live deltas would create false corruption, so hook ordering installs the apply hook before the mod hook and removes hooks in reverse-safe order. Sparse-array `EFBIG`, allocation failure, busy inode scans, and hook errors all mark incomplete. Delayed allocation deltas are included with block deltas during commit shadowing. Quota files and metadata directory inodes are intentionally excluded from usage.

## Test Signals
Tests should include live writes, truncates, ownership changes, delayed allocation conversion, realtime files, quota CHKD flag cleared, missing dquots for observed ids, all combinations of enabled quota types, and injected hook allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.h

## Purpose
`quotacheck.h` defines shared live quotacheck state and counter records for scrub and repair.

## Important APIs, Types, And Functions
`struct xqcheck_dquot` stores observed block, inode, and realtime block counts plus record flags. Flags are `XQCHECK_DQUOT_WRITTEN`, `XQCHECK_DQUOT_COMPARE_SCANNED`, and `XQCHECK_DQUOT_REPAIR_SCANNED`. `struct xqcheck` owns scrub context, per-type `xfarray` counters, a mutex, an inode scan, quota hooks, and the shadow transaction rhashtable. `xqcheck_counters_for` maps a dquot type to the matching counter array.

## Control Flow
The header has no standalone flow. Scrub initializes and fills the structure, comparison marks records scanned, and repair marks records repaired while committing counters.

## State And Persistence Behavior
State is volatile and shared across scrub-to-repair for a single operation. The flags prevent uninitialized records from being mistaken for real zero counters and allow second passes to find unvisited observations.

## Dependencies And Integration Points
It depends on XFS quota types, `xfarray`, `xchk_iscan`, quota transaction hooks, and Linux rhashtable. It is consumed by `quotacheck.c` and `quotacheck_repair.c`.

## Risks And Edge Cases
`xqcheck_counters_for` asserts on invalid dquot types and returns NULL, so callers must validate types. Repair depends on the scrub phase leaving complete, current observations.

## Test Signals
Compile and runtime coverage should verify all quota-type mappings, record flag transitions through compare and repair passes, and behavior with only one quota type enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck_repair.c

## Purpose
`quotacheck_repair.c` commits quota counters recomputed by live quotacheck to the actual dquots and manages quota CHKD flags so crash recovery can fall back to mount-time quotacheck if repair is interrupted.

## Important APIs, Types, And Functions
`xrep_quotacheck` is the repair entry point. `xqcheck_commit_dquot` adjusts one dquot from observed `xqcheck_dquot` data. `xqcheck_commit_dqtype` commits all known and observed dquots for one type. `xqcheck_chkd_flags` computes which quota CHKD flags correspond to currently running quota types.

## Control Flow
Repair first clears the CHKD flags for all active quota types and commits, making the filesystem conservatively require quotacheck if a crash occurs mid-repair. It then commits user, group, and project counters where corresponding observation arrays exist. For each quota type it first iterates dquots known to the quota file, then walks the observation array to create or repair dquots that were observed but not previously scanned. Each dquot commit allocates a scrub transaction, joins and locks the dquot, reads the observed counters, adjusts count and reserved fields by deltas, marks the observation repaired, logs dirty dquots, adjusts timers, and commits.

After all dquots are repaired, it allocates a final transaction, restores CHKD flags, and commits.

## State And Persistence Behavior
Persistent changes include dquot counts, reservations, timers, dirty dquot log items, newly allocated dquots for observed ids, and superblock quota CHKD flags. The repair uses the volatile `xqcheck` arrays from scrub as authoritative input.

## Dependencies And Integration Points
It depends on quota manager dquot lookup/allocation, transaction commit/cancel helpers, `quotacheck.h`, tracepoints, and superblock qflag update helpers. It is the repair companion to `quotacheck.c`.

## Risks And Edge Cases
If the live scan was aborted, commits return `-ECANCELED`. A crash after CHKD flags are cleared but before final restoration intentionally leaves mount-time quotacheck as the recovery path. Observed dquot ids absent from the quota file may allocate quota blocks. Negative deltas adjust reservations and counts together, so underflow-sensitive data should be tested.

## Test Signals
Tests should cover interrupted repair with CHKD flags cleared, creating missing observed dquots, count increases and decreases, timer adjustment for nonzero ids, all enabled quota-type combinations, and aborted/incomplete scan repair rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.c

## Purpose
`rcbag.c` implements an in-memory refcount bag: a multiset of reverse mapping extents keyed by start block and length, backed by the in-memory rcbag btree. It is used by scrub/repair algorithms that need to synthesize refcount edges from rmap streams.

## Important APIs, Types, And Functions
`struct rcbag` owns the mount, an `xfbtree`, and `nr_items`. Public functions are `rcbag_init`, `rcbag_free`, `rcbag_add`, `rcbag_count`, `rcbag_next_edge`, `rcbag_remove_ending_at`, and `rcbag_dump`.

## Control Flow
Initialization allocates the bag and initializes an in-memory btree. `rcbag_add` opens a btree cursor, looks for a record matching an rmap, increments its refcount if present, or inserts a new record otherwise, then commits the xfbtree transaction and increments the item count. `rcbag_next_edge` scans the bag and the next rmap candidate to find the next block at which the refcount changes. `rcbag_remove_ending_at` walks from the right edge, deletes records ending at the target block, and decrements `nr_items` by their stored refcount.

## State And Persistence Behavior
All state is in memory and associated with repair/scrub temporary buftarg storage. The btree uses transaction-like commit/cancel semantics but does not persist filesystem metadata.

## Dependencies And Integration Points
It depends on `rcbag_btree.c` cursor operations, `xfbtree`, xfs btree APIs, rmap records, and trace/debug infrastructure. It is a helper for higher-level refcount/rmap repair code.

## Risks And Edge Cases
Corruption-style returns happen if btree lookup says a record exists but cannot retrieve it, insertion does not insert, or no next edge can be found. The `nr_items` field counts multiplicities for additions and removals, not merely btree record count, so callers must interpret it carefully.

## Test Signals
Tests should add duplicate rmaps, add overlapping but differently sized rmaps, compute next edges with and without a pending next rmap, remove records ending at a boundary, and exercise xfbtree transaction cancel paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.h

## Purpose
`rcbag.h` declares the opaque refcount bag API used by scrub/repair code.

## Important APIs, Types, And Functions
It forward-declares `struct rcbag` and exposes initialization, destruction, add, count, next-edge, remove-ending-at, and dump functions.

## Control Flow
Callers create a bag with `rcbag_init`, add rmap records while scanning, repeatedly ask for next refcount edges, remove records ending at each edge, optionally dump diagnostics, and free the bag.

## State And Persistence Behavior
The API represents volatile in-memory btree state. Persistence is limited to the caller's eventual repair decisions.

## Dependencies And Integration Points
It depends on XFS mount, transaction, buftarg, and rmap record types. Implementation requires in-memory btree support through `rcbag_btree`.

## Risks And Edge Cases
The header does not expose feature guards itself, so build configuration must ensure callers are only present when the implementation is available. Ownership and lifetime of `struct rcbag **` are explicit: `rcbag_free` nulls the caller pointer.

## Test Signals
API-level tests should verify init/free lifetime, count behavior after duplicates, and next-edge/remove sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.c

## Purpose
`rcbag_btree.c` implements the in-memory btree operations used by `rcbag.c`. It defines record/key conversion, ordering, verification, cursor allocation, cache lifecycle, and record operations for refcount bag records.

## Important APIs, Types, And Functions
Public functions include `rcbagbt_mem_cursor`, `rcbagbt_mem_init`, `rcbagbt_maxrecs`, `rcbagbt_calc_size`, `rcbagbt_maxlevels_possible`, `rcbagbt_init_cur_cache`, `rcbagbt_destroy_cur_cache`, `rcbagbt_lookup_eq`, `rcbagbt_get_rec`, `rcbagbt_update`, and `rcbagbt_insert`. Internal btree ops include key/record init, comparisons, ordering checks, and buffer verification.

## Control Flow
The file defines `rcbagbt_mem_ops`, an `XFS_BTREE_TYPE_MEM` ops table backed by generic `xfbtree` block allocation, root setting, and cursor duplication. Cursor creation allocates an XFS btree cursor from a slab cache sized for the maximum possible height and attaches the target `xfbtree`. Record helpers populate `cur->bc_rec` and delegate lookup/insert/update to generic btree functions.

## State And Persistence Behavior
The btree stores records in memory buffers with XFS-like btree headers and verification but skips CRC checks for speed. The only global state is the cursor kmem cache. No on-disk filesystem metadata is written.

## Dependencies And Integration Points
It depends on `xfbtree`, `xfs_btree_mem`, buffer verification APIs, and the definitions in `rcbag_btree.h`. `rcbag.c` consumes its cursor and record helpers.

## Risks And Edge Cases
Incorrect ordering would break edge computation in `rcbag.c`. Max-level and max-record calculations must match the in-memory block size and header length. Verification rejects bad magic, v5 headers, too-high levels, and oversized record counts. The slab cache must be initialized before cursor allocation and destroyed at module shutdown.

## Test Signals
Tests should cover cursor cache lifecycle, insert/update/get/lookup behavior, ordering for equal startblock but different length records, maxlevels calculations for large record counts, and verifier rejection of malformed memory blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.h

## Purpose
`rcbag_btree.h` defines the record format, block layout macros, and public helpers for the in-memory refcount bag btree.

## Important APIs, Types, And Functions
Under `CONFIG_XFS_BTREE_IN_MEM`, it defines `RCBAG_MAGIC`, `struct rcbag_key`, `struct rcbag_rec`, `rcbag_ptr_t`, `RCBAG_BLOCK_LEN`, address macros for records, keys, and pointers, sizing helpers, cursor cache lifecycle, memory initialization, cursor creation, lookup/get/update/insert functions. Without in-memory btree support it stubs cache lifecycle only.

## Control Flow
There is no runtime flow in the header. The macros describe how btree blocks are laid out after the long-form CRC header.

## State And Persistence Behavior
The described state is volatile btree-buffer state. Records contain AG start block, block count, and multiplicity refcount.

## Dependencies And Integration Points
It depends on XFS btree block layout constants, `xfbtree`, mount, transaction, cursor, and rmap types. It is shared by `rcbag.c` and `rcbag_btree.c`; address macros are noted as used by userspace too.

## Risks And Edge Cases
Feature guarding is partial: most APIs disappear without `CONFIG_XFS_BTREE_IN_MEM`, so callers must be compiled conditionally. Layout macros must remain synchronized with `rcbag_btree.c` verifier and max record calculations.

## Test Signals
Compile both config paths, validate address macro offsets, and verify record/key sizing fits inside XFS btree unions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.c

## Purpose
`readdir.c` provides scrub-oriented directory iteration, exact directory lookup, and careful lock acquisition for parent-pointer validation. It normalizes shortform, block, leaf, and node directory formats behind one callback API.

## Important APIs, Types, And Functions
Public functions are `xchk_dir_walk`, `xchk_dir_lookup`, and `xchk_dir_trylock_for_pptrs`. Format-specific walkers are `xchk_dir_walk_sf`, `xchk_dir_walk_block`, `xchk_read_leaf_dir_buf`, and `xchk_dir_walk_leaf`. Lock helpers are `xchk_dir_trylock_both` and `xchk_dir_trylock_for_pptrs`.

## Control Flow
`xchk_dir_walk` asserts the target is a locked directory, determines its format with `xfs_dir2_format`, and dispatches. Shortform walking synthesizes `.` and `..` before iterating inline entries. Block walking reads the single block and scans data entries while skipping free regions. Leaf/node walking advances over mapped directory data blocks before `XFS_DIR2_LEAF_OFFSET`, reading buffers as needed and reporting entries.

`xchk_dir_lookup` builds `xfs_da_args` and delegates exact lookup to `xfs_dir_lookup_args`, with special owner handling for temporary repair directories whose block headers are owned by the original scrub target. `xchk_dir_trylock_for_pptrs` repeatedly tries to lock the scrub target and a parent directory without deadlocking on corrupt trees.

## State And Persistence Behavior
The file is read-only except for lock state and transaction buffer references. Buffer reads are released before return. Lock helper state is reflected in `sc->ilock_flags` and returned parent lock modes.

## Dependencies And Integration Points
It depends on XFS directory format internals, scrub transactions, inode locking, and common termination checks. Nlinks, parent, parent repair, and orphanage adoption use these helpers for directory scans and lookups.

## Risks And Edge Cases
The walkers trust callers to hold ILOCK. Leaf walking must handle holes and mapped extents correctly. Buffer cache and verifier errors propagate. Parent-pointer locking intentionally avoids normal two-inode ordering because corrupt trees can create cycles; it can return timeout/incomplete or deadlock retry signals.

## Test Signals
Tests should cover all directory formats, free-space entries, sparse leaf directories, temporary directory lookup owner overrides, shutdown behavior, invalid format errors, and parent-pointer lock contention under `TRY_HARDER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.h

## Purpose
`readdir.h` declares the scrub directory callback API and lock helper used by multiple scrub and repair modules.

## Important APIs, Types, And Functions
`xchk_dirent_fn` is the callback signature receiving scrub context, directory inode, data position, name, inode number, and private data. Declared functions are `xchk_dir_walk`, `xchk_dir_lookup`, and `xchk_dir_trylock_for_pptrs`.

## Control Flow
No standalone control flow exists. Callers provide a callback and private state to `xchk_dir_walk`, or use `xchk_dir_lookup` for exact name resolution.

## State And Persistence Behavior
The API itself is read-only. Lock helper calls mutate held lock state in the scrub context.

## Dependencies And Integration Points
It depends on XFS directory dataptr, name, inode, and scrub types. It is a central integration point for nlinks, parent scrub, parent repair, and orphanage code.

## Risks And Edge Cases
Callbacks must be prepared for synthesized dot entries in shortform directories and for names that have not yet been semantically validated. Callers must hold the required inode locks before walking or lookup.

## Test Signals
Callback consumers should test correct handling of dot, dotdot, invalid names, and early callback error termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.c

## Purpose
`reap.c` disposes of blocks that belonged to old or damaged metadata after online repair has rebuilt replacement structures. It decides whether to free extents, remove only reverse mappings for crosslinked blocks, invalidate incore buffers, manage AGFL returns, and keep deferred log intent chains within transaction reservation budgets.

## Important APIs, Types, And Functions
Public APIs are `xrep_reap_agblocks`, `xrep_reap_fsblocks`, `xrep_reap_rtblocks`, `xrep_reap_metadir_fsblocks`, `xrep_reap_ifork`, `xrep_bufscan_max_sectors`, and `xrep_bufscan_advance`. `struct xreap_state` carries scrub context, owner/reservation or inode/fork target, buffer invalidation counters, and deferred-op counters.

AG/free-space helpers include `xreap_agextent_select`, `xreap_agextent_iter`, `xreap_agextent_binval`, `xreap_put_freelist`, and limit configurators. File fork helpers include `xreap_bmapi_select`, `xreap_bmapi_binval`, `xrep_reap_bmapi_iter`, `xreap_ifork_extent`, and `xreap_configure_bmapi_limits`. Realtime paths are compiled under `CONFIG_XFS_RT`.

## Control Flow
For per-AG and fsblock bitmaps, the code walks bitmap extents, selects maximal subranges with the same crosslink status by querying rmapbt, invalidates buffers where safe, and either schedules rmap removal or deferred free operations. Crosslinked blocks are unmapped from the repaired owner but not freed. Non-crosslinked blocks are invalidated and freed or returned to AGFL depending on reservation type.

For file forks, `xrep_reap_ifork` walks real mappings, reads AGF state for the mapping's AG, chooses crosslinked subranges with offset-specific owner info, invalidates file buffers, schedules bmap removal, quota block-count adjustment, rmap removal, and free operations. It finishes deferred ops after each mapping. Realtime variants lock rtgroups and use rt rmap/refcount/free intent paths.

## State And Persistence Behavior
Persistent changes include rmap removal, refcount cleanup for CoW staging extents, bmap extent removal, quota block-count adjustments, AGFL insertion, and free-space updates. Incore buffer invalidation is transaction logged where possible, or stale-marked for unloggable large buffers. The code frequently rolls or finishes transactions based on computed log reservation limits.

## Dependencies And Integration Points
It depends on rmapbt, refcountbt, allocation, AG/rtgroup locking, bitmap walkers, deferred operation items, buffer cache APIs, quota accounting, bmap APIs, metadata reservation reset, and tracepoints. Many repair modules call it after rebuilding btrees or file forks.

## Risks And Edge Cases
Crosslinked metadata cannot always be fully fixed because buffer-cache aliasing can hide multi-block overlaps. The code deliberately avoids freeing blocks with other owners. Log reservation underestimation triggers shutdown to avoid unsafe continuation. Buffer invalidation limits can shorten an extent and force transaction rolls. AGFL blocks are handled one at a time. Realtime support is conditional.

## Test Signals
Tests should cover crosslinked and non-crosslinked old btree blocks, CoW staging extents, AGFL reaping, metadir fsblocks, file attr/data fork reaping, large remote xattr buffers, transaction roll thresholds, realtime bitmap paths, missing rmap records, and crash recovery with partially completed deferred frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.h

## Purpose
`reap.h` declares the block disposal APIs used by online repair after rebuilding metadata and defines the buffer-cache scan context used to find incore buffers over old extents.

## Important APIs, Types, And Functions
It declares reaping functions for AG block bitmaps, fsblock bitmaps, inode forks, metadata-directory fsblocks, and realtime block bitmaps. `struct xrep_bufscan` tracks a disk address, maximum scan length, step size, and internal sector count. `xrep_bufscan_max_sectors` and `xrep_bufscan_advance` drive buffer-cache scanning.

## Control Flow
Callers choose the reaping API matching the coordinate space of their old metadata: AG blocks, fsblocks, realtime blocks, metadir blocks, or file fork mappings. Realtime reaping returns `-EOPNOTSUPP` when realtime support is not compiled.

## State And Persistence Behavior
The header itself has no persistence. The declared functions persistently mutate allocation, rmap, bmap, refcount, and quota metadata through transactions.

## Dependencies And Integration Points
It depends on scrub context, bitmap types, owner info, AG reservation types, inode types, and mount/block address types. It is used throughout repair modules that replace old metadata structures.

## Risks And Edge Cases
Callers must pass the correct owner info and bitmap coordinate type; mixing them could free or unmap the wrong metadata. Realtime callers must handle the stubbed unsupported case.

## Test Signals
Compile both realtime and non-realtime configurations, and test each public reaping API with empty and non-empty bitmaps plus buffer scan progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.h -->
