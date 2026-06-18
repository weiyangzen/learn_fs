# subset-b-005788 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.c

Purpose: Implements the generic XFS scrub walker for ordinary XFS btrees. It checks structural invariants that are common to AG btrees and inode-rooted btrees, including pointer validity, record/key ordering, parent key coverage, sibling linkage, minimum record counts, buffer verifier results, and ownership cross-references, then delegates record-specific validation to the caller.

Important APIs, types, and functions: The public entry point is `xchk_btree()`. Error and flag helpers are `xchk_btree_process_error()`, `xchk_btree_xref_process_error()`, `xchk_btree_set_corrupt()`, `xchk_btree_xref_set_corrupt()`, and `xchk_btree_set_preen()`. Internal validators include `xchk_btree_rec()`, `xchk_btree_key()`, `xchk_btree_ptr_ok()`, `xchk_btree_block_check_sibling()`, `xchk_btree_block_check_siblings()`, `xchk_btree_check_owner()`, `xchk_btree_check_block_owner()`, `xchk_btree_check_minrecs()`, `xchk_btree_block_check_keys()`, `xchk_btree_get_block()`, and `xchk_btree_block_keys()`. `struct check_owner` queues delayed owner checks for bnobt/rmapbt self-cross-references.

Control flow: `xchk_btree()` sizes and allocates a variable-length `struct xchk_btree`, initializes the root pointer from the cursor, loads the root block, and performs a manual depth-first traversal using `cur->bc_levels[level].ptr`. Leaf visits validate global record order, parent key containment, and invoke the caller's `scrub_rec` callback. Node visits validate key order, pointer bounds, child block headers, siblings, minrecs, parent keys, and buffer verifiers before descending. End-of-block handling pops toward the root and rechecks calculated block keys against parent keys.

State and persistence: The file does not persist data directly. It mutates scrub state by setting `sc->sm->sm_flags` (`CORRUPT`, `PREEN`, `XFAIL`, `XCORRUPT`) and traces btree failures. Traversal temporarily changes cursor level pointers and reads buffers through the transaction. For bno/rmap btrees, block-owner checks that would disturb the same cursor are deferred in `bs->to_check` until after the walk.

Dependencies and integration points: Depends on `xfs_btree_cur` operations for record/key comparison, pointer checks, block retrieval, sibling/key helpers, and cursor duplication. Cross-reference checks call `xchk_xref_is_used_space()` and `xchk_xref_is_only_owned_by()` through AG setup from `common.c`. It is shared by scrubbers for allocation, inode, rmap, refcount, bmap, and realtime-style btrees that can supply a record callback and owner info.

Risks and test signals: Risk concentrates around corrupt cyclic btrees, incorrect parent high-key logic for overlapping btrees, null-buffer handling for inode roots, cursor aliasing when scrubbing bnobt/rmapbt, and minrecs exceptions for historical bmap root spillover. Test with one-level and multi-level btrees, overlapping-key refcount/rmap forms, inode-rooted bmap btrees with attr forks, broken sibling pointers, invalid owners, missing rmaps, forced verifier errors, and callbacks that terminate early after setting corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.h

Purpose: Declares the common btree scrub interface used by XFS metadata scrubbers to walk a btree and validate generic structural invariants while allowing the caller to check records.

Important APIs, types, and functions: Exposes `xchk_btree_process_error()`, `xchk_btree_xref_process_error()`, `xchk_btree_set_corrupt()`, `xchk_btree_set_preen()`, `xchk_btree_xref_set_corrupt()`, and `xchk_btree()`. Defines callback type `xchk_btree_rec_fn`, `struct xchk_btree_key` for per-level last-key tracking, and `struct xchk_btree` for per-walk state. `xchk_btree_sizeof()` computes allocation size for `lastkey[]`.

Control flow: Callers initialize a normal `xfs_btree_cur` and invoke `xchk_btree()` with owner info, private callback data, and a record scrub function. The walker controls traversal and passes each leaf record to the callback via `struct xchk_btree`.

