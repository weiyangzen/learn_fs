# Group Research: group_1108_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_nlinks_c_so_ebfa82ae2744

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.c

- Role: Live scrub implementation for inode link counts. It builds shadow per-inode link counters by walking the filesystem, tracks concurrent directory updates through dirent hooks, and compares the observed counters to live inode `i_nlink` values.
- Setup: `xchk_setup_nlinks` enables directory-entry fs gates, optionally prepares repair via `xrep_setup_nlinks`, allocates `struct xchk_nlink_ctrs`, and enters filesystem scrub setup.
- Collection phase:
  - Creates an `xfarray` indexed by inode number for `struct xchk_nlink`.
  - Counts superblock-rooted metadata files such as rt bitmap/summary and quota inodes as linked.
  - Walks all inodes with `xchk_iscan`; directories are scanned with `xchk_dir_walk`, non-directories are only marked visited.
  - For dirents, validates names, `.` self-reference, and inode numbers; increments parent counts for normal entries, child counts for directory children, and backref counts for `..` entries when parent pointers are absent.
  - On parent-pointer filesystems, walks parent pointer xattrs to derive directory backref counts instead of trusting only `..`.
- Live update handling: `xchk_nlinks_live_update` observes dirent changes after a directory or child has been scanned and updates shadow counters under `xnc->lock`. Any hook failure aborts the inode scan so scrub reports incomplete data instead of false corruption.
- Comparison phase:
  - Walks allocated inodes and compares observed totals to `VFS_I(ip)->i_nlink`.
  - For old filesystems without ftype, substitutes `backrefs` for `children` when checking directories.
  - Flags corruption on impossible totals, mismatched link counts, non-directories with child/backref counts, linked non-root files with no parents, or root directories without exactly one parent.
  - Performs a second pass over unvisited shadow records to catch observations for missing/free inodes.
- Error model: Collection errors that undermine completeness set `XFS_SCRUB_OFLAG_INCOMPLETE`; comparison corruption often returns `-ECANCELED` to stop early.
- Dependencies: `iscan`, `xfarray`, directory walking, xattr walking, parent pointers, tempfile filtering, and orphanage repair setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.h

- Role: Shared data structures for live link count scrub and repair.
- `struct xchk_nlink_ctrs`: Holds scrub context, shadow `xfarray`, mutex, collection and comparison inode scans, dirent hook, orphanage adoption state, and reusable name buffer.
- `struct xchk_nlink`: Stores observed link components:
  - `parents`: forward links from directories to this inode.
  - `backrefs`: `..` or parent-pointer back links from child directories to this directory.
  - `children`: directory child entries plus directory `.` accounting used in total calculation.
  - `flags`: written/compare/repair state.
- Flags:
  - `XCHK_NLINK_WRITTEN`
  - `XCHK_NLINK_COMPARE_SCANNED`
  - `XREP_NLINK_DIRTY`
- `xchk_nlink_total`: Computes expected `i_nlink` as observed parents plus one dot entry for linked directories plus observed children. Uses `uint64_t` to detect overflow before clamping or flagging corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks_repair.c

- Role: Online repair for inode link counts using the live shadow data collected by `nlinks.c`.
- Setup: `xrep_setup_nlinks` attempts to create/attach the orphanage (`/lost+found`) so parentless linked files can be reattached during repair.
- Main repair path:
  - `xrep_nlinks` requires ftype support because accurate child directory counts are needed.
  - Iterates allocated inodes using `compare_iscan`; each inode repair cancels the scrub transaction and creates a purpose-specific transaction.
  - `xrep_nlinks_repair_inode` reads the collected shadow record while holding the inode lock, computes expected total links, and updates `i_nlink` if needed.
- Orphan handling:
  - Non-root, non-orphanage inodes with nonzero actual link count but no observed parents may be moved to the orphanage.
  - Adoption updates the directory tree, then rereads the shadow counter because live dirent hooks should have observed the move.
