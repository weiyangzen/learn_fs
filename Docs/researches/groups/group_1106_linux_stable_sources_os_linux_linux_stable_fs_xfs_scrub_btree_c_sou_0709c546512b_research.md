# Group Research: group_1106_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_btree_c_sou_0709c546512b

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/btree.c

## Purpose
Implements the generic online scrub walker for XFS btrees. It traverses any regular XFS btree through a supplied cursor, validates tree shape and ordering invariants, checks block ownership, and dispatches each leaf record to a caller-provided record checker.

## Main Entry Points
- `xchk_btree`: allocates walker state, descends from the root, validates every node/leaf, invokes the record callback, and performs deferred owner checks.
- `xchk_btree_process_error` / `xchk_btree_xref_process_error`: normalize btree operation errors into scrub corruption or xref failure flags.
- `xchk_btree_set_corrupt`, `xchk_btree_xref_set_corrupt`, `xchk_btree_set_preen`: record scrub outcomes with btree-aware tracepoints.

## Key Behavior
The walker validates pointer sanity with `__xfs_btree_check_ptr`, loads blocks through `xfs_btree_lookup_get_block`, reruns buffer structure verifiers, checks minimum record counts, validates sibling links against adjacent parent pointers, and confirms parent keys cover child key ranges. Leaf records are checked for global ordering and parent low/high-key containment; node keys receive similar ordering and parent-bound checks.

Ownership checks cross-reference btree blocks against used-space and rmap ownership metadata. For bnobt and rmapbt, checks are deferred until after traversal because the tree being scrubbed can alias the cross-reference cursor.

## Notable Details
Inode-rooted btrees are handled specially because the root can be in-core rather than buffer-backed. The code preserves compatibility with old data-fork bmap root spill behavior when an attr fork exists. Overlapping-key btrees receive additional high-key validation.

## Failure Handling
Verifier errors and I/O/corruption returns set scrub flags and usually clear the errno so scrub can report bad metadata instead of failing as an operation. Runtime errors such as allocation failure propagate. Traversal stops early on corruption, fatal signal termination, or callback failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/btree.h

## Purpose
Declares the generic btree scrub interface and its traversal state.

## API
- `xchk_btree`: generic btree traversal and validation entry point.
- `xchk_btree_process_error` and `xchk_btree_xref_process_error`: btree operation error handling.
- `xchk_btree_set_corrupt`, `xchk_btree_xref_set_corrupt`, `xchk_btree_set_preen`: btree-specific outcome flag helpers.
- `xchk_btree_sizeof`: computes the allocation size for per-level key tracking.

## Key Structures
`struct xchk_btree` stores the scrub context, btree cursor, record callback, owner information, callback-private data, previous leaf record, deferred owner-check list, and a flexible array of previous keys for internal levels.

## Notes
The callback type `xchk_btree_rec_fn` lets individual scrubbers supply btree-specific leaf record validation while reusing the common traversal and structural checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/common.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/common.c

## Purpose
Provides shared infrastructure for XFS online scrub and repair setup. It centralizes error normalization, scrub flag reporting, transaction management, AG/realtime group locking, btree cursor setup, inode lookup, inode locking, cross-reference gating, buffer verifier reruns, metadata inode checks, and filesystem gate enabling.

## Main Entry Points
- Error processors: `xchk_process_error`, `xchk_process_rt_error`, `xchk_xref_process_error`, `xchk_fblock_process_error`, `xchk_fblock_xref_process_error`.
- Flag reporters: `xchk_set_corrupt`, `xchk_block_set_corrupt`, `xchk_ino_set_corrupt`, `xchk_fblock_set_corrupt`, xref variants, preen variants, warning variants, and `xchk_set_incomplete`.
- AG helpers: `xchk_ag_read_headers`, `xchk_perag_drain_and_lock`, `xchk_ag_btcur_init`, `xchk_ag_init`, `xchk_ag_free`.
- Realtime helpers: `xchk_rtgroup_init`, `xchk_rtgroup_lock`, `xchk_rtgroup_btcur_free`, `xchk_rtgroup_unlock`, `xchk_rtgroup_free`.
- Transaction/setup helpers: `xchk_trans_alloc`, `xchk_setup_fs`, `xchk_setup_rt`, `xchk_setup_ag_btree`, `xchk_checkpoint_log`.
- Inode helpers: `xchk_iget`, `xchk_iget_agi`, `xchk_iget_for_scrubbing`, `xchk_install_live_inode`, `xchk_install_handle_inode`, `xchk_irele`, `xchk_setup_inode_contents`.
- Validation helpers: `xchk_should_check_xref`, `xchk_buffer_recheck`, `xchk_metadata_inode_forks`, `xchk_inode_is_allocated`, `xchk_inode_count_blocks`.

