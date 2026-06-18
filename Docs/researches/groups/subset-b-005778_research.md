# Research: subset-b-005778 XFS libxfs attribute core

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.c

## Purpose
`xfs_attr_leaf.c` implements the storage formats and algorithms for inline shortform attributes and leaf blocks in the XFS attribute fork. It handles leaf block verification, endian conversion, shortform add/remove/get/verify, conversion between shortform, leaf, and node formats, leaf block creation, insertion, deletion, split/rebalance/unbalance, lookup, value extraction, and `INCOMPLETE` flag manipulation.

## Important APIs, types, and functions
Header conversion and verification are handled by `xfs_attr3_leaf_hdr_from_disk`, `xfs_attr3_leaf_hdr_to_disk`, `xfs_attr3_leaf_header_check`, `xfs_attr3_leaf_read`, and the `xfs_attr3_leaf_buf_ops` verifier set. Shortform operations include `xfs_attr_shortform_bytesfit`, `xfs_attr_shortform_create`, `xfs_attr_sf_findname`, `xfs_attr_shortform_replace`, `xfs_attr_shortform_add`, `xfs_attr_fork_remove`, `xfs_attr_sf_removename`, `xfs_attr_shortform_getvalue`, `xfs_attr_shortform_to_leaf`, `xfs_attr_shortform_allfit`, and `xfs_attr_shortform_verify`.

Leaf and node-format operations include `xfs_attr3_leaf_to_shortform`, `xfs_attr3_leaf_to_node`, `xfs_attr3_leaf_init`, `xfs_attr3_leaf_split`, `xfs_attr3_leaf_add`, `xfs_attr3_leaf_remove`, `xfs_attr3_leaf_toosmall`, `xfs_attr3_leaf_unbalance`, `xfs_attr3_leaf_lookup_int`, `xfs_attr3_leaf_getvalue`, `xfs_attr_leaf_lasthash`, `xfs_attr_leaf_order`, `xfs_attr_leaf_newentsize`, `xfs_attr3_leaf_clearflag`, `xfs_attr3_leaf_setflag`, and `xfs_attr3_leaf_flipflags`.

Important internal helpers include `xfs_attr_leaf_entries_end`, `xfs_attr_leaf_ichdr_freemaps_verify`, firstused disk conversion helpers, `xfs_attr3_leaf_verify_entry`, `xfs_attr3_leaf_verify`, namespace/value match helpers, `xfs_attr_copy_value`, `xfs_attr3_leaf_create`, `xfs_attr3_leaf_add_work`, `xfs_attr3_leaf_compact`, `xfs_attr3_leaf_rebalance`, `xfs_attr3_leaf_figure_balance`, `xfs_attr3_leaf_moveents`, and `xfs_attr_leaf_entsize`.

## Control flow
Shortform paths manipulate inode-local packed records directly. `xfs_attr_shortform_bytesfit` determines if a byte count fits in inode literal space while preserving data fork room. `xfs_attr_shortform_add` appends a variable-length record and updates `i_forkoff`; removal compacts the inline array and may remove the attr fork entirely if empty and safe. `xfs_attr_shortform_to_leaf` snapshots inline data, clears local fork data, grows the attr fork, creates block zero as a leaf, and reinserts each shortform entry into the new leaf.

Leaf add first loads the incore leaf header, calculates whether the new value is local or remote, searches the three-entry freemap, optionally compacts the block, and inserts a sorted entry. If a leaf cannot fit the new entry, split/rebalance logic allocates a new leaf and redistributes records. Node conversion copies the existing leaf to a new block and creates a root da-node at block zero that points to the copied leaf.

Lookup performs a binary search by hash, backs up to the first equal hash, then scans duplicate hashes for exact namespace/name/value match. Getvalue copies local values immediately or sets remote fields and delegates to `xfs_attr_rmtval_get` through `xfs_attr_copy_value`.

## State and persistence behavior
Leaf blocks store sorted `xfs_attr_leaf_entry` arrays growing forward from the header and name/value payloads growing backward from the block tail. The incore header uses a 32-bit `firstused` so 64 KiB attr blocks can be represented even though on-disk fields are 16-bit; zero is the special on-disk value for an empty max-size block. Free space is tracked by three freemap entries and a holes flag. All mutating paths log modified buffer ranges or full buffers through the transaction.