State and persistence: `struct xchk_btree` stores transient traversal state: scrub context, cursor, callback, owner information, private pointer, last leaf record, deferred owner checks, and last key per internal level. No persistent metadata layout is defined here.

Dependencies and integration points: Included by btree-specific scrubbers and by `btree.c`. It depends on XFS btree cursor types, owner info, scrub context, list handling, and kernel flexible-array allocation helpers.

Risks and test signals: The main ABI risk is that `lastkey[]` must remain last and be sized with `xchk_btree_sizeof(nlevels)`; callers that pass invalid cursors or levels can produce bad allocations or traversal state. Test by building scrubbers with one-level btrees, many-level btrees, and callback-private data under KASAN/UBSAN-style instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/common.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/common.c

Purpose: Provides shared infrastructure for XFS scrub and repair setup, error classification, flag reporting, AG and realtime group resource acquisition, inode lookup/locking, cross-reference gating, buffer re-verification, metadata-inode checks, filesystem hook activation, and small utility predicates used by many scrubbers.

Important APIs, types, and functions: Error processors include `xchk_process_error()`, `xchk_process_rt_error()`, `xchk_fblock_process_error()`, `xchk_xref_process_error()`, and `xchk_fblock_xref_process_error()`. Flag setters include block/inode/file offset `*_set_corrupt`, `*_xref_set_corrupt`, `*_set_preen`, warning setters, `xchk_qcheck_set_corrupt()`, and `xchk_set_incomplete()`. Setup and resource APIs include `xchk_trans_alloc()`, `xchk_setup_fs()`, `xchk_setup_rt()`, `xchk_setup_ag_btree()`, `xchk_ag_read_headers()`, `xchk_ag_btcur_init()`, `xchk_ag_free()`, `xchk_rtgroup_init()`, `xchk_rtgroup_lock()`, `xchk_rtgroup_free()`, `xchk_iget_for_scrubbing()`, `xchk_setup_inode_contents()`, `xchk_ilock()`, `xchk_iunlock()`, and `xchk_should_check_xref()`.

Control flow: Operational error helpers convert metadata verifier and IO-style failures into scrub outcome flags and tracepoints while preserving true runtime errors for userspace. AG setup allocates a transaction, gets a perag, reads AGI before AGF, optionally waits for deferred intents to drain, and creates bno/cnt/rmap/refcount/inobt/finobt cursors as available. Realtime setup similarly grabs rtgroup references, locks metadata inodes, drains intents when needed, and initializes rt rmap/refcount cursors. Inode setup first tries a safe iget, then uses AGI locking and inobt lookup to distinguish vanished files from corrupt allocated inodes.

State and persistence: This file mostly manages in-memory scrub state: `sc->tp`, `sc->sa`, `sc->sr`, `sc->ip`, `sc->ilock_flags`, hook flags, and `sm_flags`. It can force the log and AIL to disk through `xchk_checkpoint_log()`, and repair-mode transactions reserve real blocks/log space, but most helpers do not alter persistent metadata unless invoked by repair callers through transactions. `xchk_inode_count_blocks()` accounts for metadata btree forks by counting btree blocks rather than ordinary bmap extents.

Dependencies and integration points: This is the central dependency of almost every scrubber. It integrates with XFS transaction reservation, perag and rtgroup lifetimes, btree cursor constructors, quota repair attach, tempfile adjustment, inode cache and AGI locking, deferred intent drains, buffer verifiers, subordinate scrub dispatch, rmap queries, reflink shared-extent checks, and static-key filesystem gates for drain/quota/dirent/rmap hooks.

Risks and test signals: High-risk areas are lock ordering around AGI/AGF, intent drain retry behavior (`-ECHRNG`, `-EDEADLOCK`), distinguishing verifier corruption from runtime failure, dropping inode references while in transaction context, and stale xref cursors after a secondary structure fails. Test with concurrent allocation/free, inodegc racing iget, realtime intent chains, metadata inode scrub with reflink enabled, quota attach failures in repair mode, forced log checkpoints, buffer verifier injection, and xref cursor failures that should mark `XFAIL` without aborting the primary scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/common.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/common.h