- Unlinked list handling:
  - If total links are positive and inode is on the unlinked list, remove it.
  - If total links are zero and inode is not on the unlinked list, add it.
- Limits and unfixable states:
  - Non-directories with directory children are treated as unfixable and skipped without changing counters.
  - Written link count is clamped to `XFS_NLINK_PINNED`.
- Locking: Coordinates IOLOCK/ILOCK ordering with orphanage locks and transaction reservations; uses `xrep_orphanage_iolock_two` and `xrep_adoption_trans_alloc` when adoption is possible.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/off_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/off_bitmap.h

- Role: Thin type-safe wrapper around `xbitmap64` for file-offset ranges.
- `struct xoff_bitmap`: Contains one `xbitmap64`.
- Helpers:
  - `xoff_bitmap_init`
  - `xoff_bitmap_destroy`
  - `xoff_bitmap_set`
  - `xoff_bitmap_walk`
- Purpose: Lets scrub code track `xfs_fileoff_t` / `xfs_filblks_t` ranges without directly exposing generic 64-bit bitmap operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/off_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.c

- Role: Shared online repair support for creating and using `/lost+found` as an orphanage for disconnected files.
- Orphanage creation:
  - `xrep_orphanage_create` finds the root dentry, creates `lost+found` if missing, verifies it is a directory, grabs an inode reference, and stores it in `sc->orphanage`.
  - New orphanage directories are created mode `0750`.
  - `xrep_chown_orphanage` makes it root-owned, clears setuid/setgid/sticky bits, clears realtime inheritance flags, and updates quota ownership state.
- Lock helpers: Tracks orphanage lock flags in scrub context and provides blocking/nowait lock wrappers plus `xrep_orphanage_iolock_two` for coordinated target/orphanage IOLOCK acquisition.
- Adoption support:
  - `xrep_orphanage_can_adopt` rejects the orphanage itself, superblock-rooted files, and internal metadata inodes.
  - `xrep_adoption_trans_alloc` reserves space/quota for adding the orphanage name, possible child `..` replacement, and parent pointer attr fork work.
  - `xrep_adoption_compute_name` chooses a unique name based on inode number, appending `.N` up to 10000 attempts.
  - `xrep_adoption_move` creates the orphanage dirent, updates orphanage timestamps/link count, optionally bumps child nlink, replaces child `..` for directories, adds parent pointer if enabled, notifies dirent hooks, and invalidates affected dentries.
  - `xrep_adoption_trans_roll` finishes deferred ops and rolls to a clean transaction.
- Dcache handling: Checks for unexpected positive dentries before adoption and invalidates negative orphanage dentries plus aliases of the adopted child after the move.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.h

- Role: Interface for online repair orphanage and adoption operations.
- Under `CONFIG_XFS_ONLINE_REPAIR`, declares orphanage creation, lock/unlock/release helpers, adoption transaction setup, name computation, move, and transaction roll.
- `xrep_orphanage_try_create`: Wrapper used by repair setup. Treats missing, non-directory, and no-space orphanage outcomes as nonfatal so repair can continue without adoption.
- `struct xrep_adoption`: Carries scrub context, chosen name, parent pointer args, orphanage/child block reservations, and whether to bump child nlink.
- Without online repair, exposes an empty `struct xrep_adoption` and no-op orphanage release.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/parent.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/parent.c

- Role: Scrubs directory parent information. Supports both legacy `..` validation and parent-pointer xattr validation.
- Setup: `xchk_setup_parent` optionally initializes repair support, then sets up inode-content scrub.
- Legacy mode without parent pointers:
  - Only directories are meaningful; non-directories return `-ENOENT`.
  - Looks up `..`, validates inode number, and checks that the alleged parent is a directory containing exactly one entry pointing back, except unlinked directories expect zero.
  - Handles root and metadata root as self-parented.
  - Uses trylock/retry logic to avoid deadlocks with parent directories.
