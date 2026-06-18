# Group Research: group_866_linux_sources_os_linux_linux_fs_xfs_scrub_nlinks_c_sources_os_linux__54acc58d5a30

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/nlinks.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/nlinks.c

## Role
Implements live filesystem-wide inode link-count scrub for XFS. Link counts are treated as summary metadata derived from directory entries and parent pointers, so this file builds a shadow counter table by scanning all inodes and then compares it against actual inode `i_nlink` values.

## Setup
- `xchk_setup_nlinks` enables the dirent fsgate, prepares repair via `xrep_setup_nlinks` when possible, allocates `struct xchk_nlink_ctrs`, and calls `xchk_setup_fs`.
- `xchk_nlinks_setup_scan` initializes the collection iscan, creates a sparse `xfarray` large enough for possible inode numbers, installs a directory update hook, and arranges deferred cleanup.

## Collection Phase
- `xchk_nlinks_collect` first counts superblock-rooted metadata files, then walks all allocated inodes.
- Directories are locked with IOLOCK plus ILOCK, scanned through `xchk_dir_walk`, and optionally scanned for parent-pointer xattrs.
- Non-directories simply advance the iscan cursor under IOLOCK.
- Temporary repair staging files/directories are ignored to avoid counting repair internals.

## Counters
- `xchk_nlinks_update_incore` updates `parents`, `backrefs`, and `children` in the sparse `xfarray`.
- `careful_add` clamps counters to `U32_MAX`; later checks still catch values beyond XFS limits.
- Directory entries increment parent counts for children and child counts for directories; `..` contributes backrefs unless parent pointers are enabled.

## Live Updates
- `xchk_nlinks_live_update` receives dirent notifications while the scan is running.
- Updates are applied only when the affected inode or directory has already been scanned.
- Hook failures abort the iscan, forcing `INCOMPLETE` so repair cannot use partial data.

## Comparison Phase
- `xchk_nlinks_compare` walks all allocated inodes and compares actual link counts to observed totals.
- Skipped or leftover observations are checked with `xchk_nlinks_compare_inum`, using AGI protection for missing/unallocated inode numbers.
- Directories require matching child/backref counts; non-directories and unlinked directories must not have backrefs or children.
- Overflow beyond `XFS_NLINK_PINNED` is corruption; values beyond `XFS_MAXLINK` are warnings.

## Risk Points
- Correctness depends on live dirent hooks staying installed until repair or teardown.
- Any collection error must set `INCOMPLETE`; otherwise repair could write bad link counts.
- Parent-pointer filesystems derive directory backrefs from xattrs instead of `..` entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/nlinks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/nlinks.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/nlinks.h

## Role
Defines the data structures shared by live nlink scrub and repair.

## Main Structures
- `struct xchk_nlink_ctrs` holds the scrub context, sparse shadow link-count array, mutex, collection and comparison iscans, dirent hook, orphanage adoption state, and reusable name buffer.
- `struct xchk_nlink` records observed `parents`, `backrefs`, `children`, and state flags for one inode.

## Flags
- `XCHK_NLINK_WRITTEN` marks initialized shadow records.
- `XCHK_NLINK_COMPARE_SCANNED` marks records already compared.
- `XREP_NLINK_DIRTY` marks records already repaired.

## Link Total
- `xchk_nlink_total` computes the expected `i_nlink` from observed parent links plus child-directory links.
- Linked directories get one extra count for `.`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/nlinks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/nlinks_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/nlinks_repair.c

## Role
Repairs inode link counts using the live shadow data collected by `nlinks.c`.

## Setup
- `xrep_setup_nlinks` tries to create/attach the orphanage (`/lost+found`) so disconnected linked inodes can be adopted.

## Repair Flow
- `xrep_nlinks` requires filetype support because accurate child directory counting depends on dirent ftypes.
- It scans all allocated inodes using a comparison iscan and calls `xrep_nlinks_repair_inode`.
- Empty transactions are used between inode repairs to avoid metadata deadlocks.

## Inode Repair
- Loads observed counts from the shared `xfarray` while holding the nlink mutex and inode locks.
- Refuses unfixable non-directories with child-directory observations.
- Orphaned linked inodes with no parents can be moved to the orphanage.
- Synchronizes the unlinked list:
  - linked inodes on the unlinked list are removed from it;
  - unlinked inodes not on the list are added.
- Updates VFS `i_nlink`, capped at `XFS_NLINK_PINNED`, and logs the inode core.