## Key Behavior
Operational verifier errors such as bad CRC, filesystem corruption, I/O, or missing data are converted into scrub outcome flags, while runtime errors propagate. Cross-reference failures are isolated from the primary scrub by dropping broken xref cursors and setting `XFAIL`.

AG setup takes perag references, reads AGI/AGF headers in lock order, waits for deferred intent chains to drain when necessary, and initializes allocation, inode, rmap, and refcount btree cursors. Realtime setup performs analogous rtgroup locking and cursor initialization under `CONFIG_XFS_RT`.

Inode setup handles untrusted inode numbers carefully: it first tries a safe transaction-wrapped iget, then locks AGI and consults inobt state to distinguish missing/free inodes from corrupt allocated inodes. `xchk_setup_inode_contents` coordinates inode locks, repair transaction sizing, and quota attachment.

## Notable Details
`xchk_buffer_recheck` reruns in-memory buffer structure verifiers to catch bad buffers after read-time verification. Metadata inode fork scrub rejects realtime placement and reflink participation, and delegates inode/data/attr fork checks through subordinate scrub contexts. `xchk_inode_is_allocated` uses incore inode state under AGI protection to resolve allocation status more accurately than stale ondisk buffers.

## Failure Handling
The file defines the scrubber contract: metadata corruption is reported through scrub flags, not usually through errno; incomplete or unavailable xref metadata does not abort the primary check; deadlock-avoidance codes are left for higher-level retry logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/common.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/common.h

## Purpose
Declares shared scrub setup, error handling, resource management, inode handling, xref, and helper APIs used across XFS scrub modules.

## API Surface
Includes transaction helpers, all common error processors, corrupt/preen/warning flag helpers, setup functions for filesystem, AG, realtime, inode, directory, xattr, symlink, parent, dirtree, quota, counters, and link-count scrubbers.

## Key Definitions
- `xchk_setup_nothing`: disabled-feature setup fallback.
- `xchk_ag_init_existing` and `xchk_rtgroup_init_existing`: treat missing referenced groups as corruption.
- `XCHK_RTGLOCK_ALL`: aggregate realtime metadata lock mask.
- `xchk_iget_safe`: safe transaction-wrapped untrusted inode lookup.
- `xchk_skip_xref`: suppresses xref after primary corruption or xref corruption.
- `xchk_needs_repair` and `xchk_could_repair`: repair decision predicates.
- `xchk_need_intent_drain`: identifies when the expensive intent-drain gate was needed.

## Notes
The header is the central dependency surface for individual scrubbers. Quota and realtime APIs compile to safe no-op or unsupported fallbacks when features are absent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/cow_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/cow_repair.c

## Purpose
Repairs an inode’s in-core CoW fork mappings by replacing bad unwritten CoW staging extents with freshly allocated staging space, then reaping the discarded old blocks.

## Main Entry Points
- `xrep_bmap_cow`: top-level CoW fork repair entry point.
- `xrep_cow_find_bad` / `xrep_cow_find_bad_rt`: detect bad CoW staging extents in regular and realtime storage.
- `xrep_cow_replace`: walks bad file-offset ranges and replaces them.
- `xrep_cow_replace_range`: allocates replacement space and splices it into the CoW fork.

## Key Behavior
Repair scans CoW fork extent mappings and ignores delalloc reservations because they exist only in memory. It also ignores written CoW extents because writeback can already be in flight. For unwritten mappings, it checks refcount records for shared or missing CoW-domain staging records and rmap records for non-CoW ownership. Bad physical ranges are translated into a file-offset bitmap.

Replacement allocates regular or realtime extents, records CoW staging ownership in refcount metadata, updates the in-core CoW fork extent list, finishes deferred work, records old blocks in a bitmap, and finally reaps them as CoW-owned metadata blocks.

## Constraints
Requires rmapbt and reflink. Big realtime allocation units are unsupported because partially written CoW mappings cannot safely be relocated. Metadata inodes on realtime storage are rejected.

