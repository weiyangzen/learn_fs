# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr.c

## Purpose
`xfs_attr.c` is the high-level libxfs extended-attribute coordinator. It exposes the core get/set/update entry points, chooses between inline shortform attributes, single leaf blocks, and node-format da-btrees, and drives delayed attribute intent state machines for operations that need multiple transactions. It does not implement the packed leaf record format or remote value I/O directly; it calls `xfs_attr_leaf.c` and `xfs_attr_remote.c` for those details.

## Important APIs, types, and functions
The main public entry points are `xfs_inode_hasattr`, `xfs_attr_is_leaf`, `xfs_attr_get_ilocked`, `xfs_attr_get`, `xfs_attr_set`, `xfs_attr_set_iter`, `xfs_attr_setname`, `xfs_attr_removename`, `xfs_attr_replacename`, `xfs_attr_add_fork`, `xfs_attr_calc_size`, `xfs_attr_set_resv`, `xfs_attr_hashname`, `xfs_attr_hashval`, `xfs_attr_check_namespace`, `xfs_attr_namecheck`, `xfs_attr_intent_init_cache`, `xfs_attr_intent_destroy_cache`, and `xfs_attr_sf_totsize`.

Internal format-specific paths include `xfs_attr_try_sf_addname`, `xfs_attr_sf_addname`, `xfs_attr_shortform_addname`, `xfs_attr_leaf_addname`, `xfs_attr_leaf_get`, `xfs_attr_leaf_removename`, `xfs_attr_node_addname`, `xfs_attr_node_addname_find_attr`, `xfs_attr_node_try_addname`, `xfs_attr_node_lookup`, `xfs_attr_node_get`, `xfs_attr_node_removename_setup`, `xfs_attr_node_remove_attr`, `xfs_attr_leaf_remove_attr`, and `xfs_attr_leaf_shrink`.

The file uses `struct xfs_da_args` as the shared operation descriptor. Important fields include `dp`, `trans`, `geo`, `whichfork`, `owner`, `op_flags`, `attr_filter`, `hashval`, `index`, `blkno`, remote value fields, and duplicate remote fields suffixed with `2` for replace/remove choreography. Delayed work lives in `struct xfs_attr_intent`, allocated from `xfs_attr_intent_cache`.

## Control flow
`xfs_attr_get` validates shutdown state, fills `owner`, geometry, fork, and hash, takes the shared attr mapping lock, and calls `xfs_attr_get_ilocked`. The locked path reads attr-fork extents, then dispatches to shortform, leaf, or node lookup.

`xfs_attr_set` is the main mutation entry point. It computes reservations for create/upsert/replace/remove, creates an attr fork if needed, allocates a transaction against the inode, reserves incore extent capacity, probes existing state through `xfs_attr_lookup`, and then dispatches to set, remove, or replace helper paths. Small shortform-only operations can complete in the current transaction. Larger operations enqueue delayed attr work with `xfs_attr_defer_add`, after which `xfs_attr_set_iter` advances the intent state machine across transaction rolls.

`xfs_attr_set_iter` is the core multi-transaction switch. Initial states add/remove from shortform, leaf, or node formats. Remote states first find space, then allocate attr-fork extents in chunks, then write values and clear or flip `INCOMPLETE` flags. Replace states atomically flip visibility between old and new entries before removing old remote blocks and the old name. Node removal first marks the leaf entry incomplete and invalidates remote buffers, then unmaps remote blocks and removes the name from the da-tree.

## State and persistence behavior
This file orchestrates persistent changes to the attr fork and inode core through transactions. Shortform updates alter inline inode fork bytes and log `XFS_ILOG_CORE | XFS_ILOG_ADATA`. Leaf/node changes log buffers through leaf helpers. Remote values are protected by creating a leaf entry with `XFS_ATTR_INCOMPLETE`, writing remote blocks synchronously through remote helpers, and clearing the incomplete bit only after values are safely stored. Replace uses `xfs_attr_save_rmt_blk`, `xfs_attr_restore_rmt_blk`, and `xfs_attr_complete_op` to track old and new entries and provide an atomic visible switch.

`xfs_attr_add_fork` persists creation of the attr fork with `xfs_bmap_add_attrfork`. `xfs_attr_set` updates inode change time, logs inode core, honors wsynced mounts, and commits or cancels the transaction. Recovery behavior is visible through `XFS_DA_OP_RECOVERY`, where missing removal targets can be tolerated because recovery may be cleaning partial state.

## Dependencies and integration points
The file depends on da-btree traversal and split/join (`xfs_da3_node_lookup_int`, `xfs_da3_split`, `xfs_da3_join`, `xfs_da_state_*`), bmap and transaction code (`xfs_bmap_*`, `xfs_iext_count_extend`, `xfs_trans_*`), format-specific leaf functions, remote value helpers, quota/reservation definitions, tracepoints, parent pointer hashing/name validation, and attr intent logging in `xfs_attr_item.h`. Declared but externally implemented APIs such as `xfs_attr_list`, `xfs_attr_list_ilocked`, `xfs_attr_remove_iter`, and `xfs_attr_inactive` are integration points with sibling XFS files.

## Risks and edge cases
The highest-risk behavior is the delayed operation state machine: enum ordering is relied upon by `++attr->xattri_dela_state`, and leaf/node remote state sequences must stay aligned. Atomic replace depends on correctly preserving old entry location and remote extent state while adding the new entry. Leaf-versus-node detection is subtle because a single leaf with remote blocks can look like a multi-block attr fork. Remote block cleanup must keep returning and handling `-EAGAIN` without losing progress. Namespace validation matters because attr hash and parent-pointer semantics differ. Any missed `xfs_trans_brelse`, stale da-state, or incorrect incomplete-flag handling can lead to leaks, hidden attributes, or recovery-visible corruption.

## Test signals
Useful tests include create/upsert/replace/remove for shortform, leaf, and node attrs; transitions shortform-to-leaf, leaf-to-node, node-to-leaf/shortform; remote values around local/remote threshold and maximum length; logged replace and parent pointer replace; crash/recovery at each incomplete-flag transition; ENOSPC during fork creation, split, and remote allocation; fsx/xfstests xattr coverage with CRC and non-CRC filesystems; corruption tests for namespace masks and invalid names; and trace assertions that delayed states reach `XFS_DAS_DONE` without leaking da-state or transactions.