Purpose: Declares the shared XFS scrub helper API and compile-time fallbacks for optional quota and realtime features.

Important APIs, types, and functions: The header exports transaction helpers, error processors, corruption/preen/warning setters, setup functions for filesystem/AG/inode/directory/xattr/parent/dirtree/metapath/realtime/quota/counter scrubbers, AG and rtgroup lifecycle functions, inode acquisition and lock wrappers, buffer recheck, cross-reference gating, metadata inode fork scrub, filesystem hook enabling, inode allocation/block-count helpers, and root-directory predicates. Inline helpers include `xchk_setup_nothing()`, `xchk_ag_init_existing()`, `xchk_rtgroup_init_existing()`, `xchk_iget_safe()`, `xchk_skip_xref()`, `xchk_needs_repair()`, `xchk_could_repair()`, and `xchk_need_intent_drain()`.

Control flow: Scrub operation tables use the setup prototypes to acquire the required resources before calling a specific scrub function. Optional feature sections map unsupported realtime or quota setup functions to `xchk_setup_nothing()` or corruption-style stubs so callers can compile without feature-specific conditionals.

State and persistence: The header defines no persistent structures. Its inline predicates interpret `struct xfs_scrub_metadata` flags to decide whether xref should continue, whether repair is needed, and whether repair was requested and not already completed.

Dependencies and integration points: Included throughout `fs/xfs/scrub`. It ties scrub code to XFS mount, inode, buffer, btree cursor, perag, rtgroup, owner info, and quota types, and exposes integration points for repair, health marking, and feature-gated metadata scans.

Risks and test signals: Risks are API contract drift between setup functions and callers, wrong feature fallback behavior for `CONFIG_XFS_RT` or `CONFIG_XFS_QUOTA`, and misuse of `xchk_skip_xref()` causing missed cross-reference failures. Test by compiling quota/realtime combinations, running each scrub type's setup/teardown, and checking repair-flag transitions through preen/corrupt/xcorrupt outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/cow_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/cow_repair.c

Purpose: Repairs an inode's in-core CoW fork mappings by replacing bad unwritten CoW staging extents whose on-disk refcount/rmap evidence is missing, shared, or cross-linked. It deliberately avoids written CoW extents in active writeback and delalloc reservations that have no on-disk state.

Important APIs, types, and functions: The external entry point is `xrep_bmap_cow()`. State lives in `struct xrep_cow` and replacement allocations in `struct xrep_cow_extent`. Discovery helpers include `xrep_cow_find_bad()`, `xrep_cow_find_bad_rt()`, `xrep_cow_mark_shared_staging()`, `xrep_cow_mark_missing_staging()`, `xrep_cow_mark_missing_staging_rmap()`, `xrep_cow_mark_file_range()`, and `xrep_cow_trim_refcount()`. Mutation helpers include `xrep_cow_alloc()`, `xrep_cow_alloc_rt()`, `xrep_cow_find_mapping()`, `xrep_cow_replace_mapping()`, `xrep_cow_replace_range()`, and `xrep_cow_replace()`.

Control flow: `xrep_bmap_cow()` rejects unsupported filesystems, absent CoW forks, big realtime allocation units, metadata realtime inodes, and non-extents CoW forks. It joins the inode to the transaction, scans each CoW fork extent, skips delalloc and written extents, and queries AG or rtgroup refcount and rmap btrees for unwritten staging mappings. Bad file offset ranges are recorded in `bad_fileoffs`; each range is replaced by allocating fresh CoW staging space, updating/splitting the in-core CoW fork extent, finishing deferred refcount allocation work, and recording old blocks for later reap.

State and persistence: The CoW fork itself is in-core, but replacement allocations update persistent allocation/refcount metadata through the transaction and deferred operations. Removed old staging blocks are persisted as free/unmapped by `xrep_reap_fsblocks()` or `xrep_reap_rtblocks()` using `XFS_RMAP_OINFO_COW`. Bitmaps track bad file offsets and old physical blocks only for the repair session.

