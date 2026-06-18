# Group Research: group_1874_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_alloc_c_sources_local_8f08dc3e2434

Scope: `Docs/research_subset_a.md`; source tree `sources/local-fs/xfsprogs`.

Files researched completely:
- `sources/local-fs/xfsprogs/libxfs/xfs_alloc.c`
- `sources/local-fs/xfsprogs/libxfs/xfs_alloc.h`
- `sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.c`
- `sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.h`
- `sources/local-fs/xfsprogs/libxfs/xfs_attr.c`
- `sources/local-fs/xfsprogs/libxfs/xfs_attr.h`

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc.c

## Purpose

`xfs_alloc.c` is the core allocation-group free-space manager for libxfs. It owns AGF/AGFL verification and update paths, allocation from the paired free-space btrees, free-space insertion/merge, per-AG freelist refill/shrink, top-level extent allocation wrappers, deferred extent-free item creation, and AGFL walking/query helpers.

## Key Areas

- Maintains bnobt and cntbt free-space btrees, including lookup/update/delete/insert operations and record validation.
- Implements exact, near, anywhere-in-AG, and whole-filesystem allocation paths.
- Handles busy extent trimming and retry through `xfs_extent_busy_trim` / `xfs_extent_busy_flush`.
- Frees extents by merging left/right neighboring free-space records and updating both btrees.
- Verifies and logs AGF and AGFL buffers, including CRC, UUID, LSN, level, length, and ring-index checks.
- Refills or shrinks the AGFL before allocation/free operations with `xfs_alloc_fix_freelist`.
- Updates reverse mappings unless owner info explicitly skips rmap updates.
- Queues deferred extent frees and supports paused autoreap items for crash-safe rollback of new allocations.
- Exposes query helpers for free-space records and AGFL walking.

## Main Control Flow

Allocation flows through `xfs_alloc_vextent_*` wrappers. Shared preflight normalizes arguments, checks AG lock-order constraints, fixes the AG freelist, and prepares AGF/perag state. The actual AG allocation then uses one of the lower-level algorithms:

- `xfs_alloc_ag_vextent_exact` finds the containing bnobt record and allocates only if the target range is free and non-busy.
- `xfs_alloc_ag_vextent_near` uses a multi-cursor locality search over cntbt and bnobt.
- `xfs_alloc_ag_vextent_size` uses cntbt best-fit allocation when locality is not important.
- `xfs_alloc_ag_vextent_small` handles fallback to the largest small extent or a single AGFL block.

Successful allocation finishes in `xfs_alloc_vextent_finish`, which sets `fsbno`, updates rmap, decrements free counters, consumes AG reservation accounting, records stats, and drops perag references if needed.

Freeing flows through `__xfs_free_extent`, which fixes the freelist, validates the extent against the AGF, calls `xfs_free_ag_extent`, and inserts the freed range into the busy extent list.

## Important Invariants

- bnobt and cntbt must describe exactly the same free extents.
- `agf_longest` and `pagf_longest` must track the largest cntbt record.
- AGF free block counters cannot exceed AG length.
- AGFL count/ring fields must stay within `xfs_agfl_size`.
- Allocations must preserve AGFL minimums, per-AG reservations, and caller `minleft`.
- Allocation attempts must respect `t_highest_agno` to avoid AGF lock ordering deadlocks.
- Btree block allocation/free must go through AGFL and maintain allocbt block counters.
- Corruption paths mark the relevant AG or btree sick and return `-EFSCORRUPTED`.

## Dependencies

This file integrates generic btree code, allocation btree constructors, transaction/buffer logging, perag state, rmap updates, AG reservations, busy extents, deferred-intent infrastructure, health marking, and tracepoints.

## Risk Areas

AGFL refill/shrink and btree split/join behavior are transaction-sensitive. Busy extent retry behavior affects allocation correctness under delayed free pressure. Any change to free-space btree updates, `agf_longest`, or AG lock ordering can cause allocator corruption, false ENOSPC, or deadlocks.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc.h

## Purpose

`xfs_alloc.h` declares the public allocation/free-space API for libxfs allocation-group management. It exposes allocation arguments, allocator flags, free-space btree query helpers, AGF/AGFL accessors, deferred extent-free interfaces, and allocation cache lifecycle hooks.

## Key Types