## Risk Points
- Repair is only valid if the collection scan was not aborted.
- Orphanage adoption requires careful IOLOCK/ILOCK and transaction ordering.
- Missing ftype support disables repair rather than risking wrong directory counts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/nlinks_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/off_bitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/off_bitmap.h

## Role
Provides a type-checked wrapper around `xbitmap64` for `xfs_fileoff_t` file offsets.

## API
- `xoff_bitmap_init` initializes the wrapped bitmap.
- `xoff_bitmap_destroy` releases bitmap storage.
- `xoff_bitmap_set` marks a file-offset range.
- `xoff_bitmap_walk` iterates marked ranges using an `xbitmap64` callback.

## Integration
This is a small helper header for scrub/repair code that wants bitmap operations expressed in XFS file-offset units instead of raw 64-bit integers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/off_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/orphanage.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/orphanage.c

## Role
Implements online repair’s orphanage directory, modeled after `xfs_repair`’s `/lost+found`, and provides adoption helpers for reconnecting orphaned files.

## Orphanage Creation
- `xrep_orphanage_create` locates the root dentry, creates or finds `lost+found`, verifies it is a directory, grabs its inode, and stores it in `sc->orphanage`.
- Read-only filesystems skip creation.
- `xrep_chown_orphanage` makes the orphanage root-owned, clears setuid/setgid/sticky and realtime inheritance flags, and updates quota ownership.

## Locking Helpers
- `xrep_orphanage_ilock`, `xrep_orphanage_ilock_nowait`, and `xrep_orphanage_iunlock` track orphanage lock state in the scrub context.
- `xrep_orphanage_iolock_two` repeatedly trylocks orphanage and scrub target IOLOCKs to avoid blocking while a scrub transaction exists.
- `xrep_orphanage_rele` releases locks and inode references.

## Adoption
- `xrep_orphanage_can_adopt` excludes the orphanage itself, superblock-rooted inodes, and internal inodes.
- `xrep_adoption_trans_alloc` reserves space, locks orphanage and child, joins both inodes, and reserves quota with repair override semantics.
- `xrep_adoption_compute_name` chooses a unique orphanage name based on inode number with numeric suffix fallback.
- `xrep_adoption_move` creates the orphanage dirent, bumps link counts as needed, updates child `..` for directories, adds parent pointers when enabled, emits dirent hook notifications, and invalidates relevant dentries.
- `xrep_adoption_trans_roll` finishes deferred work and rolls to a clean transaction.

## Risk Points
- Dcache checks guard against disagreement between the locked ondisk directory and VFS lookup state.
- Parent-pointer filesystems may need attr fork creation before adoption.
- Adoption returns with a dirty transaction so callers can combine it with other metadata fixes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/orphanage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/orphanage.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/orphanage.h

## Role
Declares orphanage and adoption interfaces for online repair.

## Repair-Enabled API
- `xrep_orphanage_create` creates/attaches `/lost+found`.
- `xrep_orphanage_try_create` tolerates absent, non-directory, or no-space orphanage failures so repair can continue without adoption.
- Lock helpers manage orphanage IOLOCK/ILOCK state.
- `xrep_orphanage_rele` drops orphanage references.

## Adoption State
- `struct xrep_adoption` tracks scrub context, chosen name, parent-pointer args, block reservations, and whether to bump the child link count.
- Adoption helpers allocate the transaction, compute a unique name, move the file, and roll the transaction.

## Non-Repair Build
When `CONFIG_XFS_ONLINE_REPAIR` is disabled, adoption is an empty structure and orphanage release is a no-op.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/orphanage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/parent.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/parent.c

## Role
Scrubs parent relationships for XFS inodes. On older filesystems it validates directory `..`; on parent-pointer filesystems it validates xattr parent pointers against forward directory entries.

## Setup
- `xchk_setup_parent` prepares repair if available and sets up inode contents scrub.

## Legacy `..` Validation
- `xchk_parent` rejects non-directories when parent pointers are absent.
- It looks up `..`, validates root/metadir self-parent rules, and checks that the alleged parent directory has exactly the expected dirent pointing back.
- `xchk_parent_validate` handles invalid parent inode numbers, corrupt parent inodes, non-directory parents, zapped directories, and metadata/regular tree crossing.

## Parent Pointer Scrub
- `xchk_parent_pptr` walks parent-pointer xattrs with `xchk_xattr_walk`.
- `xchk_parent_scan_attr` parses each parent record, rejects self-parent pointers, validates parent inode/generation/type, and checks the forward dirent.
- Parent pointers that cannot be checked due to trylock failure are stashed in `xfarray`/`xfblob`.