Dependencies and integration points: Requires rmapbt and reflink; realtime repair also uses rtgroup rmap/refcount cursors and rt allocator APIs. It depends on scrub/repair AG or rtgroup initialization, `xfs_refcount_query_range()`, `xfs_rmap_query_range()`, extent-list manipulation, transaction reservation growth, refcount COW allocation intents, and repair reap helpers.

Risks and test signals: Risks include replacing the wrong part of a split CoW extent, mishandling realtime block/group conversions, failing after in-core mapping update but before old-block reap, ENOSPC during replacement, and preserving written extents that later expose latent damage. Test shared-domain refcount records over CoW fork ranges, missing COW-domain records, non-COW rmap overlaps, forced rebuild, partial allocations shorter than the requested range, realtime CoW extents, transaction roll/defer failures, and crash recovery after replacement before reap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/cow_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dab_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dab_bitmap.h

Purpose: Provides a tiny type-checked wrapper around `xbitmap32` for directory/attribute block numbers (`xfs_dablk_t`).

Important APIs, types, and functions: Defines `struct xdab_bitmap` containing an `xbitmap32`, plus inline wrappers `xdab_bitmap_init()`, `xdab_bitmap_destroy()`, `xdab_bitmap_set()`, and `xdab_bitmap_test()`.

Control flow: Users initialize the bitmap, set directory/attribute block-number ranges with lengths, test whether a block is present and optionally retrieve the contiguous length, then destroy the bitmap.

State and persistence: All state is transient in-memory bitmap state. No filesystem metadata is persisted.

Dependencies and integration points: Used by scrub or repair code that needs to track DA block ranges without mixing them with fsblocks or file offsets. It depends on `xbitmap32` and XFS DA block typedefs.

Risks and test signals: The main risk is unit confusion: callers must pass DA block numbers and extents, not fsblocks or byte offsets. Test with boundary DA block values, overlapping ranges, empty ranges, and callers that convert between directory data pointers and DA blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dab_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.c

Purpose: Implements a generic directory/attribute btree scrub walker for XFS DA btrees. It validates DA node/leaf structure, hash ordering, parent hash coverage, sibling linkage, block ownership, CRC-era padding, block-type expectations, and delegates leaf-record checks to directory or attribute-specific scrubbers.

Important APIs, types, and functions: Public APIs are `xchk_da_process_error()`, `xchk_da_set_corrupt()`, `xchk_da_set_preen()`, `xchk_da_btree_hash()`, and `xchk_da_btree()`. Internal helpers include `xchk_da_btree_node_entry()`, `xchk_da_btree_ptr_ok()`, multiplexed buffer verifiers `xchk_da_btree_read_verify()`, `xchk_da_btree_write_verify()`, `xchk_da_btree_verify()`, sibling checkers, and `xchk_da_btree_block()`.

Control flow: `xchk_da_btree()` skips short-format forks, allocates `struct xchk_da_btree`, initializes `xfs_da_args` and `xfs_da_state`, chooses directory or attr geometry, and starts from the expected root block. `xchk_da_btree_block()` bounds-checks the block number, reads it with a scrub-specific verifier that accepts leaf1/leafn/node/attr leaf forms, checks owner and siblings, normalizes magic values, records max records/hash values, and verifies parent hash expectations. The main loop descends through node `before` pointers and calls the supplied record callback for leaf entries.

State and persistence: Traversal state is temporary in `xfs_da_state`, `path`, `altpath`, hash arrays, and max-record arrays. It reads buffers through the scrub transaction and releases them before returning. It only modifies scrub flags and buffer type annotations; it does not repair or persist metadata.

Dependencies and integration points: Used by directory and xattr scrub code. It depends on XFS DA geometry, dir/attr buffer verifiers, `xfs_da3_path_shift()` for sibling validation, DA hash helpers, transaction buffer lifetime, and `xchk_buffer_recheck()` from common infrastructure.

Risks and test signals: Risks include false positives around leaf1-as-leafn handling, missing holes in directory btrees, wrong `tree_level` tracking, unbounded or cyclic sibling/path traversal, and confusion between directory block ranges (`leafblk` to `freeblk`) and attr fork unbounded DA ranges. Test short format skip, block/leaf/node/attr leaf formats, missing root block, bad owner, nonzero CRC padding, sibling mismatch, out-of-order hashes, too-deep trees, and leaf callback early termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.h