- `struct xfs_alloc_arg`: central argument/result carrier for allocation routines. It includes transaction, mount, AGF buffer, perag, target fsblock/AG/AG block, min/max/prod/mod/alignment constraints, minleft/total reservation pressure, NEAR allocation AG block bounds, output length, allocation datatype, delayed-allocation hints, freelist source flag, exact-minlen debug flag, owner info, and AG reservation type.
- `struct xfs_extent_free_item`: deferred free work item sorted by start block. It records owner, start block, block count, group, flags, and AG reservation.
- `struct xfs_alloc_autoreap`: handle for a paused deferred free pending item used to autoreap allocations if a later operation fails or recovery completes it.
- `xfs_alloc_query_range_fn` and `xfs_agfl_walk_fn`: callbacks for btree free-space record queries and AGFL walks.

## Exported APIs

- Allocation: `xfs_alloc_vextent_this_ag`, `xfs_alloc_vextent_near_bno`, `xfs_alloc_vextent_exact_bno`, `xfs_alloc_vextent_start_ag`, `xfs_alloc_vextent_first_ag`.
- Freeing: `__xfs_free_extent`, `xfs_free_extent`, `xfs_free_ag_extent`, `xfs_free_extent_later`, `xfs_free_extent_fix_freelist`.
- AG metadata: `xfs_agfl_size`, `xfs_alloc_set_aside`, `xfs_alloc_ag_max_usable`, `xfs_prealloc_blocks`, `xfs_alloc_longest_free_extent`, `xfs_alloc_min_freelist`, `xfs_alloc_compute_maxlevels`, `xfs_alloc_log_agf`, `xfs_read_agf`, `xfs_alloc_read_agf`, `xfs_alloc_read_agfl`, `xfs_alloc_fix_freelist`, `xfs_alloc_get_freelist`, `xfs_alloc_put_freelist`, `xfs_validate_ag_length`.
- Btree/query: `xfs_alloc_lookup_le`, `xfs_alloc_lookup_ge`, `xfs_alloc_get_rec`, `xfs_alloc_btrec_to_irec`, `xfs_alloc_check_irec`, `xfs_alloc_query_range`, `xfs_alloc_query_all`, `xfs_alloc_has_records`, `xfs_agfl_walk`.
- Autoreap/cache: `xfs_alloc_schedule_autoreap`, `xfs_alloc_cancel_autoreap`, `xfs_alloc_commit_autoreap`, `xfs_extfree_intent_init_cache`, `xfs_extfree_intent_destroy_cache`.

## Flags

The header defines freelist fix flags such as `TRYLOCK`, `FREEING`, `NORMAP`, `NOSHRINK`, `CHECK`, and `TRYFLUSH`; allocation datatype flags for user data, initial user data, and no-busy behavior; and deferred free flags for skip-discard and realtime frees.

## Integration Notes

The header is consumed by allocation, bmap, repair, scrub/query, transaction, and allocation btree code. Repair-specific `NORMAP` and `NOSHRINK` flags are part of the shared libxfs contract.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.c

## Purpose

`xfs_alloc_btree.c` adapts the generic XFS btree engine to the two allocation free-space btrees: bnobt, ordered by start block, and cntbt, ordered by block count then start block. It defines cursor operations, block allocation/free callbacks, record/key comparisons, verifiers, buffer ops, cursor constructors, staged btree commit support, max record/height calculations, and cursor cache lifecycle.

## Key Areas

- Duplicates bnobt/cntbt cursors with the same mount, transaction, AGF buffer, and perag.
- Sets AGF root pointers and level counters for either free-space tree.
- Allocates btree blocks from AGFL and returns freed btree blocks to AGFL.
- Maintains `m_allocbt_blks`, AGF btree block counters, and busy extent state.
- Converts cursor records to disk records and initializes keys/pointers.
- Defines comparison and ordering semantics for bnobt and cntbt.
- Verifies btree blocks, including CRC-enabled headers and level bounds.
- Exports `xfs_bnobt_buf_ops`, `xfs_cntbt_buf_ops`, `xfs_bnobt_ops`, and `xfs_cntbt_ops`.
- Constructs live and staged btree cursors.
- Commits staged btree fake roots to AGF.
- Calculates max records, max levels, and estimated btree size.
- Creates/destroys the allocation btree cursor cache.

## Btree Semantics

