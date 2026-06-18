# Research: subset-b-005780

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.c

## Purpose
This file is the generic XFS btree engine.  It supplies block validation, cursor traversal, lookup, insertion, deletion, record update, range query, owner rewrite, cursor cache setup, and shared block allocation helpers for all concrete XFS btree families.  Concrete trees provide `struct xfs_btree_ops` callbacks for record/key interpretation, min/max geometry, root updates, block allocation/freeing, comparisons, and buffer verification; this file implements the common mechanics around those callbacks for AG-rooted, inode-rooted, and in-memory btrees.

## Important APIs, Types, And Functions
The primary entry points are `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_update`, `xfs_btree_get_rec`, `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_visit_blocks`, `xfs_btree_count_blocks`, `xfs_btree_change_owner`, `xfs_btree_new_iroot`, `xfs_btree_alloc_metafile_block`, and `xfs_btree_free_metafile_block`.

Validation helpers split by pointer format and root type: `__xfs_btree_check_fsblock`, `__xfs_btree_check_memblock`, and `__xfs_btree_check_agblock` validate magic, level, record count, CRC-era UUID/block-number/owner metadata, and sibling pointers.  `xfs_btree_fsblock_verify`, `xfs_btree_agblock_verify`, and `xfs_btree_memblock_verify` are verifier-facing helpers.  CRC helpers (`xfs_btree_fsblock_calc_crc`, `xfs_btree_agblock_calc_crc`, and matching verify functions) integrate with buffer log items and `xfs_buf_update_cksum`.

Layout helpers such as `xfs_btree_rec_addr`, `xfs_btree_key_addr`, `xfs_btree_high_key_addr`, and `xfs_btree_ptr_addr` compute 1-based addresses inside a btree block using operation-provided key, pointer, and record lengths.  They understand overlapping interval trees, where each node pointer has low and high keys.

Mutation helpers include `xfs_btree_lshift`, `xfs_btree_rshift`, `__xfs_btree_split`, `xfs_btree_new_root`, `xfs_btree_insrec`, `xfs_btree_delrec`, `xfs_btree_kill_root`, and inode-root promotion/demotion helpers.  They are internal but form the balancing logic for public insert/delete operations.

## Control Flow
Lookup starts by initializing a root pointer with `xfs_btree_init_ptr_from_cur`, then descends from root to leaf.  Each level is binary searched with the tree-specific `cmp_key_with_cur` callback.  For non-leaf levels, the selected key index is converted to a child pointer and validated before reading the next block.  On the leaf, the cursor is adjusted for EQ, LE, or GE semantics and may step to the next leaf when a GE lookup lands beyond a nonterminal block.

Forward and backward iteration first tries to move within the current block.  If the cursor runs off an edge, it climbs parent levels until it can move to an adjacent subtree, reads down to the requested level, and sets leaf-side pointers to the first or last entry.  Sibling read-ahead is used opportunistically and recorded in each `bc_levels[level].ra` bitset.

Insertion starts with a record generated from `cur->bc_rec`, then calls `xfs_btree_insrec` from the leaf upward.  Full blocks are handled by enlarging inode roots, promoting inode roots to real blocks, shifting entries into siblings, splitting blocks, or creating a new root.  If a split returns a new block pointer and key, the loop continues at the parent level.  Deletion removes the selected entry, shifts block contents, updates keys, and rebalances underfull blocks by borrowing from siblings or joining blocks; root shrinkage can remove a level or copy a child back into an inode root.

Range query has two paths.  Non-overlapping btrees do a LE lookup near the low key and iterate until record low keys exceed the high key.  Overlapping interval btrees perform a depth-first search using low/high node keys to prune subtrees, with cleanup logic to release node buffers if no leaf result is left pinned in the cursor.

## State And Persistence Behavior
The core mutable state is the `xfs_btree_cur`: transaction, mount, ops, current in-core record, tree height, root-specific union, per-format private state, and per-level buffer/pointer/read-ahead slots.  For on-disk btrees, data changes are persisted by transaction logging of exact header, key, pointer, or record byte ranges.  Header logging intentionally skips CRC fields because recovery recomputes them.  Buffer types are marked as btree buffers before logging.