## Slow Path
- `xchk_parent_finish_slow_pptrs` replays deferred parent pointers.
- `xchk_parent_slow_pptr` revalidates xattrs after lock cycling so stale removed parent pointers are not reported as corruption.
- `xchk_dir_trylock_for_pptrs` is used when the normal fast trylock path fails.

## Directory Consistency
- `xchk_parent_pptr_and_dotdot` verifies a linked directory’s `..` matches at least one parent pointer.
- `xchk_parent_count_pptrs` compares parent-pointer count to link count, with special handling for roots, unlinked directories, and superblock-rooted metadir children.

## Zapped Attr Detection
- `xchk_pptr_looks_zapped` detects missing or reset attr forks that imply parent pointers were zapped by inode repair and should be postponed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/parent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/parent_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/parent_repair.c

## Role
Repairs directory parent metadata. Without parent pointers it repairs `..`; with parent pointers it rebuilds the target inode’s parent-pointer xattrs from live directory entries using a temporary file and atomic attr-fork exchange.

## Setup
- `xrep_setup_parent` enables dirent fsgates, allocates `struct xrep_parent`, creates a repair tempfile, and tries to attach the orphanage.
- Parent-pointer repair requires rmapbt and exchange-range support.

## Legacy Repair
- `xrep_parent_find_dotdot` avoids sick directories, tries self-reference and dcache parent discovery, then scans the filesystem if needed.
- `xrep_parent_reset_dotdot` replaces the target directory’s `..` entry with the discovered parent inode.

## Parent-Pointer Rebuild
- `xrep_parent_scan_dirtree` scans all directories for dirents pointing to the scrub target.
- `xrep_parent_scan_dirent` converts each matching dirent into a stashed parent-pointer add operation.
- `xrep_parent_live_update` captures concurrent dirent adds/removes that affect already scanned directories.
- Stashed parent-pointer operations are periodically replayed into the tempfile to cap memory use.

## Xattr Preservation
- Non-parent xattrs are copied from the target inode into the tempfile.
- Large/remote xattr values are fetched as needed.
- If parent-pointer updates occur while opportunistically flushing copied attrs, the copy restarts with stronger locking.

## Commit Path
- `xrep_parent_finalize_tempfile` replays all pending pptr updates, ensures both inodes have attr forks, allocates exchange transaction resources, and locks both files.
- `xrep_parent_rebuild_pptrs` swaps the rebuilt attr fork into the target and resets the tempfile fork.
- Files with no parent can be moved to the orphanage; metadir superblock-rooted children are exempt.
- For non-directories, `xrep_parent_set_nondir_nlink` resets link counts and unlinked-list membership from rebuilt parent pointers.

## Risk Points
- Repair intentionally drops locks during full filesystem scans and relies on hooks for correctness.
- The pptr replay loop must finish with no queued updates before attr-fork exchange.
- If adoption cannot be performed for an otherwise parentless linked file, repair reports corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/parent_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quota.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/quota.c

## Role
Scrubs one quota type’s quota inode and dquot records.

## Setup
- `xchk_quota_to_dqtype` maps scrub type to user, group, or project quota type.
- `xchk_setup_quota` verifies quotas are enabled, installs the quota inode as the live inode, sets up filesystem scrub state, and takes the quota inode ILOCK.

## Quota File Checks
- `xchk_quota_data_fork` runs metadata inode fork checks, then rejects unwritten/delalloc extents and mappings beyond the maximum dquot id range.
- `xchk_quota_item_bmap` verifies each dquot’s file offset, backing mapping, disk address, and written extent state.

## Dquot Checks
- `xchk_quota_item` checks dquot id ordering, bmap backing, soft/hard limit consistency, physical count sanity, inode count sanity, and timer state.
- Hard limits larger than filesystem size and usage over hard limits are warnings in cases administrators can create.
- On reflink filesystems, block usage can exceed physical blocks without being immediate corruption.

## Top-Level Flow
- `xchk_quota` checks the quota inode first, drops ILOCK_EXCL, iterates dquots with `xchk_dquot_iter`, and stops early on corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quota.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/quota.h

## Role
Declares quota scrub helpers and the dquot iterator state.

