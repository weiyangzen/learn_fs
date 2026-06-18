# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr.h

## Purpose
`xfs_attr.h` is the public libxfs interface and contract for XFS extended attribute operations. It declares the attribute-list cursor context, delayed attribute intent structure, update operation enum, delayed state enum, state initialization helpers, hash helpers, and public get/set/list/remove entry points used across XFS.

## Important APIs, types, and functions
The header defines `ATTR_MAX_VALUELEN`, `struct xfs_attrlist_cursor_kern`, `put_listent_func_t`, `struct xfs_attr_list_context`, `enum xfs_delattr_state`, `XFS_DAS_STRINGS`, `struct xfs_attr_intent`, and `enum xfs_attr_update`.

`struct xfs_attr_list_context` carries list operation state: transaction and inode, cursor, output buffer, stop/error indicator, incomplete-entry visibility, duplicate hash count, output size accounting, namespace filter, resync flag, emitter callback, and index. `struct xfs_attr_intent` is the deferred-operation context, containing list linkage, optional da-state, args pointer, logged name/value backing, delayed state, operation flags, current remote logical block/count, and current bmap record.

Static helpers `xfs_attr_is_shortform`, `xfs_attr_init_add_state`, `xfs_attr_init_remove_state`, and `xfs_attr_init_replace_state` encode initial state selection. `xfs_attr_sethash` computes the namespace-aware hash through `xfs_attr_hashval`.

## Control flow
The state diagrams embedded in the header document how multi-transaction set and remove operations resume after transaction rolls. Initial add/remove states are format-specific: shortform, leaf, or node. For replace, `xfs_attr_init_replace_state` sets add and replace flags; logged replacements start with removal of old state so recovery can replay from logged name/value information, while unlogged replacements start with adding the new incomplete entry.

The delayed state enum deliberately groups leaf and node remote sequences in matching order. Implementation code in `xfs_attr.c` increments states to advance from find-space to allocate-remote to replace/remove phases, so the order here is not merely descriptive.

## State and persistence behavior
The header itself stores no persistent data, but it defines the durable protocol used by the implementation: incomplete flags protect partially initialized or partially removed attrs, remote value allocation/removal can span multiple transactions, and `xfs_attr_intent` fields record enough in-memory/logged intent state to resume an operation. `XFS_DA_OP_LOGGED`, `XFS_DA_OP_REPLACE`, and attr intent operation flags determine whether operations are recoverable and which state is selected.

## Dependencies and integration points
Consumers include the attr core, attr leaf implementation, attr remote implementation, attr item logging, list/inactive code, xattr VFS front end, handle/parent pointer code, tracepoints, and repair/recovery code. The header forward-declares `struct xfs_inode`, `struct xfs_da_args`, and `struct xfs_attr_list_context`, but relies on format and log headers for constants such as `XFS_ATTRI_OP_FLAGS_*`, `XFS_ATTR_NSP_ONDISK_MASK`, and fork formats.

## Risks and edge cases
Because state enum ordering is part of executable behavior, inserting or reordering states can break delayed operations. The helper `xfs_attr_init_add_state` has a special null attr-fork case for pure remove completion; callers must not assume an attr fork always exists. `xfs_attr_is_shortform` treats an empty extents-format attr fork as shortform for upgrade decisions, which must match implementation expectations. Parent pointer replacement uses separate old and new names/values, so intent operation decoding and hash initialization must be consistent.

## Test signals
Compile-time users should exercise every declared operation path. Runtime tests should stress delayed state replay, logged attr replacement recovery, parent pointer replace, attr list cursor resync across duplicate hashes, and state-string traceability. Static analysis should check all switch statements over `enum xfs_delattr_state` after any enum edit.