Inode-rooted btrees can store the root in an inode fork; root changes log the inode fork through `xfs_trans_log_inode`.  AG-rooted btrees update AG header roots through `ops->set_root`, while staging cursors redirect root updates to fake root structures.  In-memory btrees route buffer access to an xmbuf target and use long-format block addresses.  Cursor deletion releases held buffers and drops group references.  Cursor duplication re-reads each pinned block through the transaction so the new cursor owns its own buffer references.

## Dependencies And Integration Points
This file is central to allocation, inode allocation, bmap, rmap, refcount, realtime rmap/refcount, quota/metafile, online repair, transaction, buffer, health, and trace code.  It depends heavily on `xfs_btree.h` contracts, buffer verifiers, endian conversion helpers, `xfs_trans_*` logging APIs, allocation/free APIs, group/perag helpers, and tree-specific ops from concrete btree implementations.  Staging integration is explicit through `XFS_BTREE_STAGING`, fake roots, and bulk-load constraints.  Memory-btree integration is explicit through `xfbtree_verify_bno`, xmbuf address conversion, and xmbuf-backed buftargs.

## Risks And Edge Cases
High-risk areas are off-by-one cursor indexing, 1-based in-block addressing, root-level special cases, inode root reallocations, overlapping high-key maintenance, sibling pointer consistency, and transaction buffer ownership.  Staging cursors deliberately reject regular block allocation/freeing and duplication because bulk-load construction owns block provisioning.  Split handling contains a kernel-only worker path for bmap btree stack pressure and includes comments about avoiding workqueue rescuer and AGF lock deadlocks.  Deletion is especially sensitive because joins defer some overlapping high-key updates to the caller-level loop.

Corruption handling usually marks the btree sick and returns `-EFSCORRUPTED`; verifier paths return failure addresses.  Some paths depend on DEBUG checks for pointer ordering and block consistency, so production safety relies on earlier verifiers, operation callbacks, and transaction discipline.  In-memory query cleanup exists because a zero-result overlapped search can otherwise leave node buffers pinned.

## Test Signals
Useful test signals include xfstests that stress bmap, rmap, refcount, inode allocation, free-space btrees, realtime btrees, online repair rebuilds, and metadata directory btrees.  Targeted tests should cover insert/delete at root boundaries, inode-root promotion and demotion, block split/join with left and right siblings, overlapping rmap/refcount interval queries, cursor duplication under active transactions, CRC verifier failures, wrong owner detection, sibling cycles during `xfs_btree_visit_blocks`, ENOSPC from tree-specific allocation callbacks, and xmbuf-backed in-memory btree operations.  Tracepoints such as btree split, allocation, free, update keys, overlapped query, and corruption traces are strong runtime observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.h

## Purpose
This header defines the generic btree ABI used by XFS btree implementations and the shared core in `xfs_btree.c`.  It provides disk-format wrapper unions for keys, records, and pointers; the operation vector that concrete btrees must implement; cursor state; geometry flags; exported core APIs; and inline helpers for key comparisons, cursor allocation, root detection, record counts, and pointer state.

## Important APIs, Types, And Functions
`union xfs_btree_ptr`, `union xfs_btree_key`, `union xfs_btree_rec`, and `union xfs_btree_irec` unify the concrete allocbt, inobt, bmbt, rmapbt, and refcountbt formats.  `struct xfs_btree_ops` is the most important contract: it supplies tree name/type, geometry flags, key/pointer/record sizes, LRU refs, stats offset, sick mask, cursor duplication/update hooks, root setter, block allocator/free callbacks, min/max record callbacks, key/record initialization, comparison functions, contiguity checks, verifier ops, and optional inode-root reallocation.

`struct xfs_btree_cur` captures active traversal and mutation state.  It stores transaction and mount pointers, ops, current record, height limits, optional group reference, root-specific inode/AG/memory state, per-tree private accounting, and a flexible array of per-level `struct xfs_btree_level` slots.  Flags include `XFS_BTREE_STAGING`, `XFS_BTREE_BMBT_WASDEL`, `XFS_BTREE_BMBT_INVALID_OWNER`, and `XFS_BTREE_ALLOCBT_ACTIVE`.

The header exports the common core (`lookup`, `insert`, `delete`, `update`, iteration, range query, block visit, count, owner change), block verifier and CRC helpers, block layout addressors, cursor lifecycle functions, and metafile block allocation/free helpers.  Inline comparison helpers delegate to `ops->cmp_two_keys`, including masked comparison variants for callers that compare only selected key fields.