## API
- `xchk_quota_to_dqtype` maps scrub type to dquot type.
- `xchk_dqiter_init` initializes quota-file iteration.
- `xchk_dquot_iter` returns referenced dquots one at a time.

## Iterator State
`struct xchk_dqiter` tracks scrub context, quota inode, cached bmap, next id, quota type, and data-fork sequence number used to detect stale mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quota_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/quota_repair.c

## Role
Repairs quota inode mappings, dquot verifier failures, and dquot fields that quota scrub can identify as nonsensical.

## Dquot Mapping Repair
- `xrep_quota_item_bmap` computes the correct quota-file offset, fills holes/delalloc with real initialized quota blocks, rejects unwritten extents, and updates cached disk addresses.
- `xrep_quota_item_fill_bmap_hole` allocates quota-file blocks, initializes a dquot chunk, and rolls the transaction.

## Dquot Field Repair
- `xrep_quota_item` clamps soft limits to hard limits.
- Counts beyond physical filesystem limits are capped where valid and mark `need_quotacheck`.
- Timers are normalized through quota timer adjustment before logging dirty dquots.

## Disk Block Repair
- `xrep_quota_block` rereads verifier-failing quota blocks without ops, rewrites magic/version/type/id, fixes timers, updates UUID/checksum/LSN, sets buffer type, and logs the block.

## Quota File Repair
- `xrep_quota_data_fork` repairs metadata inode forks, converts unwritten extents, truncates mappings beyond max dquot id, cancels CoW reservations, and fixes quota blocks.
- `xrep_quota_problems` iterates dquots and forces a future quotacheck if counters were suspect.

## Top-Level Flow
- `xrep_quota` repairs the quota inode under ILOCK_EXCL, finishes deferred work, unlocks the inode, fixes dquots, and commits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quota_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quotacheck.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/quotacheck.c

## Role
Implements live quotacheck: recomputes quota counters from every inode and compares the results to incore dquots.

## Setup
- `xchk_setup_quotacheck` requires quotas to be enabled, enables quota fsgates, allocates `struct xqcheck`, and sets up filesystem scrub state.
- `xqcheck_setup_scan` creates sparse counter arrays for active quota types, initializes a transaction shadow-accounting hash, installs quota transaction hooks, and sets deferred cleanup.

## Live Update Hooks
- `xqcheck_mod_live_ino_dqtrx` records quota deltas made to already scanned inodes in per-transaction shadow state.
- `xqcheck_apply_live_dqtrx` applies those shadow deltas to the recomputed counters when the real quota code commits and frees transaction shadow state.
- Hook errors abort the iscan to force `INCOMPLETE`.

## Collection
- `xqcheck_collect_counts` walks all allocated inodes with an empty transaction.
- `xqcheck_collect_inode` skips metadata/quota inodes, locks data state, counts data and realtime blocks, then increments user/group/project shadow counters for the inode’s ids.
- Realtime inodes load data fork mappings so realtime blocks can be counted accurately.

## Comparison
- `xqcheck_compare_dquot` compares observed inode, data block, and realtime block counts to a dquot.
- `xqcheck_compare_dqtype` first checks quota `CHKD` flags, iterates known dquots, then checks observed dquots that were not in the quota file.
- Missing incore dquots for observed ids are corruption.

## Risk Points
- The apply hook must be removed after the mod hook to avoid leaking shadow transaction state.
- Partial scans cannot be used for repair.
- Comparison handles all active quota types independently.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quotacheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quotacheck.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/quotacheck.h

## Role
Defines live quotacheck data structures shared by scrub and repair.

## Structures
- `struct xqcheck_dquot` holds recomputed block, inode, and realtime block counts plus state flags.
- `struct xqcheck` holds scrub context, per-type sparse counter arrays, mutex, iscan, quota hooks, and transaction shadow-accounting hash table.

## Flags
- `XQCHECK_DQUOT_WRITTEN` marks initialized counter records.
- `XQCHECK_DQUOT_COMPARE_SCANNED` marks records compared by scrub.
- `XQCHECK_DQUOT_REPAIR_SCANNED` marks records repaired.

## Helper
- `xqcheck_counters_for` returns the appropriate sparse counter array for a quota type.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quotacheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quotacheck_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/quotacheck_repair.c

## Role
Repairs quota counters using live quotacheck observations left active from scrub.

## Dquot Commit
- `xqcheck_commit_dquot` allocates a transaction, locks and joins the dquot, loads observed counters, adjusts reserved/count fields by deltas, updates timers, logs the dquot, and commits if dirty.
- Records are marked `XQCHECK_DQUOT_REPAIR_SCANNED`.