- Parent-pointer mode:
  - Walks parent pointer xattrs and validates each against the alleged parent directory’s forward dirent.
  - Rejects self-referential parent pointers.
  - Validates parent inode type and generation.
  - Defers parent pointers that cannot be checked due to lock contention into `xfarray`/`xfblob` scratch storage, then revalidates them later after lock cycling.
  - For directories, confirms `..` matches at least one parent pointer, while allowing corrupt multi-parent situations to be handled by directory loop repair.
  - Compares parent pointer count to link count: non-directories should match exactly; linked directories need at least one parent pointer; unlinked directories should have none.
- `xchk_pptr_looks_zapped`: Detects attr forks that were removed or reset by inode/fork repair and should postpone parent-pointer checking.
- Dependencies: Directory walking/lookup, xattr walking, parent pointer decoding, tempfile filtering, and `xfarray`/`xfblob` scratch storage.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/parent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/parent_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/parent_repair.c

- Role: Repairs parent metadata, either by fixing directory `..` entries or by rebuilding parent-pointer xattrs.
- Setup:
  - Enables dirent fs gates.
  - Allocates `struct xrep_parent`.
  - Creates a temporary regular file used to build replacement attr fork contents.
  - Attempts orphanage creation for disconnected targets.
- Without parent pointers:
  - `xrep_parent_find_dotdot` finds a plausible parent via self-reference, dcache, or a full filesystem scan.
  - `xrep_parent_reset_dotdot` replaces `..` if needed.
- With parent pointers:
  - Requires rmapbt and exchange-range support because repair swaps attr fork mappings and reaps old blocks.
  - Scans all directories for entries pointing to the target and stashes parent-pointer add operations.
  - Hooks live dirent updates so concurrent adds/removes affecting already-scanned parents are replayed into the temporary file.
  - Periodically flushes staged parent-pointer updates to bound memory use.
  - Copies all non-parent xattrs to the temp file, with restart logic if parent-pointer updates happen while attrs are being flushed.
  - Ensures both target and temp file have attr forks, replays final parent-pointer updates, atomically swaps xattr contents with `xrep_xattr_swap`, and resets the temp fork.
- Orphanage fallback: After rebuilding parent information, files with no parent may be moved to `/lost+found` if adoption is possible; otherwise repair reports corruption.
- Non-directory link count repair: After parent-pointer rebuild, recounts parent pointers and updates non-directory `i_nlink` and unlinked-list membership.
- Concurrency: Uses inode scan hooks, mutex-protected staging arrays, explicit IOLOCK/ILOCK choreography, and transaction rolls around temp-file mutation and adoption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/parent_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quota.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quota.c

- Role: Scrubs one quota type’s quota inode and dquot records.
- `xchk_quota_to_dqtype`: Maps scrub type to user/group/project quota type.
- Setup:
  - Requires quotas globally enabled and the requested quota type active.
  - Enables intent drain when needed.
  - Installs the quota inode as the live scrub inode and takes `ILOCK_EXCL`.
- Data fork checking:
  - Runs metadata inode fork scrub.
  - Ensures quota file extents are written and within the maximum dquot id offset.
  - Rejects delalloc, unwritten, or out-of-range quota mappings.
- Dquot item checking:
  - Iterates dquots with `xchk_dquot_iter`.
  - Verifies dquot id order, file offset, backing bmap record, disk address, and written extent state.
  - Warns on hard limits larger than filesystem capacity; flags soft limits greater than hard limits as corruption.
  - Checks usage counts against physical block/inode limits, with reflink filesystems treated more leniently for block counts.
  - Checks quota timers: timers must be set only when usage exceeds soft/hard thresholds.
- Error behavior: Stops early on corruption via `-ECANCELED` but converts that to success after marking scrub state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quota.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quota.h