## Control Flow And State
Callers allocate cursors with `xfs_btree_alloc_cursor`, populate type-specific state, then call core functions.  The cursor levels array tracks one buffer and 1-based entry pointer per tree level.  For inode-rooted btrees, `xfs_btree_at_iroot` identifies the root level as an in-inode block instead of a buffer.  For staged rebuilds, the cursor redirects AG or inode root state to fake-root structures declared in the staging header.

## Dependencies And Integration Points
The header depends on XFS format types from other headers but forward-declares major kernel/XFS structures to limit include coupling.  It integrates with buffer verifiers via `struct xfs_buf_ops`, transaction logging through exported log helpers, health reporting through sick masks, concrete btree modules through cursor cache init/destroy calls, and online repair via staging/memory btree support.

## Risks And Test Signals
The main risk is contract mismatch between a concrete btree's ops and the generic core: wrong key length, pointer length, comparison semantics, min/max geometry, root reallocation size, or verifier pairing can corrupt metadata.  Tests should validate each concrete btree's ops table against the generic invariants: correct cursor sizing, root detection, max/min record calculations, key ordering, masked comparisons, overlapping high-key behavior, and staging flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.c

## Purpose
This file implements the in-memory btree backend used with xmbuf-backed buffer targets.  It adapts the generic btree core to ephemeral btrees, primarily for online repair and staging workflows that need btree algorithms without committing intermediate state to normal filesystem metadata.

## Important APIs And Functions
`xfbtree_init` initializes an empty memory btree, computes record/key-pointer geometry from xmbuf block size and btree ops, requires CRC-capable long-format btrees, creates an empty leaf root, and records the root pointer.  `xfbtree_destroy` drains the buftarg.  `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`, and `xfbtree_dup_cursor` implement generic btree ops for memory roots.  `xfbtree_alloc_block` and `xfbtree_free_block` hand out monotonically increasing xfile block numbers and shrink `highest_bno` only when freeing the topmost block.  `xfbtree_get_minrecs` and `xfbtree_get_maxrecs` expose precomputed geometry.

`xfbtree_trans_commit` and `xfbtree_trans_cancel` are the transaction integration points.  They scan transaction log items, detach buffers belonging to the memory btree target, finalize or release them, and recompute the transaction dirty flag based on non-xfbtree items.  `xfbtree_buf_match` identifies matching buffer log items.

## Control Flow
Initialization zeros the `struct xfbtree`, stores the target, computes max/min records for leaves and internal nodes, sets `highest_bno` to zero and `nlevels` to one, then allocates block zero as an initialized leaf root through `xfs_buf_get` and `xfs_btree_init_buf`.  Allocation simply assigns the next xfbno if `xfbtree_verify_bno` accepts the translated daddr.  Commit walks `tp->t_items`, detaches matching xmbuf buffers, finalizes dirty contents to backing xfile storage, and releases each buffer even if a previous finalize failed.

## State And Persistence Behavior
The in-memory btree persists only to its xmbuf/xfile target, not to normal XFS metadata.  `root`, `nlevels`, `highest_bno`, and min/max geometry live in `struct xfbtree`.  Transaction commit writes dirty ephemeral btree buffers immediately and detaches them from the transaction because the larger transaction should not log these temporary buffers.  Cancel does not undo changes; callers must discard the btree afterwards.

## Dependencies And Integration Points
This file depends on xmbuf address conversion, buffer items, transaction internals, tracepoints, btree core initialization, and group references for cursor duplication.  It is enabled through `CONFIG_XFS_BTREE_IN_MEM` declarations in the header and used by online repair paths that build temporary btrees.

## Risks And Test Signals
Risks include address-space exhaustion, stale dirty transaction state after detaching xfbtree buffers, use-after-cancel if callers keep accessing a canceled memory btree, and assumptions that only topmost freed blocks reduce `highest_bno`.  Tests should cover memory btree init failure cleanup, root creation, allocation limit failure, cursor duplication with held group references, transaction commit with mixed xfbtree and non-xfbtree dirty items, finalize errors that still detach all buffers, and cancel behavior followed by teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.h

## Purpose
This header defines the lightweight state and API for xmbuf-backed in-memory btrees.  It gives the generic btree code a block-number type, daddr conversion helpers, an `xfbtree` root/geometry structure, and operation prototypes used when `CONFIG_XFS_BTREE_IN_MEM` is enabled.