Purpose: Declares the shared scrub interface and traversal state for XFS directory/attribute btrees.

Important APIs, types, and functions: Defines `struct xchk_da_btree`, which embeds `xfs_da_args`, per-level hash and max-record arrays, `xfs_da_state`, scrub context, private callback data, expected block bounds, and tree level. Defines callback type `xchk_da_btree_rec_fn` and declares `xchk_da_process_error()`, `xchk_da_set_corrupt()`, `xchk_da_set_preen()`, `xchk_da_btree_hash()`, and `xchk_da_btree()`.

Control flow: Directory and attribute scrubbers call `xchk_da_btree()` with the fork id and a leaf-record callback. The callback receives the active `struct xchk_da_btree` and level, and can use the stored DA state/path to inspect the current leaf entry.

State and persistence: The struct captures only transient traversal state. `lowest` and `highest` constrain legal DA block addresses for directory trees while attr trees leave the upper bound open.

Dependencies and integration points: Included by DA btree clients such as `dir.c` and attr scrubbers. It depends on `xfs_da_args`, `xfs_da_state`, scrub context, and DA geometry constants.

Risks and test signals: API risks include duplicate declaration of `xchk_da_set_preen()` and callback misuse if callers assume a leaf layout inconsistent with `blk->magic`. Test all callers with directory data fork and attr fork btrees, including short-format forks where the walker must return without invoking callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dir.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dir.c

Purpose: Scrubs XFS directory metadata: DA btree leaf records, data-block bestfree accounting, leaf/free bestfree indexes, directory entry lookupability, file type consistency, special `.`/`..` entries, parent pointer back-links, and zapped-directory health.

Important APIs, types, and functions: Setup and main entry points are `xchk_setup_directory()` and `xchk_directory()`. Directory scan state lives in `struct xchk_dir` with deferred `struct xchk_dirent` entries stored in `xfarray`/`xfblob`. Key helpers include `xchk_dir_check_ftype()`, `xchk_dir_lock_child()`, `xchk_dir_parent_pointer()`, `xchk_dir_check_pptr_fast()`, `xchk_dir_actor()`, `xchk_dir_rec()`, `xchk_directory_data_bestfree()`, `xchk_directory_leaf1_bestfree()`, `xchk_directory_free_bestfree()`, `xchk_directory_blocks()`, slow-dirent revalidation helpers, and `xchk_dir_looks_zapped()`.

Control flow: `xchk_directory()` rejects non-directories and zapped-looking forks, checks plausible size, runs `xchk_da_btree()` with `xchk_dir_rec()` to validate leaf hash entries against data entries, checks free-space structures with `xchk_directory_blocks()`, then walks every directory entry with `xchk_dir_walk()`. Each entry is name/inode validated, re-looked-up by hash, checked against the child inode's ftype and tree membership, and, if parent pointers are enabled, checked for a matching parent xattr. Parent-pointer checks use a fast nowait child lock path and defer contended entries to a slow path that can drop and reacquire locks with revalidation.

State and persistence: This is a read-only scrubber. It temporarily allocates deferred dirent arrays/blobs, reads directory buffers, and sets scrub flags. Successful clean scrub marks the zapped-directory sickness bit healthy via `xchk_mark_healthy_if_clean()`. It does not persist directory changes.

Dependencies and integration points: Depends on DA btree scrub, directory readdir helpers, `xchk_dir_lookup()`, inode iget/release, XFS directory buffer verifiers, parent pointer lookup, temporary xfile arrays/blobs, health tracking, and common inode/transaction locking. Repair setup can be invoked first via `xrep_setup_directory()` when repair is allowed.

Risks and test signals: Risks include stale entries while cycling locks, parent pointer races, directory block holes tolerated in some formats, bestfree ordering/count errors, incorrect ftype handling on filesystems without ftype support, and metadata-vs-regular tree crossings. Test short/block/leaf/node directories, bad name bytes, stale hash entries, leaf1 free index mismatch, free block stale counts, root `..`, metadir directories, parent-pointer mismatch, child lock contention, zapped forks, and concurrent rename during slow parent-pointer validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dir_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dir_repair.c