- Role: Shared quota scrub declarations.
- Declares `xchk_quota_to_dqtype`.
- `struct xchk_dqiter`: Cursor for walking dquot records. Tracks scrub context, quota inode, cached bmap, next id, quota type, and data fork sequence number for stale mapping detection.
- Declares:
  - `xchk_dqiter_init`
  - `xchk_dquot_iter`
- Consumers in this group use the iterator from quota scrub, quota repair, and quotacheck repair.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quota_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quota_repair.c

- Role: Repairs malformed quota inode mappings and dquot records for one active quota type.
- Data fork repair:
  - Calls metadata inode fork repair.
  - Converts unwritten quota extents to written extents.
  - Truncates mappings beyond the maximum dquot id offset and cancels CoW reservations/reflink state.
  - Reads each quota block; if verifier/type/id checks fail, rewrites every dquot in the chunk with correct magic, version, type, id, UUID, checksum, and timer compatibility.
- Dquot backing block repair:
  - `xrep_quota_item_bmap` ensures each dquot has a real written block at its computed file offset.
  - Sparse holes are filled by allocating and initializing quota blocks.
  - Cached `q_blkno` is updated if repair changed the physical block.
- Dquot field repair:
  - Clamps soft limits down to hard limits.
  - Clamps impossible usage counts to filesystem maxima on non-reflink filesystems and schedules a quotacheck because the true count is unknown.
  - Fixes timer state through normal quota timer adjustment.
  - Logs dirty dquots in transactions and rolls as needed.
- Completion: Rolls off the quota inode, unlocks it, repairs dquot-level problems, and commits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quota_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.c

- Role: Live quotacheck scrub. Recomputes quota usage counters from all inodes and compares them to incore dquot counters.
- Setup: Requires quota enabled, enables quota fs gates, allocates `struct xqcheck`, and sets up filesystem scrub.
- Shadow accounting:
  - Allocates sparse `xfarray` counter tables for active user/group/project quotas.
  - Uses an inode scan to count one inode plus data/realtime block usage into the appropriate owner/group/project ids.
  - Skips quota inodes and metadata-directory inodes.
  - Realtime files have data fork extents read so realtime block usage can be counted accurately.
- Live transaction hooks:
  - `xqcheck_mod_live_ino_dqtrx` records per-transaction quota deltas for already-scanned inodes into a hash keyed by transaction id.
  - `xqcheck_apply_live_dqtrx` applies those deltas to shadow counters at quota transaction commit and frees shadow transaction state.
  - Hook failures abort the scan so scrub reports incomplete data.
- Comparison:
  - Verifies quota `CHKD` flags are set for each checked quota type.
  - Iterates real dquots and compares `icount`, `bcount`, and `rtbcount` against shadow counters.
  - Walks observations not seen in the dquot iterator and ensures corresponding dquots exist and match.
- Teardown: Removes quota hooks, destroys hash state and all counter arrays, tears down scan state, and clears scrub pointer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.h

- Role: Shared definitions for live quotacheck scrub and repair.
- `struct xqcheck_dquot`: Shadow dquot usage counters for blocks, inodes, realtime blocks, plus state flags.
- Flags:
  - `XQCHECK_DQUOT_WRITTEN`
  - `XQCHECK_DQUOT_COMPARE_SCANNED`
  - `XQCHECK_DQUOT_REPAIR_SCANNED`
- `struct xqcheck`: Holds scrub context, active quota counter arrays, mutex, inode scan, quota transaction hooks, and hash table of shadow transaction accounting.
- `xqcheck_counters_for`: Maps user/group/project quota type to the corresponding counter `xfarray`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck_repair.c

- Role: Commits recomputed live quotacheck counters back to dquots.
- Safety sequence:
  - Clears quota `CHKD` flags for active quota types before modifying counters, then commits. If the system crashes, mount-time quotacheck can recover.
  - Commits recomputed counters by quota type.
  - Sets `CHKD` flags again only after all counter repair succeeds.