Crash-safe remote and replace behavior is centered on `XFS_ATTR_INCOMPLETE`. Adding a remote value creates an incomplete leaf entry before writing remote blocks. `xfs_attr3_leaf_clearflag` publishes it and stores the remote block/length. `xfs_attr3_leaf_setflag` hides an old entry before removal. `xfs_attr3_leaf_flipflags` clears the new entry and sets the old entry incomplete in one transaction for atomic replacement.

## Dependencies and integration points
This file depends on da-btree routines for node creation, split/join coordination, sibling path movement, and block linking; bmap for local-to-extents conversion and fork shrink/grow; transaction logging; buffer verifiers and CRC support; remote value retrieval; parent pointer matching semantics; superblock attr2 feature updates; health marking for corrupt attr forks; and trace/error injection infrastructure.

## Risks and edge cases
The packed leaf format is vulnerable to off-by-one and overlap bugs. Verification checks sorted hashes, name bounds, nonzero names, remote value block presence for complete entries, freemap bounds/alignment/overlap, and header-vs-payload collision. Split/rebalance must update insertion indexes and old/new replace locations accurately, including double splits and cross-block replacements. Compaction drops holes but must preserve CRC-era header fields. Empty leaf blocks are permitted after crash during format conversion. Parent pointers match on both name and value and do not support remote values. Any mismatch between local/remote sizing thresholds and remote block allocation can corrupt attr visibility.

## Test signals
Tests should cover shortform fit boundaries, dev inode and btree data fork forkoff rules, shortform verify rejection, shortform-to-leaf and leaf-to-shortform conversion, empty leaf verifier acceptance, local and remote leaf lookup with duplicate hashes, leaf insertion/removal with freemap coalescing, compaction after holes, split/rebalance/unbalance with replacement state, CRC and non-CRC leaf verification, 64 KiB block firstused conversion, parent pointer matching, and crash points around clear/set/flip incomplete flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.h

## Purpose
`xfs_attr_leaf.h` declares the in-core attribute leaf header and the shortform/leaf/node helper API exported by `xfs_attr_leaf.c` to the rest of XFS. It is the interface boundary for manipulating leaf blocks, converting formats, and checking attr leaf buffer validity.

## Important APIs, types, and functions
The central type is `struct xfs_attr3_icleaf_hdr`, containing sibling links, magic, entry count, used bytes, 32-bit `firstused`, holes flag, and three freemap entries. The 32-bit `firstused` is an explicit abstraction over the 16-bit on-disk field.

Shortform declarations include creation, replacement, add, getvalue, conversion to leaf, removal, find-name, all-fit, bytes-fit, verifier, and fork removal APIs. Leaf/node declarations include conversion to node/shortform, incomplete flag operations, split, lookup, getvalue, add, remove, list, init, toosmall, unbalance, last hash, ordering, new entry sizing, leaf read, header conversion, and owner/header checking.

## Control flow
Callers in `xfs_attr.c` use these prototypes to dispatch by attr fork format. Da-btree code uses split, toosmall, unbalance, order, and last-hash helpers to maintain tree shape. Lookup and getvalue are leaf-buffer-local helpers used both by single-leaf and node-leaf paths. Conversion APIs move persistent data among inode-local shortform, block leaf, and da-node structures.

## State and persistence behavior
The header formalizes the incore state used to safely edit and log leaf blocks. `firstused`, `usedbytes`, `holes`, and `freemap[]` must match the packed on-disk leaf layout. Incomplete flag APIs are part of the persistence protocol for remote values and replace atomicity. Read and header-check APIs tie leaf buffers to verifiers and owners, particularly for CRC-enabled filesystems.

## Dependencies and integration points
The header forward-declares `xfs_da_args`, `xfs_da_state`, `xfs_da_state_blk`, `xfs_inode`, `xfs_trans`, and attr-list context to avoid heavy includes. It assumes format definitions for attr leaf map size and on-disk structures are already available from XFS format headers. It is consumed by the attr core, list handling, da-btree code, repair/recovery paths, and any code that initializes attr leaf buffers.

## Risks and edge cases
Changing `struct xfs_attr3_icleaf_hdr` semantics can silently break endian conversion and verifier assumptions. The API exposes low-level operations that require callers to hold the right transaction, inode locks, owner, geometry, and fork context. `xfs_attr3_leaf_list_int` is declared here but implemented in sibling list code, so linkage assumptions matter. `xfs_attr_leaf_newentsize` decides local versus remote storage by side effect through its `local` out parameter; callers must pass it consistently with reservation and remote allocation code.

## Test signals
Compile and link tests should ensure all declarations match implementation signatures. Functional tests should exercise every exported conversion and flag operation through higher-level xattr operations, plus direct verifier tests for malformed leaf headers, freemaps, and owner mismatches. Static checks should flag callers that invoke leaf APIs without transaction or attr geometry initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.c