## Quota-Type Commit
- `xqcheck_commit_dqtype` first repairs every dquot known to the quota file.
- A second pass walks observed sparse records and creates missing dquots with `xfs_qm_dqget(..., true)` before committing counters.

## CHKD Flags
- `xqcheck_chkd_flags` computes active quota check flags.
- `xrep_quotacheck` clears CHKD flags before repair so a crash forces mount-time quotacheck, then restores them after all counters are committed.

## Risk Points
- Repair aborts if the original live scan was aborted.
- Creating missing dquots may allocate quota blocks in separate transactions.
- Crash safety relies on clearing CHKD before counter rewrites.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/quotacheck_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag.c

## Role
Implements a refcount bag: an in-memory btree-backed multiset of reverse-mapping extents used to compute sharing/refcount transitions.

## Lifecycle
- `rcbag_init` allocates a bag and initializes an in-memory `xfbtree`.
- `rcbag_free` destroys the tree and clears the caller’s pointer.

## Operations
- `rcbag_add` inserts an rmap extent or increments the record refcount if the same start/length already exists.
- `rcbag_count` returns the total item count, including duplicate refcounts.
- `rcbag_next_edge` finds the next block where refcount state can change, considering both the next incoming rmap and tracked bag entries ending.
- `rcbag_remove_ending_at` deletes all records ending at a specified block and decrements item count by their refcounts.
- `rcbag_dump` emits diagnostic records.

## Risk Points
- Every mutation commits or cancels the backing `xfbtree` transaction.
- Tree cursor failures are treated as corruption because this is repair scratch state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag.h

## Role
Declares the public refcount-bag API.

## API
- Lifecycle: `rcbag_init`, `rcbag_free`.
- Mutation/query: `rcbag_add`, `rcbag_count`.
- Sweep helpers: `rcbag_next_edge`, `rcbag_remove_ending_at`.
- Diagnostics: `rcbag_dump`.

## Integration
The API is intentionally opaque: callers see `struct rcbag` but not the in-memory btree internals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.c

## Role
Defines the in-memory btree implementation backing `rcbag`.

## Btree Format
- Records contain start block, block count, and refcount.
- Keys contain start block and block count.
- Ordering is lexicographic by start block then block count.
- Uses XFS in-memory btree (`xfbtree`) operations and buffer verification.

## Cursor and Ops
- `rcbagbt_mem_ops` supplies XFS btree callbacks for key/record conversion, comparison, ordering, block allocation, and root management.
- `rcbagbt_mem_cursor` allocates a memory btree cursor from a slab cache.
- `rcbagbt_mem_init` initializes the in-memory btree.

## Geometry
- `rcbagbt_maxrecs`, `rcbagbt_maxlevels_possible`, and `rcbagbt_calc_size` compute btree capacity and space needs.
- Verifiers use `RCBAG_MAGIC` and memory btree block checks.

## Record Helpers
- `rcbagbt_lookup_eq` positions by rmap start/length.
- `rcbagbt_get_rec`, `rcbagbt_update`, and `rcbagbt_insert` wrap generic XFS btree record operations.

## Lifecycle
- `rcbagbt_init_cur_cache` and `rcbagbt_destroy_cur_cache` manage the cursor slab cache.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.h

## Role
Declares the refcount-bag in-memory btree format and helper functions.

## Format
- `RCBAG_MAGIC` identifies in-memory refcount bag btree blocks.
- `struct rcbag_key` indexes records by start block and block count.
- `struct rcbag_rec` stores start block, block count, and accumulated refcount.
- Address macros compute record, key, and pointer locations in btree blocks.

## API
- Geometry helpers: `rcbagbt_maxrecs`, `rcbagbt_calc_size`, `rcbagbt_maxlevels_possible`.
- Cache lifecycle: `rcbagbt_init_cur_cache`, `rcbagbt_destroy_cur_cache`.
- Memory btree setup: `rcbagbt_mem_cursor`, `rcbagbt_mem_init`.
- Record operations: lookup, get, update, insert.

## Build Guards
When in-memory btrees are disabled, init/destroy degrade to no-op/success macros.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rcbag_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/readdir.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/readdir.c

## Role
Provides scrub-side directory iteration, directory lookup, and parent-pointer lock helpers.