## Important APIs And Types
`xfbno_t` is a 64-bit memory-btree block number.  `XFBNO_BLOCKSIZE`, `XFBNO_BBSHIFT`, and `XFBNO_BBSIZE` map xmbuf block sizing into 512-byte sector units.  `xfbno_to_daddr` and `xfs_daddr_to_xfbno` convert between memory btree block numbers and buffer daddrs.

`struct xfbtree` stores the xfs buftarg, highest assigned block number, owner, root pointer, tree height, and two-entry min/max record arrays for leaf and node levels.  The exported functions are the memory-btree implementations of root, pointer, cursor duplication, record geometry, block allocation/free, initialization/destruction, and transaction commit/cancel.

## Control Flow And State
The header-level state model is intentionally small: the root pointer and height mimic on-disk btree roots, while the target and block counter provide storage allocation.  `xfbtree_verify_bno` delegates to `xmbuf_verify_daddr` to ensure a translated address is valid for the backing memory target.  When in-memory btrees are disabled, this verifier is a constant false macro, which prevents accidental use.

## Dependencies, Risks, And Test Signals
The header depends on xmbuf constants and generic XFS btree declarations.  Its main risk is unit mismatch between xfbno, daddr, filesystem block, and basic-block units; tests should assert round-trip conversion and block-size assumptions.  Config-gated builds should verify both enabled and disabled compilation paths and ensure callers do not rely on memory-btree APIs when the feature is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.c

## Purpose
This file implements staged btree construction and bulk loading.  It lets callers build a completely new AG-rooted or inode-rooted btree behind a fake root, using preallocated blocks, then atomically commit the new root into normal metadata.  This is important for online repair and rebuild paths because a partially loaded tree must not become visible through primary filesystem roots.

## Important APIs And Functions
`xfs_btree_stage_afakeroot` and `xfs_btree_commit_afakeroot` switch an AG-rooted cursor into and out of staging mode.  `xfs_btree_stage_ifakeroot` and `xfs_btree_commit_ifakeroot` do the same for inode-rooted btrees, redirecting the cursor to a fake inode fork and staging fork id.  `xfs_btree_bload_compute_geometry` calculates final height and block count from record count, min/max geometry, root constraints, and slack.  `xfs_btree_bload` creates all leaf and node blocks, fills records, derives parent keys, links siblings, writes delayed buffers, and records the fake root state.

Internal helpers include `xfs_btree_bload_prep_block`, `xfs_btree_bload_leaf`, `xfs_btree_bload_node`, `xfs_btree_bload_level_geometry`, `xfs_btree_bload_ensure_slack`, `xfs_btree_bload_max_npb`, `xfs_btree_bload_desired_npb`, and `xfs_btree_bload_drop_buf`.

## Control Flow
A caller initializes a fake root and staging cursor, configures `struct xfs_btree_bload`, computes geometry, preallocates all blocks, then calls `xfs_btree_bload`.  The loader starts at level zero, calculates how many records each leaf should receive, repeatedly claims/prepares a block, invokes the caller's sorted-record callback to fill it, and remembers the leftmost child pointer.  For each higher level, it creates node blocks whose key/pointer entries are derived by reading child blocks and calling `xfs_btree_get_keys`; sibling pointers chain blocks left-to-right.  After the last level, the fake root is updated with root block, height, and block count.  Dirty buffers are submitted at thresholds or at the end.

Inode-rooted btrees are special: a root can live in the fake inode fork, so geometry is recomputed to distinguish root-block capacity from normal block capacity.  `iroot_size` allocates the in-core root buffer, and inode btree `nr_blocks` excludes that root.

## State And Persistence Behavior
Staging mode sets `XFS_BTREE_STAGING`, clears normal transaction use during construction, and redirects root storage to `xbtree_afakeroot` or `xbtree_ifakeroot`.  Bulk loading uses a local delayed-write buffer list and marks buffers uptodate before queuing them.  Callers must preallocate blocks and provide `claim_block`, so the loader should not hit ENOSPC midway.  Commit functions do not log root changes themselves; callers must log the owning AG or inode metadata before converting the cursor back to normal transaction-backed operation.