- `xqcheck_commit_dquot`:
  - Allocates a transaction, locks and joins the dquot, reads shadow counts, adjusts `reserved` and `count` deltas for inode/block/realtime counters, marks the shadow record repaired, adjusts timers, logs the dquot, and commits.
  - Cancels cleanly if no counter changed.
- `xqcheck_commit_dqtype`:
  - First updates all dquots found by the quota file iterator.
  - Then walks shadow observations not repaired in the first pass, allocates missing dquots with `xfs_qm_dqget(..., true, ...)`, and commits them too.
- Dependencies: Relies on `quotacheck.c` leaving live shadow counter arrays and hooks active through the scrub-to-repair cycle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.c

- Role: In-memory “refcount bag” abstraction backed by an in-memory btree. It stores reverse mappings with multiplicity so repair code can compute sharing/refcount edges.
- `struct rcbag`: Holds mount, `xfbtree`, and total item count.
- Lifecycle:
  - `rcbag_init` allocates and initializes the memory btree.
  - `rcbag_free` destroys the btree and clears the caller pointer.
- Operations:
  - `rcbag_add` inserts a reverse mapping or increments its record refcount if already present; commits the in-memory btree transaction.
  - `rcbag_count` returns total multiplicity, not merely unique records.
  - `rcbag_next_edge` returns the next block where refcount can change, considering the next incoming rmap start and every active record end.
  - `rcbag_remove_ending_at` removes all records ending at a given block and subtracts their multiplicities.
  - `rcbag_dump` prints contents for diagnostics.
- Transaction behavior: On cursor errors, cancels the in-memory btree transaction to keep scratch state consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.h

- Role: Public interface for the refcount bag.
- Declares opaque `struct rcbag` and the operations to initialize, free, add rmaps, count items, find the next edge, remove ending records, and dump contents.
- Used by scrub/repair code that needs a compact active set of reverse mappings while reconstructing refcount information.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.c

- Role: Implements the in-memory btree mechanics for `rcbag`.
- Btree contents:
  - Key: start block and block count.
  - Record: start block, block count, refcount/multiplicity.
- Defines XFS btree callbacks for key initialization, record initialization, key comparison, ordering checks, memory block verification, and cursor allocation.
- Verification: Uses v5 filesystem-block btree header verification and memory btree block verification; skips CRC checks for speed because this is in-memory scratch state.
- Cursor/cache:
  - `rcbagbt_mem_cursor` creates a memory btree cursor over an `xfbtree`.
  - `rcbagbt_init_cur_cache` and `rcbagbt_destroy_cur_cache` manage cursor slab cache.
- Sizing helpers:
  - `rcbagbt_maxrecs`
  - `rcbagbt_maxlevels_possible`
  - `rcbagbt_calc_size`
- Record helpers:
  - `rcbagbt_lookup_eq`
  - `rcbagbt_get_rec`
  - `rcbagbt_update`
  - `rcbagbt_insert`
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.h

- Role: Header for the in-memory rcbag btree.
- Available only under `CONFIG_XFS_BTREE_IN_MEM`; otherwise init/destroy macros become no-ops.
- Defines:
  - `RCBAG_MAGIC`
  - `struct rcbag_key`
  - `struct rcbag_rec`
  - `rcbag_ptr_t`
  - block layout address macros for records, keys, and pointers.
- Declares sizing, cache lifecycle, memory btree initialization, cursor creation, lookup, get, update, and insert helpers.
- Notes that address macros may be used by userspace even if not referenced in kernel code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.c

- Role: Directory iteration and lookup helpers for scrub code.
- Directory walking:
  - `xchk_dir_walk_sf` synthesizes `.` and `..` for shortform directories and iterates shortform entries.
  - `xchk_dir_walk_block` reads a block-format directory and walks non-free data entries.
  - `xchk_dir_walk_leaf` scans mapped data blocks below `XFS_DIR2_LEAF_OFFSET` for leaf/node-format directories.
  - `xchk_dir_walk` dispatches by XFS directory format and requires caller to hold ILOCK.