## Purpose
`xfs_attr_remote.c` implements out-of-line storage for extended attribute values that do not fit inside an attr leaf block. Remote values live in data blocks mapped by the inode attribute fork. The file handles remote block sizing, v5 remote headers and CRC verification, synchronous value writes, value reads, buffer invalidation, extent allocation, and extent removal.

## Important APIs, types, and functions
Public functions include `xfs_attr3_rmt_buf_space`, `xfs_attr3_rmt_blocks`, `xfs_attr_rmtval_get`, `xfs_attr_rmt_find_hole`, `xfs_attr_rmtval_set_value`, `xfs_attr_rmtval_stale`, `xfs_attr_rmtval_find_space`, `xfs_attr_rmtval_set_blk`, `xfs_attr_rmtval_invalidate`, and `xfs_attr_rmtval_remove`. The buffer verifier is `xfs_attr3_rmt_buf_ops`.

Internal verification and copy helpers include `xfs_attr3_rmt_hdr_ok`, `xfs_attr3_rmt_verify`, `__xfs_attr3_rmt_read_verify`, read/write verifier wrappers, `xfs_attr3_rmt_verify_struct`, `xfs_attr3_rmt_hdr_set`, `xfs_attr_rmtval_copyout`, and `xfs_attr_rmtval_copyin`. The file uses a one-entry extent map batch size (`ATTR_RMTVALUE_MAPSIZE`) for remote reads.

## Control flow
For reads, `xfs_attr_rmtval_get` walks attr-fork mappings from `args->rmtblkno` for `args->rmtblkcnt`, reads each mapped buffer with remote verifier ops, translates disk ENODATA to EIO, copies value bytes out, and advances logical block, remaining block count, offset, and destination pointer.

For writes, delayed attr code first calls `xfs_attr_rmtval_find_space`, which finds an unused attr-fork hole and stores logical start/count in both args and intent. Repeated `xfs_attr_rmtval_set_blk` calls allocate mapped extents with `xfs_bmapi_write` and advance the intent cursor. After all extents are allocated, `xfs_attr_rmtval_set_value` maps the extents back, obtains buffers, fills headers and payload with `xfs_attr_rmtval_copyin`, and writes each buffer synchronously with `xfs_bwrite`.

For removal, `xfs_attr_rmtval_invalidate` walks mapped remote extents and marks incore buffers stale. `xfs_attr_rmtval_remove` calls `xfs_bunmapi` to unmap remote blocks, returning `-EAGAIN` until the bmap layer reports completion.

## State and persistence behavior
Remote attribute values are intentionally not logged. On CRC-enabled filesystems each remote fsblock carries an `xfs_attr3_rmt_hdr` with magic, offset, byte count, uuid, owner, disk block number, and `NULLCOMMITLSN`. The write verifier rejects any non-`NULLCOMMITLSN` value because log recovery must not treat remote buffers as normal logged metadata after block reuse. Values are written synchronously before the corresponding leaf entry is made complete, providing crash safety in combination with `XFS_ATTR_INCOMPLETE`.

The block count calculation differs between CRC and non-CRC filesystems because each CRC block loses header space. For max-sized xattrs, this can require more than 64 KiB of buffer space across multiple fsblocks, which is why remote buffers must never acquire log items.

## Dependencies and integration points
This file depends on bmap read/write/unmap functions, XFS buffer cache, attr geometry, CRC/magic verification, inode locks, attr fork health marking, delayed attr state in `struct xfs_attr_intent`, and leaf-state code that stores `rmtblkno`, `rmtblkcnt`, and `rmtvaluelen` in leaf entries. It integrates with `xfs_attr.c` remote state transitions and with `xfs_attr_leaf.c` clear/set/flip incomplete flag routines.

## Risks and edge cases
The most important invariant is that remote buffers do not enter the logging system. Header mismatch on owner, byte offset, byte count, uuid, or block number indicates corruption and marks the attr fork sick. Sizing must account for per-block headers on CRC filesystems. Sparse, delayed, or hole mappings in remote value extents are corruption. `xfs_attr_rmtval_remove` intentionally uses `-EAGAIN` as progress, so callers must roll transactions and retry. ENODATA from disk I/O must not be confused with ENOATTR semantics. Buffer invalidation uses trylock flags and must be safe if buffers are absent.