Purpose: Rebuilds corrupt XFS directories by constructing a clean temporary directory from either salvaged on-disk dirents or authoritative parent pointers, then atomically exchanging the rebuilt data fork into the target. It can also repair parent selection, link counts, and orphanage adoption for parentless directories.

Important APIs, types, and functions: Public setup/repair entry points are `xrep_setup_directory()` and `xrep_directory()`. State lives in `struct xrep_dir`; staged updates use `struct xrep_dirent`. Major helpers include parent discovery (`xrep_dir_find_parent()`), salvage filters and readers (`xrep_dir_want_salvage()`, `xrep_dir_salvage_entry()`, `xrep_dir_recover_sf()`, `xrep_dir_recover_data()`, `xrep_dir_recover_dirblock()`, `xrep_dir_recover()`), replay (`xrep_dir_stash_createname()`, `xrep_dir_stash_removename()`, `xrep_dir_replay_update()`, `xrep_dir_replay_updates()`), parent-pointer scans and live updates, swap/finalize helpers, link-count reset, orphanage movement, and teardown.

Control flow: Setup enables dirent hooks, ensures the orphanage exists, creates a temporary directory, and allocates repair state. Without parent pointers, repair finds a plausible parent, salvages valid entries from shortform or mapped data blocks, computes child ftypes by iget, periodically flushes staged entries into the tempdir to cap memory, then drops locks for an exchange. With parent pointers, it scans filesystem inodes and parent xattrs, records parent pointers that target the broken directory as tempdir entries, tracks a parent via child dirents pointing back to the target, and uses live dirent hooks to capture concurrent changes during the scan. Rebuild finalization replays queued updates, fixes `..`, converts shortform forks if necessary, sets nlink, atomically exchanges data fork mappings, resets the tempfile, and optionally moves parentless linked directories to the orphanage.

State and persistence: Persistent changes occur through normal XFS directory operations, parent-pointer removal/addition side effects, link count updates, unlinked-list removal, atomic file mapping exchange, and old-block reaping/reset of the tempfile. Temporary state includes staged dirent arrays/blobs, findparent/iscan state, live-update hooks, adoption context, and exchange context.

Dependencies and integration points: Requires rmapbt for reaping and exchange-range support for atomic rebuild. It integrates with tempfile/tempexch infrastructure, orphanage/adoption helpers, findparent scans, inode scans, xattr/parent-pointer walking, readdir helpers, xfs_dir create/remove/replace APIs, transaction reservation helpers, quota/resource accounting, dcache invalidation for moved entries, and scrub hook gates.

Risks and test signals: High-risk areas are reconstructing duplicate or stale names, dropping locks during scans while preserving correctness via hooks, shortform-to-block conversion before exchange, link-count repair for unlinked directories, orphanage move races, and crash consistency between exchange and tempfile reset. Test corrupt shortform and block directories, parent-pointer enabled rebuilds under concurrent renames, duplicate names, invalid child inodes, huge directories that trigger stash flushes, root/metadir repairs, no-parent adoption, unlinked directories with and without dirents, ENOSPC/EDQUOT during replay, and crash recovery around exchange and reap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dir_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.c

Purpose: Validates the directory tree structure on parent-pointer filesystems by walking each parent-pointer path from a directory upward toward the appropriate root and detecting loops, multiple parents, disconnected paths, corrupt ancestors, stale concurrent updates, and parentless-directory invariants.

Important APIs, types, and functions: Setup and scrub entry points are `xchk_setup_dirtree()` and `xchk_dirtree()`. Shared repair-facing APIs include `xchk_dirtree_find_paths_to_root()`, `xchk_dirpath_append()`, `xchk_dirtree_evaluate()`, and `xchk_dirtree_parentless()`. Internal helpers create initial paths from parent xattrs, revalidate first steps, find next parent steps, walk upward, detect stale path steps from dirent hooks, reset/load path state, and clean up allocated path arrays/blobs.