## Directory Walking
- `xchk_dir_walk` dispatches by directory format.
- `xchk_dir_walk_sf` synthesizes `.` and `..` entries and iterates shortform entries.
- `xchk_dir_walk_block` reads block-format directories and reports non-free data entries.
- `xchk_dir_walk_leaf` scans mapped data blocks below the leaf offset for leaf/node directories.

## Lookup
- `xchk_dir_lookup` performs exact name lookup using XFS directory args and returns the target inode number.
- For repair temp directories, it substitutes the scrub target as owner because temp directory block headers use that owner.

## Lock Helper
- `xchk_dir_trylock_for_pptrs` attempts to lock scrub target and peer inode with IOLOCK/ILOCK ordering suitable for uncertain/corrupt directory trees.
- It returns success, retry/deadlock, timeout with `INCOMPLETE` under `TRY_HARDER`, or interruption.

## Assumptions
- Callers must hold the directory ILOCK for walking and lookup.
- Callback file types are XFS directory filetype values.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/readdir.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/readdir.h

## Role
Declares directory walking and lookup helpers for scrub and repair.

## API
- `xchk_dirent_fn` is the callback signature for directory entries.
- `xchk_dir_walk` iterates all entries of a locked directory.
- `xchk_dir_lookup` resolves a name in a locked directory.
- `xchk_dir_trylock_for_pptrs` performs bounded locking for parent-pointer checks.

## Integration
Used by directory scrub, parent-pointer scrub/repair, nlink checks, and orphanage adoption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/readdir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/reap.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/reap.c

## Role
Disposes of old metadata blocks after online repair constructs replacement metadata. It handles AG metadata, file metadata, metadir metadata, CoW staging extents, realtime CoW extents, and complete inode forks.

## Core State
- `struct xreap_state` carries scrub context, owner information or inode/fork, buffer invalidation counts, and deferred-intent limits.
- Limit helpers throttle buffer invalidation and deferred work so transactions do not exceed log reservations.

## Buffer Scanning
- `xrep_bufscan_max_sectors` and `xrep_bufscan_advance` search for incore buffers of plausible sizes.
- Reap invalidates buffers before freeing blocks when it believes no other owner remains.
- Oversized/non-loggable file buffers are staled directly instead of logged.

## AG/FS Metadata Reap
- `xreap_agextent_select` uses rmapbt to split extents into crosslinked and non-crosslinked runs.
- `xreap_agextent_iter` removes rmaps for crosslinked blocks or frees single-owner blocks.
- CoW extents use refcount cleanup; AGFL blocks are returned one at a time.
- `xrep_reap_agblocks` and `xrep_reap_fsblocks` walk bitmaps and finish deferred work.

## Realtime Reap
- Under `CONFIG_XFS_RT`, realtime CoW extents are split by realtime rmap crosslink state.
- `xrep_reap_rtblocks` locks realtime group bitmap/rmap/refcount state and frees or unmaps CoW extents.

## Metadir Reap
- `xrep_reap_metadir_fsblocks` reaps old metadir btree blocks with regular AG reservation semantics and then resets metafile reservation accounting.

## Inode Fork Reap
- `xrep_reap_ifork` walks every real mapping in an inode fork and removes it.
- `xreap_bmapi_select` determines crosslink status using rmap owner including file offset.
- Crosslinked mappings are unmapped from the fork and rmap only; non-crosslinked mappings also invalidate buffers and free space.
- Quota block counts are adjusted during fork unmap.

## Risk Points
- Reap intentionally cannot fix all possible buffer-cache aliasing crosslinks.
- Crash during very large reap chains can leak blocks, so deferral chains are periodically finished.
- Requires rmapbt for ownership/crosslink decisions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/reap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/reap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/reap.h

## Role
Declares block and fork reaping interfaces for online repair.

## Reap API
- `xrep_reap_agblocks` disposes per-AG extents from an AG bitmap.
- `xrep_reap_fsblocks` disposes filesystem block extents from an fsblock bitmap.
- `xrep_reap_ifork` removes all mappings from a scrub target or tempfile fork.
- `xrep_reap_metadir_fsblocks` handles old metadir metadata blocks.
- `xrep_reap_rtblocks` handles realtime extents when realtime support is enabled, otherwise returns `-EOPNOTSUPP`.

## Buffer Scan API
- `struct xrep_bufscan` tracks daddr, maximum scan length, step size, and internal sector count.
- `xrep_bufscan_max_sectors` computes a bounded scan range.
- `xrep_bufscan_advance` returns matching incore buffers during reap invalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/reap.h -->