- Lookup:
  - `xchk_dir_lookup` wraps `xfs_dir_lookup_args`, supports temporary directory owner substitution, and requires caller to hold ILOCK.
- Parent-pointer locking helper:
  - `xchk_dir_trylock_for_pptrs` repeatedly tries to lock scrub target and peer inode in a safe order for parent-pointer validation.
  - Returns `-EDEADLOCK` for retry, `-ETIMEDOUT` with incomplete state under `XCHK_TRY_HARDER`, or termination errors.
- Locking intent: Avoids deadlocks in corrupt directory trees where normal parent/child lock ordering cannot be trusted.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.h

- Role: Public interface for scrub directory walking.
- Defines `xchk_dirent_fn`, a callback receiving scrub context, directory inode, directory data position, name, target inode number, and caller-private data.
- Declares:
  - `xchk_dir_walk`
  - `xchk_dir_lookup`
  - `xchk_dir_trylock_for_pptrs`
- Used by nlink scrub, parent scrub/repair, orphanage adoption, and other directory-aware repair code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/reap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/reap.c

- Role: Reclaims or disconnects old metadata blocks after online repair builds replacement structures.
- Core model:
  - Uses reverse mapping data to decide whether blocks are crosslinked.
  - Crosslinked blocks have this owner’s rmap removed but are not freed.
  - Single-owner blocks have buffers invalidated and are freed or returned to the proper allocator path.
  - Work is throttled to transaction reservation limits for buffer invalidations and deferred intents.
- `struct xreap_state`: Carries scrub context, owner info or inode/fork target, buffer invalidation counters, and deferred-operation counters.
- Buffer scanning:
  - `xrep_bufscan_max_sectors` bounds plausible buffer sizes.
  - `xrep_bufscan_advance` scans the incore buffer cache for buffers at a disk address and increasing lengths.
  - AG and file-fork paths invalidate logged buffers where possible; oversized/unloggable file buffers are staled directly.
- AG/fsblock reaping:
  - `xrep_reap_agblocks` reaps per-AG metadata extents from an `xagb_bitmap`.
  - `xrep_reap_fsblocks` reaps filesystem-block bitmap extents for file metadata or CoW staging.
  - `xrep_reap_metadir_fsblocks` handles metadata-directory btree blocks and resets metadata file reservations afterward.
  - AGFL blocks are returned one at a time via `xreap_put_freelist`.
- Realtime support under `CONFIG_XFS_RT`:
  - `xrep_reap_rtblocks` handles realtime CoW staging extents using rtgroup rmap/refcount locks.
- Inode fork reaping:
  - `xrep_reap_ifork` walks real mappings in a target fork and removes/frees them.
  - `xreap_bmapi_select` splits a mapping by crosslink status.
  - `xrep_reap_bmapi_iter` schedules bmap unmap, rmap unmap, quota block decrement, and possible extent free.
- Reservation logic: Dedicated configuration helpers estimate worst-case log space for EFI/RUI/CUI/BUI chains and buffer invalidations, then force transaction rolls or defer finishes before reservations are exhausted.
- Assumptions: Requires rmapbt for all exported reap paths; callers must already hold the relevant inode/AG locks for the repair operation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/reap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/reap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/reap.h

- Role: Public interface for block reaping after repair.
- Declares reaping entry points:
  - `xrep_reap_agblocks`
  - `xrep_reap_fsblocks`
  - `xrep_reap_ifork`
  - `xrep_reap_metadir_fsblocks`
  - `xrep_reap_rtblocks` or `-EOPNOTSUPP` stub without realtime support.
- Defines `struct xrep_bufscan`, the state used to search for incore buffers over a disk address and increasing sector counts.
- Declares buffer scan helpers:
  - `xrep_bufscan_max_sectors`
  - `xrep_bufscan_advance`
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/reap.h -->