bnobt is ordered by start block. Its record-order check permits adjacent extents but rejects overlap. cntbt is ordered by block count and then start block. Both trees share the same record format but differ in comparison, high-key generation, and usefulness of key-contiguity checks.

## Verification

`xfs_allocbt_verify` checks magic values, v5 headers, perag tree levels when available, online-repair temporary levels when enabled, mount maximum levels otherwise, and generic AG btree block structure. Read/write verifiers attach CRC and corruption reporting.

## Risk Areas

The file is small but central: choosing the wrong op table, weakening ordering checks, or mishandling AGFL block allocation/free would corrupt free-space accounting. Verifier level checks must keep supporting growfs, recovery, and repair contexts where perag state can be missing or temporarily divergent.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.h

## Purpose

`xfs_alloc_btree.h` declares on-disk layout access macros and public helpers for XFS allocation free-space btrees. It is the interface between allocation code, repair/staging code, and the generic btree implementation.

## Contents

- `XFS_ALLOC_BLOCK_LEN(mp)` selects CRC or non-CRC short btree header length.
- `XFS_ALLOC_REC_ADDR`, `XFS_ALLOC_KEY_ADDR`, and `XFS_ALLOC_PTR_ADDR` compute 1-based record, key, and pointer addresses inside allocation btree blocks.
- `xfs_bnobt_init_cursor` and `xfs_cntbt_init_cursor` construct bno/count free-space btree cursors.
- `xfs_allocbt_maxrecs`, `xfs_allocbt_calc_size`, and `xfs_allocbt_maxlevels_ondisk` expose btree geometry calculations.
- `xfs_allocbt_commit_staged_btree` installs a staged allocation btree root into AGF.
- `xfs_allocbt_init_cur_cache` and `xfs_allocbt_destroy_cur_cache` manage cursor cache allocation.

## Integration Notes

Some layout macros are explicitly retained for userspace even if they appear unused in kernel-style builds. The header forward-declares staging support through `xbtree_afakeroot`, reflecting repair/rebuild usage.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr.c

## Purpose

`xfs_attr.c` implements high-level extended attribute get/set/remove/replace operations for XFS. It dispatches between shortform, single-leaf, and node/remote-value formats; computes transaction reservations; manages resumable delayed attribute intents; handles atomic replacement semantics; and validates namespaces and names.

## Storage Formats

- Shortform attributes are packed into the inode attr fork.
- Leaf attributes occupy one attr fork block.
- Node attributes use DA btrees and can include remote value blocks.
- A single leaf with remote value extents can look like node format to higher-level checks.

## Read Path

`xfs_attr_get` prepares owner, geometry, fork, hash, and lookup flags, takes the attr-map lock, and calls `xfs_attr_get_ilocked`. The locked getter loads attr fork extents and dispatches to shortform, leaf, or node retrieval. Node retrieval uses DA state and releases all path buffers before returning.

## Mutation Path

`xfs_attr_set` is the public mutator. It determines remove/upsert/create/replace semantics, calculates reservations and remote block needs, adds an attr fork if required, allocates an inode transaction, reserves incore attr extent growth, looks up the existing attr, enforces operation semantics, then either performs a shortform shortcut or queues deferred attr work. It updates ctime, logs inode core, commits, unlocks, and clears `args->trans`.

## Delayed State Machine

`xfs_attr_set_iter` drives resumable attr operations through `xattri_dela_state`. It handles shortform/leaf/node adds and removes, remote value allocation, replacement flag flipping, old remote block removal, and final old-name removal. It returns after work that requires transaction rolling and resumes from the stored state.

Important state groups include initial add/remove states, leaf/node remote allocation states, replacement flip states, old remote removal states, old attr removal states, and `XFS_DAS_DONE`.

## Shortform, Leaf, and Node Behavior

- Shortform add can create the shortform list, replace by removing old entry first, and fall back to leaf conversion on `-ENOSPC`.
- Leaf add enforces create/replace semantics, can save old remote metadata for replacement, and converts to node if insertion does not fit.
- Node add locates insertion/replacement position, inserts into the target leaf, splits DA btree nodes when needed, or converts a remote-value leaf into true node form.
- Leaf and node remove paths mark remote attrs incomplete before removing remote blocks and can shrink back to shortform when contents fit.

## Replacement and Remote Values