## Failure Handling
The code is conservative because ondisk metadata does not directly identify CoW fork ownership. It only replaces unwritten mappings proven or forced to be unsafe. Unsupported feature combinations return `-EOPNOTSUPP`; inconsistent current mappings return corruption errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/cow_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dab_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dab_bitmap.h

## Purpose
Provides a type-checked bitmap wrapper for XFS directory/attribute block numbers.

## API
- `struct xdab_bitmap`: wraps `struct xbitmap32`.
- `xdab_bitmap_init`
- `xdab_bitmap_destroy`
- `xdab_bitmap_set`
- `xdab_bitmap_test`

## Notes
The wrapper keeps DA block-number users from directly manipulating generic 32-bit bitmap units, reducing accidental type mixups in scrub/repair code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dab_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.c

## Purpose
Implements a generic scrub walker for XFS directory/attribute btrees. It validates DA tree blocks, hashes, ownership, sibling links, parent hash coverage, and dispatches leaf records to directory or attribute-specific validators.

## Main Entry Points
- `xchk_da_btree`: generic DA btree traversal entry point.
- `xchk_da_btree_hash`: validates hash ordering and parent hash bounds.
- `xchk_da_process_error`, `xchk_da_set_corrupt`, `xchk_da_set_preen`: DA-specific error and outcome handling.

## Key Behavior
The walker skips short format forks, allocates `xfs_da_state`, identifies the root block, and descends node blocks until it reaches leaf blocks. For directories, valid node/leaf blocks must live between the directory leaf and free block regions; attribute forks have no such DA block limit.

Block loading uses a custom verifier multiplexer because directory `leaf1` blocks are treated as degenerate DA leaves even though normal DA code does not handle them. Loaded blocks are checked for padding, owner, sibling consistency, magic normalization, header validity, tree-level consistency, and parent hash match.

## Notable Details
The code supports attr leaf, dir leafn, dir leaf1, and DA node blocks. CRC filesystems get additional padding checks, with node `__pad32` drift marked preen.

## Failure Handling
Directory data forks without a DA root at the expected location are treated as having no tree. Attribute forks missing an expected DA block are corrupt. Verifier errors set scrub corruption flags and stop local traversal without necessarily returning hard errno.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.h

## Purpose
Declares the generic directory/attribute btree scrub interface and walker state.

## Key Structures
`struct xchk_da_btree` stores DA args, per-level last hashes, per-level maximum records, DA state paths, scrub context, callback-private data, expected DA block range, and current tree level.

## API
- `xchk_da_btree`: walk and validate a directory or attribute DA btree.
- `xchk_da_btree_hash`: validate a DA hash at a level.
- `xchk_da_process_error`, `xchk_da_set_corrupt`, `xchk_da_set_preen`: DA scrub helpers.
- `xchk_da_btree_rec_fn`: callback type for leaf record validation.

## Notes
The header contains a duplicated `xchk_da_set_preen` prototype, which is harmless. It is shared by directory and attribute scrubbers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dir.c

## Purpose
Implements XFS directory scrub. It validates directory DA btree entries, directory data and free-space accounting blocks, dirent name and inode consistency, ftype values, parent pointers, and zapped-directory state.

## Main Entry Points
- `xchk_setup_directory`: prepares directory scrub and optional repair setup.
- `xchk_directory`: top-level directory scrub.
- `xchk_dir_rec`: validates directory leaf records against data blocks and name hashes.
- `xchk_directory_blocks`: validates directory data, leaf1, and free-space summary blocks.
- `xchk_dir_actor`: validates each dirent encountered by `xchk_dir_walk`.
- `xchk_dir_looks_zapped`: detects directories whose data fork was reset by repair.

## Key Behavior
Directory scrub first rejects non-directories and zapped data forks, checks plausible size, then runs generic DA btree scrub for leaf records. It validates data block bestfree arrays, leaf1 bestfree tails, free block best arrays, stale counts, hash ordering, and directory block layout.

The full dirent walk verifies inode numbers, names, dot and dotdot semantics, hash lookup consistency, child inode lookup, ftype matching, and metadata-tree separation. On parent-pointer filesystems, it checks that every non-dot dirent has a matching child parent pointer.

## Locking and Deferred Checks
Child parent-pointer validation first tries nonblocking child IOLOCK/ILOCK acquisition. If locking fails, the dirent name and target inode are stored in `xfarray`/`xfblob` and revisited later. The slow path may cycle locks, revalidate the dirent, and then check parent pointers.