Control flow: Setup enables dirent hooks, optionally prepares repair, allocates `struct xchk_dirtree`, path step arrays and name blobs, then sets up inode contents. `xchk_dirtree()` records the root inode for the target tree, installs a live dirent hook, and calls `xchk_dirtree_find_paths_to_root()`. That function repeatedly creates one path per parent pointer, walks each path upward while dropping the target ILOCK to avoid lock explosion, records outcomes (`OK`, `DELETE`, `LOOP`, `CORRUPT`), and restarts if hooks mark scan data stale. Evaluation counts good/suspect/bad paths and flags corruption or xref corruption according to whether the target should be parentless.

State and persistence: The scrubber is read-only. It maintains in-memory path lists, per-path seen-inode bitmaps, xfarray path steps, xfblob names, parent-pointer scratch records, stale/aborted flags, and a live update hook. It sets scrub flags for corruption, xref corruption, or incomplete scans but does not modify directory entries.

Dependencies and integration points: Requires parent pointer support and dirent hook gates. It uses xattr walking for parent pointers, inode iget/lock helpers, parent xattr parsing, inode root/metadir predicates, zapped-parent-pointer detection, orphanage setup when repair is possible, and structures shared with `dirtree_repair.c`.

Risks and test signals: Risks include missing a concurrent rename that invalidates a path, treating corrupt ancestor parent pointers as target corruption, path-depth overflow, multiple-parent counting errors, cross-tree parent links, unlinked parents, and stale xattr forks. Test root and metadir roots, normal one-parent directories, zero-parent nonroots, self-parent loops, ancestor cycles, multiple parent pointers, bad generation in parent records, parent not a directory, parent in another tree, zapped attr forks, and heavy concurrent rename while scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.h

Purpose: Defines shared directory-tree path tracking structures and APIs used by the directory tree scrubber and repairer.

Important APIs, types, and functions: Defines `struct xchk_dirpath_step` for one parent-link step, `enum xchk_dirpath_outcome` for scan and repair states, `struct xchk_dirpath` for an in-core path with seen-inode bitmap and xfarray indices, `struct xchk_dirtree_outcomes` for evaluation counts, and `struct xchk_dirtree` for global scan/repair state. Declares iteration macros and functions `xchk_dirtree_parentless()`, `xchk_dirtree_find_paths_to_root()`, `xchk_dirpath_append()`, and `xchk_dirtree_evaluate()`.

Control flow: `dirtree.c` fills path steps and outcomes while scanning; `dirtree_repair.c` consumes and mutates outcomes to delete excess paths or adopt orphaned directories. Repair-specific outcome values (`DELETING`, `DELETED`, `ADOPTING`, `ADOPTED`) let live update hooks distinguish self-induced changes from stale external mutations.

State and persistence: The header defines transient in-memory state only: names in `xfblob`, steps in `xfarray`, path list entries, scratch parent records, hook state, lock, and stale/aborted booleans. Persistent directory entries and parent pointers are changed only by repair code using this state.

Dependencies and integration points: Integrates parent records, parent args, adoption context, dirent hooks, inode bitmaps, xfile arrays/blobs, and scrub context. It is the contract boundary between scan/evaluate and repair/fix logic.

Risks and test signals: Risks include outcome state-machine drift between scrub and repair, stale hook processing after `sc->ip` release, and xfarray index assumptions that path steps for a path are sequential after the second step. Test path creation/deletion/adoption transitions, cleanup after aborted scans, and concurrent hook callbacks during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree_repair.c

Purpose: Repairs directory tree structural problems discovered by `dirtree.c`, primarily by removing excess or looping parent paths to the target directory and adopting parentless linked directories into the orphanage.

Important APIs, types, and functions: Public entry points are `xrep_setup_dirtree()` and `xrep_dirtree()`. Decision helpers include `xrep_dirtree_decide_fate()`, `xrep_dirtree_delete_all_paths()`, `xrep_dirtree_keep_one_good_path()`, `xrep_dirtree_keep_one_suspect_path()`, and `xrep_dirtree_find_surviving_path()`. Mutation helpers include `xrep_dirtree_prep_path()`, `xrep_dirtree_unlink_iolock()`, `xrep_dirtree_unlink()`, `xrep_dirtree_delete_path()`, adoption path creation, `xrep_dirtree_adopt_iolock()`, `xrep_dirtree_adopt()`, and `xrep_dirtree_fix_problems()`.