## Test signals
Tests should cover remote values at local/remote boundary, max xattr size, CRC and non-CRC remote block layout, multi-block values on 4 KiB and 64 KiB filesystems, header corruption detection, stale buffer invalidation before unmap, bmap holes/corruption rejection, transaction-rolled removal returning `-EAGAIN`, synchronous write error propagation, and crash recovery before and after leaf incomplete flag clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.h

## Purpose
`xfs_attr_remote.h` declares the remote extended-attribute value API. It exposes sizing helpers and the read/write/allocation/removal functions used by the attr core and leaf state machine when values are stored out of line in attr-fork extents.

## Important APIs, types, and functions
The header declares `xfs_attr3_rmt_blocks` and inline `xfs_attr3_max_rmt_blocks`, plus remote value functions `xfs_attr_rmtval_get`, `xfs_attr_rmtval_stale`, `xfs_attr_rmtval_invalidate`, `xfs_attr_rmtval_remove`, `xfs_attr_rmt_find_hole`, `xfs_attr_rmtval_set_value`, `xfs_attr_rmtval_set_blk`, and `xfs_attr_rmtval_find_space`.

## Control flow
The exported functions are used in two phases. Set/replace operations first find a hole and allocate blocks through intent-based helpers, then synchronously write the value and publish the leaf entry. Get operations use `xfs_attr_rmtval_get` after leaf lookup fills remote block metadata. Remove and replace cleanup invalidate stale buffers and unmap extents through the intent retry loop.

## State and persistence behavior
The header defines the remote-block count contract: max remote blocks are computed from `XFS_XATTR_SIZE_MAX`, not a fixed byte-to-fsb conversion, because CRC remote value headers consume payload space. Callers are expected to keep `struct xfs_da_args` and `struct xfs_attr_intent` remote fields synchronized while progressing through transactions.

## Dependencies and integration points
It depends on `struct xfs_mount`, `struct xfs_da_args`, `struct xfs_inode`, `struct xfs_bmbt_irec`, and `struct xfs_attr_intent` definitions from including translation units. It is consumed by `xfs_attr.c` and `xfs_attr_leaf.c` and implemented by `xfs_attr_remote.c`.

## Risks and edge cases
Callers must distinguish `xfs_attr_rmtval_set_blk`, which allocates extents under the active transaction, from `xfs_attr_rmtval_set_value`, which writes already allocated remote buffers synchronously. Removing remote values can require repeated calls. The max-block helper must be used for reservations that do not yet know the exact removed value length.

## Test signals
Compilation should catch prototype drift. Runtime tests should cover remote get/set/remove through public xattr operations and verify that reservation code using `xfs_attr3_max_rmt_blocks` handles worst-case CRC header overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_sf.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_sf.h

## Purpose
`xfs_attr_sf.h` defines helpers for XFS shortform extended attributes stored inline in the inode attr fork. It supplies the sort descriptor used by attr list code and inline routines for sizing and walking packed shortform entries.

## Important APIs, types, and functions
The header defines `xfs_attr_sf_sort_t`, containing original entry number, name length, value length, flags, hash, and pointers to name/value. It defines `XFS_ATTR_SF_ENTSIZE_MAX`, the maximum representable name or value length for shortform fields, and inline helpers `xfs_attr_sf_entsize_byname`, `xfs_attr_sf_entsize`, `xfs_attr_sf_firstentry`, `xfs_attr_sf_nextentry`, and `xfs_attr_sf_endptr`.

## Control flow
Shortform users treat the attr fork as a header followed by variable-length entries. `xfs_attr_sf_firstentry` starts iteration immediately after the header, `xfs_attr_sf_nextentry` advances by the computed entry size, and `xfs_attr_sf_endptr` points to the end of valid bytes using the big-endian `totsize` header field. Add/remove/list/verify code in sibling files builds on these pointer operations.

## State and persistence behavior
The packed shortform format stores each entry with one-byte name and value lengths, flags, and a flexible name/value byte array. The helpers do not log or persist by themselves; they encode the layout used by inode attr fork mutation code. `XFS_ATTR_SF_ENTSIZE_MAX` is the boundary that forces conversion to leaf format when names or values cannot be represented in u8 fields.

## Dependencies and integration points
The header depends on on-disk shortform structure definitions from XFS format headers and endian helpers. It is used by `xfs_attr.c`, `xfs_attr_leaf.c`, and attr list code that needs to sort shortform entries by hash for list output.