Atomic replacement depends on incomplete flags. New and old entries are flipped so one appears while the other disappears atomically. Old remote block metadata is saved and restored through secondary fields. Parent-pointer replacement has special name/value swapping via `xfs_attr_update_pptr_replace_args`.

Remote allocation and removal proceed in resumable transaction-sized steps through attr remote helpers.

## Validation and Hashing

`xfs_attr_hashval` delegates parent-pointer attrs to parent-pointer hashing and otherwise hashes names normally. `xfs_attr_check_namespace` permits at most one namespace bit. `xfs_attr_namecheck` checks namespace validity, maximum name length, embedded NULs for normal attrs, and parent-pointer-specific validation.

## Dependencies

The file depends on DA btree code, attr shortform/leaf/remote helpers, inode fork and bmap code, transaction reservations, quota expectations, deferred intents, parent pointer helpers, tracepoints, and mount feature flags.

## Risk Areas

The delayed attr state enum is order-sensitive because several paths advance by incrementing state. Replacement crash consistency relies on incomplete flags and transaction boundaries. Remote value state must preserve block metadata correctly across rolls. Shortform fast paths must fall back without losing create/replace semantics.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr.h

## Purpose

`xfs_attr.h` declares the XFS extended attribute interface, list context, delayed attribute state machine, attr intent structure, update operation enum, hashing helpers, namespace/name validation, and internal helpers shared across libxfs attr implementation files.

## Main Types

- `struct xfs_attrlist_cursor_kern`: internal listing cursor with hash value, block, equal-hash offset, ABI padding, and initialized flag.
- `struct xfs_attr_list_context`: carries transaction, inode, list cursor, output buffer, abort/error state, incomplete-entry policy, buffer counters, namespace filter, resync state, list-entry callback, and output index.
- `enum xfs_delattr_state`: resumable delayed attr states for shortform/leaf/node add/remove, remote allocation, replacement, old remote removal, old attr removal, and done.
- `struct xfs_attr_intent`: deferred attr work item containing list linkage, DA state, DA args, shared logged name/value storage, current delayed state, operation flags, and remote allocation progress.
- `enum xfs_attr_update`: public mutation modes: remove, upsert, create, replace.

## State Machine Documentation

The header contains detailed diagrams for attr remove and set operations. They document where `-EAGAIN` causes transaction roll/reentry, which states belong to subroutines, and how set/replace/remove flows progress through shortform, leaf, node, remote-block, flag-flip, and cleanup phases.

The enum ordering is part of the implementation contract: leaf and node sequences are parallel, and implementation code advances through some phases by incrementing the state value.

## Public APIs

- Attr lifecycle and listing: `xfs_attr_inactive`, `xfs_attr_list_ilocked`, `xfs_attr_list`.
- Lookup/get: `xfs_inode_hasattr`, `xfs_attr_is_leaf`, `xfs_attr_get_ilocked`, `xfs_attr_get`.
- Mutation: `xfs_attr_set`, `xfs_attr_set_iter`, `xfs_attr_remove_iter`.
- Validation/sizing: `xfs_attr_check_namespace`, `xfs_attr_namecheck`, `xfs_attr_calc_size`, `xfs_attr_set_resv`.
- Hashing: `xfs_attr_hashname`, `xfs_attr_hashval`, `xfs_attr_sethash`.
- Fork/format helpers: `xfs_attr_sf_totsize`, `xfs_attr_add_fork`, `xfs_attr_setname`, `xfs_attr_removename`, `xfs_attr_replacename`.
- Cache lifecycle: `xfs_attr_intent_init_cache`, `xfs_attr_intent_destroy_cache`.

## Inline Helpers

- `xfs_attr_is_shortform` treats local attr format or zero-extent extents format as shortform/nonexistent attr data.
- `xfs_attr_init_add_state` sets `XFS_DA_OP_ADDNAME` and chooses shortform, leaf, node, or done.
- `xfs_attr_init_remove_state` chooses the matching remove state for the current format.
- `xfs_attr_init_replace_state` chooses remove-first for logged attrs and add-first otherwise.
- `xfs_attr_sethash` stores the hash in `args->hashval`.

## Risk Areas

Logged replacement semantics depend on remove-first ordering. Namespace validation deliberately checks for fewer than two namespace bits, not exactly one. The no-attr-fork special case in `xfs_attr_init_add_state` supports pure remove completion. Reordering delayed states or changing inline state helpers can break transaction-roll resumption.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr.h -->