## Dependencies And Integration Points
This file relies on the generic btree layout helpers, block initialization, sibling setters, key derivation, buffer read/get helpers, transaction-independent delayed write APIs, and tree-specific callbacks from `struct xfs_btree_bload`.  It integrates with online repair rebuild flows and with the guardrails in `xfs_btree.c` that reject normal allocation/freeing for staging cursors.

## Risks And Test Signals
Risks include unsorted records from `get_records`, wrong preallocation counts, incorrect slack causing overfull or under-minimum blocks, failure to submit/cancel delayed buffers, root capacity miscalculation for inode btrees, and exposing fake-root state before the owner metadata is logged.  Tests should cover zero records, one-block roots, multi-level trees, uneven record distribution, negative and excessive slack, inode roots with and without records, dirty threshold flushing, `claim_block` and `get_records` failures, and post-build verification of sibling chains and parent low/high keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.h

## Purpose
This header declares the fake-root structures and bulk-load interface for staged btree rebuilds.  It is the public contract between concrete repair/rebuild code and the staging implementation in `xfs_btree_staging.c`.

## Important APIs And Types
`struct xbtree_afakeroot` stores an AG-rooted staged tree's root AG block number, height, and block count.  `struct xbtree_ifakeroot` stores a fake inode fork pointer, block count, height, and available fork size for inode-rooted staged trees.

`xfs_btree_stage_afakeroot`, `xfs_btree_commit_afakeroot`, `xfs_btree_stage_ifakeroot`, and `xfs_btree_commit_ifakeroot` switch existing cursors between normal and fake-root operation.  The bulk-load callback types define three caller responsibilities: `get_records` must provide sorted records into a leaf block, `claim_block` must hand out preallocated blocks, and `iroot_size` must size inode root memory when needed.

`struct xfs_btree_bload` is the bulk-load control block.  Inputs include callbacks, record count, leaf/node slack, flush threshold, and private geometry constraints from the cursor.  Outputs include computed block count, final height, and dirty-buffer accounting.

## Control Flow And State
The expected flow is stage cursor, compute geometry, preallocate `nr_blocks`, bulk-load blocks, log owner metadata, and commit fake root.  The header encodes the staged state shape but leaves concrete btree-specific setup and root logging to callers.

## Dependencies, Risks, And Test Signals
This interface depends on generic btree cursors, XFS inode forks, transactions, and buffers.  Risks center on callback contracts: records must be sorted, block claims must match computed geometry, and inode root sizing must match actual block layout.  Tests should verify fake-root initialization, commit restoration of cursor fields, geometry outputs for representative trees, and error handling for callbacks that fail partway through a load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_cksum.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_cksum.h

## Purpose
This header provides inline CRC32c checksum helpers for XFS metadata buffers whose checksum field lives inside the covered buffer.  It supports both verification without modifying the buffer and update paths that temporarily zero the checksum field.

## Important APIs And Functions
`XFS_CRC_SEED` is the initial CRC32c seed.  `xfs_start_cksum_safe` computes the intermediate CRC by checksumming bytes before the checksum field, checksumming a local zero value in place of the field, and then checksumming the remaining bytes.  `xfs_start_cksum_update` writes zero into the buffer checksum field and computes CRC over the whole buffer in one pass.  `xfs_end_cksum` converts the intermediate CRC to the stored little-endian inverted format.  `xfs_update_cksum` writes the final checksum to the buffer, and `xfs_verify_cksum` compares the stored checksum with a safely computed value.

## Control Flow And State
The safe verification flow is non-mutating and is appropriate when callers do not have exclusive write access.  The update flow mutates the checksum field and therefore requires exclusive buffer access.  The only persistent state affected is the checksum field at `cksum_offset`; all other computation is local.

## Dependencies And Integration Points
The helpers depend on `crc32c`, endian conversion, and XFS integer types.  They are used by buffer-level metadata checksum helpers, including btree block CRC functions in `xfs_btree.c` through `xfs_buf_update_cksum` and `xfs_buf_verify_cksum`.

## Risks And Test Signals
Risks include passing a bad offset/length pair, using the mutating update helper without exclusive access, or confusing host-endian CRC values with on-disk little-endian inverted storage.  Tests should verify stable checksums across endian assumptions, safe verification that leaves buffers unchanged, update-then-verify cycles, corruption detection when any covered byte changes, and boundary offsets near the start or end of a metadata buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_cksum.h -->