## Risks and edge cases
All helpers perform raw pointer arithmetic over packed variable-length data, so callers must verify buffer bounds before trusting on-disk or recovered data. `xfs_attr_sf_entsize_byname` takes `uint8_t` lengths; callers must check larger lengths before conversion. The end pointer depends on `totsize`; corrupted `totsize` can make iteration unsafe unless the verifier is run first.

## Test signals
Tests should cover minimum header-only forks, several packed entries, maximum u8 name/value sizes, conversion rejection when lengths exceed shortform limits, malformed `totsize`, zero-length names, and list sorting by hash using `xfs_attr_sf_sort_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_sf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.c

## Purpose
`xfs_bit.c` provides small bitmap scanning helpers used by non-realtime XFS code. The routines operate on arrays of unsigned integer words and implement empty-map detection, contiguous set-bit counting, and next-set-bit lookup.

## Important APIs, types, and functions
The file implements `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit`. The functions use word-level constants from `xfs_bit.h` and platform bit primitives such as `ffz` and `ffs`.

## Control flow
`xfs_bitmap_empty` linearly scans `size` words and returns 1 only if all words are zero. `xfs_contig_bits` starts at `start_bit`, masks off earlier bits in the first word by forcing them to one, scans full words while they are all ones, and returns the count up to the first zero bit. `xfs_next_bit` starts at `start_bit`, masks off earlier bits in the first word by forcing them to zero, scans for a nonzero word, and returns the absolute bit index of the first set bit or `-1`.

## State and persistence behavior
These helpers are pure in-memory bitmap readers. They do not allocate, log, mutate state, or persist anything. The only state assumptions are the supplied map pointer, word count, and starting bit.

## Dependencies and integration points
The code includes `xfs_platform.h`, `xfs_log_format.h`, and `xfs_bit.h`. It is a generic libxfs utility and can support allocation or metadata code that represents state as bitmaps. It relies on `NBWORD`, `BIT_TO_WORD_SHIFT`, `ASSERT`, `ffs`, and `ffz` definitions from the platform/kernel environment.

## Risks and edge cases
`size` is a word count, not a byte or bit count, which is easy to misuse. `xfs_contig_bits` asserts that `start_bit` is within the map, while `xfs_next_bit` returns `-1` if the start is beyond the map. Both scanning routines assume the bitmap is padded to a full word. Care is needed near word boundaries because the first partial word is treated specially. Return type is `int`, so callers should not use maps larger than representable bit indexes.

## Test signals
Unit-style tests should cover empty maps, all-ones maps, starts at zero, starts inside a word, starts on word boundaries, starts at the final bit, starts beyond the map for `xfs_next_bit`, contiguous runs ending in the first word and later words, and maps with padding bits set or clear according to caller expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.h

## Purpose
`xfs_bit.h` declares XFS bit manipulation utilities and provides inline helpers for masks and high/low bit lookup on 32-bit and 64-bit integers. It also declares the bitmap scanning functions implemented in `xfs_bit.c`.

## Important APIs, types, and functions
Inline helpers are `xfs_mask64hi`, `xfs_mask32lo`, `xfs_mask64lo`, `xfs_highbit32`, `xfs_highbit64`, `xfs_lowbit32`, and `xfs_lowbit64`. External declarations are `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit`.

## Control flow
Mask helpers build high or low bit masks through shifts. High-bit helpers wrap `fls`/`fls64` and convert from one-based results to zero-based bit indexes, returning `-1` when no bit is set. Low-bit helpers similarly use `ffs`; the 64-bit variant checks the low 32 bits first, then the high 32 bits and adds 32 to the one-based result before returning a zero-based index.

## State and persistence behavior
All inline helpers are pure computations with no side effects. They do not touch persistent filesystem state. Their correctness matters because callers often use bit positions for metadata sizing, scanning, and allocation decisions.

## Dependencies and integration points
The header relies on kernel/platform bit primitives `fls`, `fls64`, and `ffs`, along with XFS integer typedefs. It is included by `xfs_bit.c` and other libxfs code that needs portable bit utility wrappers.

## Risks and edge cases
The mask helpers assume valid shift counts; passing 0 to `xfs_mask64hi` or a full word size to low-mask helpers can produce undefined C shift behavior depending on the expression. Callers must treat high/low bit returns as zero-based indexes and handle `-1` for zero input. `xfs_lowbit64` deliberately splits the value into two 32-bit halves, so tests should cover high-only values.

## Test signals
Tests should verify zero inputs, single-bit values at low and high positions, mixed-bit values, mask generation for representative counts, and consistency with kernel bit primitive expectations. Static analysis should look for unsafe mask calls with variable counts that can be 0 or word-sized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.h -->