Control flow: Repair locks the scan state, evaluates path outcomes, chooses a survivor or marks all bad paths for deletion, and applies changes. Path deletion loads the first parent-pointer step, igets the parent, drops scan locks/target ILOCK/transaction to reserve and acquire normal directory locks, removes the parent dirent, removes the child parent pointer, drops link counts, optionally resets `..` to the surviving parent or root stand-in, invalidates any cached dentry, commits, and reacquires scrub resources. If no path remains and the orphanage can adopt, repair creates an adoption path so hooks see the self-update, moves the directory, and bumps the child link count.

State and persistence: Persistent updates include directory entry removal, parent-pointer removal, link count changes, `..` replacement, dcache invalidation, and orphanage adoption. The repair state machine records in-progress deletion/adoption outcomes so dirent hooks can advance to deleted/adopted rather than marking scan data stale for changes caused by repair itself.

Dependencies and integration points: Depends on the path state built by `dirtree.c`, orphanage/adoption helpers, XFS directory remove/replace APIs, parent-pointer removename, transaction reservation for remove/adoption, dentry cache lookup/delete, scrub inode locks, and dirent update hooks.

Risks and test signals: Risks include deadlocks while acquiring parent and child IOLOCKs, stale scan results after dropping locks, incorrect `..` target after deleting a path, link-count underflow, dcache inconsistency after removal, adoption name collision, and treating repair-generated hook events as external staleness. Test deleting a self-loop, deleting extra parents while preserving one good path, all-suspect multiple paths, zero-path adoption, concurrent rename during repair causing `-ESTALE` and rescan, dcache-positive child entries, parent-pointer enabled and disabled edge cases, and orphanage unavailable/corrupt cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dqiterate.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/dqiterate.c

Purpose: Implements an iterator that walks both on-disk and in-core XFS dquots for a quota type, so scrub/repair code can inspect every relevant quota record even when quota file mappings are sparse or repairs have disturbed mappings.

Important APIs, types, and functions: Public APIs are `xchk_dqiter_init()` and `xchk_dquot_iter()`. Internal helpers are `xchk_dquot_iter_revalidate_bmap()`, `xchk_dquot_iter_advance_bmap()`, and `xchk_dquot_iter_advance_incore()`. State is stored in `struct xchk_dqiter` from the quota scrub headers, including current id, quota inode, cached bmap record, fork sequence, and quota type.

Control flow: Initialization records scrub context, quota type, quota inode, an invalid cached mapping, and id zero. Each `xchk_dquot_iter()` call locks the quota inode data map, revalidates the cached bmap against the quota fork sequence and current id, advances over holes to the next real quota-file extent, separately finds the next incore dquot id from the quota radix tree if the on-disk iterator jumped forward, chooses the lower id, obtains the dquot with `xfs_qm_dqget()`, advances the cursor, and returns 1/0/error.

State and persistence: The iterator does not persist metadata. It reads quota inode mappings and in-core dquot radix trees, and returns referenced dquots to callers. Cached bmap state is invalidated by fork sequence changes.

Dependencies and integration points: Used by quota scrub/repair code. It depends on XFS quota inode lookup, `m_quotainfo`, `qi_dqperchunk`, bmap read, data-map locking, dquot radix trees protected by `qi_tree_lock`, and `xfs_qm_dqget()`.

Risks and test signals: Risks include skipping incore dquots when the quota file has holes, stale bmap cache after quota file repair, id overflow around `XFS_DQ_ID_MAX`, sparse quota files with delayed mappings, and races with dquot allocation/removal. Test dense and sparse quota files, incore-only dquots, quota file extent changes during iteration, last-id boundary, user/group/project quota types, and injected bmap corruption or missing mapping records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/dqiterate.c -->