## Failure Handling
Dirent corruption often returns `-ECANCELED` internally to stop walking after setting scrub flags; the top-level scrub converts that to success with corruption flags set. Parent-pointer xref failures are reported as xref corruption or xref failure rather than primary directory corruption unless the primary dirent itself is bad.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dir_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dir_repair.c

## Purpose
Repairs damaged XFS directory contents by constructing a replacement directory in a temporary inode and atomically exchanging its data fork with the target directory. It supports two reconstruction strategies: direct dirent salvage and parent-pointer-driven reconstruction.

## Main Entry Points
- `xrep_setup_directory`: enables directory update gates, creates orphanage/tempdir resources, and allocates repair state.
- `xrep_directory`: top-level directory repair.
- `xrep_dir_salvage_entries`: finds the parent and salvages entries from the damaged directory when parent pointers are absent.
- `xrep_dir_scan_dirtree`: scans the filesystem for parent pointers and relevant child dirents when parent pointers exist.
- `xrep_dir_rebuild_tree`: finalizes the tempdir and exchanges it into place.
- `xrep_dir_swap`: updates dotdot, prepares fork formats, sets nlink, and performs the atomic exchange.

## Key Behavior
Without parent pointers, repair finds the parent through self-reference, dcache, dotdot lookup, or full scan, then parses shortform or data-format directory blocks to salvage plausible non-dot entries. Names are truncated at invalid bytes, entries are kept only if inode numbers and names are plausible, target inode type can be read, and metadata/regular trees do not mix.

With parent pointers, repair scans all files. Parent-pointer xattrs pointing back to the target become replacement dirents; child dirents pointing to the target identify the new dotdot parent. Live dirent hooks record concurrent updates so the tempdir remains current while the scan runs.

Stashed dirent updates are held in `xfarray`/`xfblob` and periodically replayed into the tempdir to bound memory use. Finalization replays remaining updates, allocates exchange resources, promotes local forks if needed, exchanges data forks, resets the tempfile directory, fixes nlink from observed subdirectories, and moves parentless linked directories to the orphanage.

## Requirements
Requires rmapbt for reaping old directory blocks and exchange-range support for atomic replacement. Parent-pointer filesystems rely on directory hooks and inode scans to rebuild from authoritative parent metadata.

## Failure Handling
Repair aborts before committing if termination is requested. Busy/zapped files during scans can force cancellation to userspace. If no parent can be found, repair temporarily points dotdot to root and then adopts the directory into the orphanage if possible.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dir_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.c

## Purpose
Validates XFS directory tree structure using parent pointers. It walks every parent-pointer path from a directory upward toward the root to detect cycles, disconnected directories, multiple parents, corrupt ancestors, and stale scan results under concurrent updates.

## Main Entry Points
- `xchk_setup_dirtree`: prepares directory-tree scrub resources and optional repair setup.
- `xchk_dirtree`: top-level dirtree scrub.
- `xchk_dirtree_find_paths_to_root`: builds and walks all parent-pointer paths.
- `xchk_dirpath_append`: records a path step in the in-core arrays.
- `xchk_dirtree_evaluate`: summarizes path outcomes.
- `xchk_dirtree_parentless`: identifies roots or unlinked directories that should not have parents.

## Key Behavior
The scanner creates one `xchk_dirpath` per parent pointer on the target directory. For each path, it revalidates the starting parent pointer, drops the target ILOCK while retaining IOLOCK, and steps upward through parent directories. Each step validates generation numbers, directory type, nonzero nlink, same regular/metadata tree, absence of zapped parent-pointer state, and uniqueness.

Outcomes include good path to root, direct self-parent requiring deletion, loop above the target, corrupt path, stale path, or repair in-progress states. The top-level checker treats parentless directories differently from linked directories: roots/unlinked dirs should have no paths, while normal directories should have exactly one usable path.

## Concurrency Model
The scrubber registers a directory update hook. Path steps store child/parent/name data; live dirent updates touching any scanned step mark the scan stale. Stale scans are discarded and retried, while hook errors mark the scan incomplete.

## Failure Handling
Corrupt direct parent pointers mark xref corruption and stop meaningful path checking. Zapped parent-pointer metadata marks the scrub incomplete. Excessive path count or path depth is treated as severe corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.h

## Purpose
Declares data structures and APIs for directory tree validation and repair.

## Key Structures
- `struct xchk_dirpath_step`: one upward parent-pointer step, including dirent name cookie/length and parent pointer record.
- `enum xchk_dirpath_outcome`: scanner and repair state machine for each path.
- `struct xchk_dirpath`: in-core tracked path, including first/second step indexes, seen-inode bitmap, path length, path number, and outcome.
- `struct xchk_dirtree_outcomes`: aggregate counts of bad, suspect, and good paths plus adoption need.
- `struct xchk_dirtree`: full scanner state, including root/scan/parent inode numbers, parent-pointer scratch args, adoption state, directory hook, path storage, name storage, path list, counters, stale flag, and abort flag.

## API
- `xchk_dirtree_parentless`
- `xchk_dirtree_find_paths_to_root`
- `xchk_dirpath_append`
- `xchk_dirtree_evaluate`

## Notes
The structure is shared by scrub and repair. Repair reuses the same path outcome state machine to decide which incoming directory links to delete and whether orphanage adoption is needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree_repair.c

## Purpose
Repairs directory tree structure problems found by `dirtree.c`. It deletes unwanted incoming directory links, resets dotdot to a surviving parent when necessary, and adopts orphaned directories into the orphanage.

## Main Entry Points
- `xrep_setup_dirtree`: ensures the orphanage exists.
- `xrep_dirtree`: top-level dirtree repair loop.
- `xrep_dirtree_decide_fate`: chooses which paths to keep, delete, or repair by adoption.
- `xrep_dirtree_fix_problems`: applies deletions and adoption.
- `xrep_dirtree_delete_path`: deletes a selected incoming path.
- `xrep_dirtree_move_to_orphanage`: reattaches a parentless directory.

## Key Behavior
Repair first evaluates path outcomes. Parentless directories delete all paths. A directory with exactly one good or suspect path keeps it. If multiple paths exist, repair keeps one good path if available; otherwise it keeps one suspect path and deletes the rest. If no usable path exists, it adopts the directory into the orphanage when possible.

Deleting a path locks the parent and child, allocates a remove transaction, marks the path as deleting, optionally resets the child dotdot entry to the retained parent or root, drops link counts, removes the parent dirent, removes the parent pointer, notifies dirent hooks, purges the VFS dentry, and commits.

Adoption creates a faux path so live-update tracking can observe the newly created orphanage entry, bumps child nlink because link-count repair has already run, and moves the directory to the orphanage with normal adoption helpers.

## Concurrency Model
Repair reuses dirtree stale detection. If a live update invalidates scan data during deletion or adoption, the operation returns `-ESTALE`; the top-level loop rescans paths and recomputes the repair plan.

## Failure Handling
Path depth/count overflow is converted to filesystem corruption. If orphanage adoption is required but unavailable, repair reports corruption. Transactions are canceled and locks reacquired to a consistent state on failure paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dqiterate.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dqiterate.c

## Purpose
Implements a quota dquot iterator for scrub/repair code. It walks both on-disk quota file mappings and incore dquot cache entries so scrub can visit dquots that exist on disk or only in memory.

## Main Entry Points
- `xchk_dqiter_init`: initializes the iterator for a quota type.
- `xchk_dquot_iter`: returns the next dquot or reports end/error.
- `xchk_dquot_iter_revalidate_bmap`: refreshes cached quota file mapping for the current id.
- `xchk_dquot_iter_advance_bmap`: skips holes to the next allocated quota file region.
- `xchk_dquot_iter_advance_incore`: finds the next incore dquot id from the radix tree.

## Key Behavior
The iterator maps dquot ids to quota file offsets using `qi_dqperchunk`. It caches a data fork mapping and revalidates it against the quota inode fork sequence. Sparse quota file holes are skipped by reading forward to the next real mapping. If on-disk iteration jumps forward, it also checks the incore dquot radix tree so dquots whose backing blocks were removed or have not yet been written are still returned.

## Locking
The quota inode data map is locked shared while validating or advancing file mappings. The incore radix tree is protected by `qi_tree_lock`.

## Failure Handling
Mapping gaps beyond `XFS_DQ_ID_MAX` end iteration. Missing mappings at unexpected places and impossible bmap states return corruption. `xfs_qm_dqget` is used to return a referenced dquot for the selected id.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/dqiterate.c -->