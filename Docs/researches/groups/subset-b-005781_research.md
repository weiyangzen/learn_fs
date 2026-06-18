# subset-b-005781 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.c

## Purpose
`xfs_da_btree.c` implements the shared directory/attribute btree machinery for XFS "DA" blocks: hashed-name btree search, split, join, sibling linkage, block allocation/removal, logical-to-physical buffer mapping, and v2/v3 metadata verification for directory leaf, attribute leaf, and intermediate node blocks.

## Important APIs, Types, And Functions
The file exports state lifetime helpers `xfs_da_state_alloc()`, `xfs_da_state_reset()`, and `xfs_da_state_free()`, backed by `xfs_da_state_cache`. Header conversion helpers `xfs_da3_node_hdr_from_disk()` and `xfs_da3_node_hdr_to_disk()` abstract v2 versus CRC-enabled v3 node headers. Verification entry points include `xfs_da3_blkinfo_verify()`, `xfs_da3_node_header_check()`, `xfs_da3_header_check()`, and `xfs_da3_node_buf_ops`.

Tree mutation APIs include `xfs_da3_node_create()`, `xfs_da3_split()`, `xfs_da3_join()`, `xfs_da3_fixhashpath()`, `xfs_attr3_node_entry_remove()`, `xfs_da3_blk_link()`, and `xfs_da3_path_shift()`. Lookup is implemented by `xfs_da3_node_lookup_int()`, which descends the btree and delegates leaf matching to attr or dir leaf code. Storage utilities include `xfs_da_grow_inode_int()`, `xfs_da_grow_inode()`, `xfs_da_shrink_inode()`, `xfs_da_get_buf()`, `xfs_da_read_buf()`, and `xfs_da_reada_buf()`. `xfs_da_hashname()` and `xfs_da_compname()` provide the default name hash and exact comparison functions.

## Control Flow
Lookup starts at `args->geo->leafblk`, reads each node through `xfs_da3_node_read()`, verifies owner/header state, binary-searches sorted hash entries, and descends until an attr or directory leaf is found. Duplicate hashes are handled by choosing the first matching key and, if a leaf ends with the searched hash, shifting forward with `xfs_da3_path_shift()` to inspect adjacent leaves.

Splitting walks upward from the leaf path. Attribute leaves can double-split via `state->extrablk`; directory leaves split once. Intermediate nodes either absorb new child entries or allocate a new node, rebalance entries, link siblings, and propagate hash updates. If propagation reaches above the root, `xfs_da3_root_split()` copies block zero to a new block and creates a new root with two child pointers.

Joining walks upward after deletion. Leaf or node "too small" checks decide whether to do nothing, coalesce into a sibling, or unlink an empty block. `xfs_da3_root_join()` collapses a root with a single child by copying that child into block zero. Shrinking removes extents; if directory bunmap fails with `-ENOSPC`, `xfs_da3_swap_lastblock()` moves the last DA block into the dead block slot so the tail extent can be removed.

## State And Persistence
Persistent state is the inode's directory or attr fork mappings and the on-disk DA blocks. Mutations log precise byte ranges with `xfs_trans_log_buf()`, mark buffer types for recovery, stamp v3 owner/uuid/block-number fields, and update CRCs during write verification. In-memory state in `struct xfs_da_state` carries active and alternate paths, child block metadata, and extra split state. Corruption paths mark the directory/attribute fork sick through health helpers.

## Dependencies And Integration Points
This file depends on bmap mapping/allocation (`xfs_bmapi_write`, `xfs_bmapi_read`, `xfs_bunmapi`), transactions and buffer logging, XFS buffer verifiers, dir leaf/block code, attr leaf code, mount geometry from `xfs_da_mount()`, tracepoints, error injection, and metadata health reporting. It is the common btree backend used by `xfs_dir2_leaf.c`, `xfs_dir2_node.c`, and attribute leaf/node code.

## Risks
Major risks are stale or unsorted hash propagation, sibling link corruption during split/join, owner/CRC verification gaps on v3 filesystems, incorrect block movement in `xfs_da3_swap_lastblock()`, and mapping holes being treated as valid metadata. The code depends on active transaction ownership and inode locks held by callers; violations can corrupt logged metadata. Duplicate hashes and case-insensitive lookup paths are especially sensitive because search must continue across leaf boundaries.

## Test Signals
Useful tests include directory and xattr workloads that force leaf splits, node splits, root splits, joins, root collapse, duplicate-hash names, case-insensitive lookups, no-space deletion that triggers last-block swapping, fragmented DA block mappings, v3 CRC/owner mismatch injection, read verifier format switching between node and leaf blocks, and recovery after crashes between intent/logged DA updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.h

## Purpose
`xfs_da_btree.h` defines the in-core contracts for XFS directory/attribute btree operations. It describes directory/attribute geometry, operation arguments, lookup comparison results, btree traversal state, in-core node headers, logging offset helpers, and the exported DA btree API.

## Important APIs, Types, And Functions
`struct xfs_da_geometry` stores all derived sizing and address-space constants for a directory or attribute fork, including block size, node entry count, leaf/free block locations, and maximum extents. `struct xfs_da_args` is the central argument object for directory and xattr operations; it carries the name/value, inode, transaction, owner, hash, fork selector, remote attr fields, operation flags, and lookup comparison result.

`enum xfs_dacmp` defines exact, case-only, and different name comparisons. `struct xfs_da_state_blk`, `struct xfs_da_state_path`, and `struct xfs_da_state` model active and alternate btree paths during lookup, split, and join. `struct xfs_da3_icnode_hdr` is the normalized in-core view of v2/v3 node headers. `XFS_DA_LOGOFF` and `XFS_DA_LOGRANGE` calculate byte ranges for transaction logging.

The header declares the exported split/join/search/mapping functions, buffer accessors, name hash/compare helpers, state allocation helpers, v3 node header conversion/checking helpers, and `xfs_da_state_cache`.

## Control Flow
The header has no runtime control flow beyond macros, but it encodes how DA operations are driven: callers populate `xfs_da_args`, allocate an `xfs_da_state`, use lookup to build a path, then call split/join/fixhash helpers as leaf-level code requests structural changes. Buffer helpers use `whichfork` and mount geometry to map logical DA blocks to buffers.

## State And Persistence
The structures are in-memory only, but many fields directly represent persistent metadata coordinates. `xfs_da_geometry` determines where directory data, leaf, and free spaces live in the file. `xfs_da_args::owner`, `whichfork`, `blkno`, remote attr fields, and hash/index fields are used to find and mutate persistent directory or xattr blocks. Operation flags such as `XFS_DA_OP_RECOVERY` and `XFS_DA_OP_LOGGED` influence logged/recovery behavior in higher layers.

## Dependencies And Integration Points
The header is included by directory, xattr, and btree implementation files. It depends on `xfs_da_format.h` for on-disk DA types and on XFS core types such as `xfs_inode`, `xfs_trans`, `xfs_buf`, and fork constants. Its prototypes integrate DA btree code with directory leaf/block code, attribute leaf/remote code, bmap, transaction logging, and buffer verification.

## Risks
Because this header is the ABI between several XFS subsystems, field semantics must remain synchronized with all call sites. Incorrect geometry can send metadata writes into the wrong logical address range. Mis-set operation flags can turn lookup misses into corruption assertions or skip required logging. The fixed `XFS_DA_NODE_MAXDEPTH` bounds path arrays; tree fanout assumptions must remain valid.

## Test Signals
Build coverage should include CRC and non-CRC filesystems, attr and data forks, ascii-ci directory mode, parent pointer attrs, logged attr operations, and recovery builds. Runtime tests should exercise all exported prototypes through directory and xattr add/remove/replace paths, with assertions enabled to catch bad path indexes and geometry-derived range errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_format.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_format.h

## Purpose
`xfs_da_format.h` defines the persistent on-disk format for XFS directory and attribute blocks that share the DA btree framework. It covers v2 and CRC-enabled v3 block headers, directory shortform/data/leaf/free/block layouts, attribute shortform/leaf/remote layouts, filetype and attr flag constants, and inline layout accessors.

## Important APIs, Types, And Functions
DA btree definitions include `struct xfs_da_blkinfo`, `struct xfs_da3_blkinfo`, node magic constants, `struct xfs_da_node_hdr`, `struct xfs_da3_node_hdr`, `struct xfs_da_node_entry`, and `XFS_DA_NODE_MAXDEPTH`.

Directory definitions include magic constants for block/data/free/leaf formats, filetype constants, `struct xfs_dir2_sf_hdr`, `struct xfs_dir2_sf_entry`, data block headers, active and unused data entries, leaf and free block headers, and block-tail helpers such as `xfs_dir2_block_leaf_p()` and `xfs_dir2_leaf_bests_p()`. Offset/dataptr/db types and constants define the directory's three large logical spaces: data, leaf, and free.

Attribute definitions include shortform headers/entries, leaf headers, free maps, local and remote name/value records, v3 leaf headers, attr namespace/incomplete flags, leaf entry size helpers, remote attr block headers, and the parent pointer value record `struct xfs_parent_rec`.

## Control Flow
The header is mostly declarative. Inline helpers compute variable-layout offsets and sizes for shortform directories, block tails, leaf bests, attr local/remote entries, and directory block bytes. These helpers are part of the control path for all readers and writers because the on-disk structures contain flex arrays and packed variable-length records.

## State And Persistence
Everything in this file is either on-disk metadata or a constant used to interpret on-disk metadata. v3 headers persist CRC, LSN, uuid, owner, and block-number fields. Directory data entries persist inode numbers, names, filetypes, and back-tags; unused entries persist free tags and lengths. Attribute leaf entries persist hashes, name indexes, namespace/local/incomplete flags, local values, or remote value extents. Parent pointer attributes persist parent inode and generation in the attr value.

## Dependencies And Integration Points
This format header is consumed by DA btree, directory shortform/data/block/leaf/node code, attr leaf/remote code, parent pointer code, buffer verifiers, repair/scrub code, and userspace tools that must match kernel layout. It depends on XFS endian types, UUIDs, block/inode types, and geometry from the mount code.

## Risks
Layout drift is the highest risk. The comments around flex-array conversion in attr local/remote records document historically encoded padding; changing `xfs_attr_leaf_entsize_*()` would break existing filesystems. Endian mistakes, incorrect v2/v3 header-size selection, filetype values beyond `XFS_DIR3_FT_MAX`, or malformed free/tag offsets can lead to silent directory or xattr corruption. The attr incomplete bit is crash-recovery visible and must preserve atomicity of large attr updates.

## Test Signals
Tests should validate exact structure sizes/offsets on multiple architectures, v2 and v3 directory/attr images, shortform inode-number width transitions, directory entry filetype round trips, attr local/remote size calculations after flex-array changes, free-space tag verification, remote attr header CRC/owner checks, and parent pointer attr hash/value decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.c

## Purpose
`xfs_defer.c` implements the generic deferred-operation engine for XFS. It batches metadata work that cannot be completed safely in one transaction, logs restartable intent/done items, rolls transactions while preserving held resources, supports continuations with `-EAGAIN`, captures deferred work for log recovery, and manages per-operation item caches.

## Important APIs, Types, And Functions
The file manages `struct xfs_defer_pending` objects from `xfs_defer_pending_cache`. Public entry points include `xfs_defer_add()`, `xfs_defer_add_barrier()`, `xfs_defer_finish_one()`, `xfs_defer_finish_noroll()`, `xfs_defer_finish()`, `xfs_defer_cancel()`, `xfs_defer_move()`, recovery helpers `xfs_defer_start_recovery()`, `xfs_defer_cancel_recovery()`, `xfs_defer_finish_recovery()`, capture helpers `xfs_defer_ops_capture_and_commit()`, `xfs_defer_ops_continue()`, `xfs_defer_ops_capture_abort()`, `xfs_defer_resources_rele()`, cache init/destroy functions, and pause/unpause helpers.

Internal helpers create intent and done log items, abort pending intents, save and restore held buffers/inodes, roll transactions, relog old intent items to advance the log tail, and isolate paused items. Operation-specific behavior is supplied by `struct xfs_defer_op_type` callbacks.

## Control Flow
New work enters `tp->t_dfops` via `xfs_defer_add()`, which appends to the last compatible pending item unless it is full, already logged, or paused. `xfs_defer_finish_noroll()` loops while there is intake or pending work: create intent items for intake, isolate paused items, splice intake to a local pending list, roll if intents exist or work was just finished, relog old intents if needed, and call `xfs_defer_finish_one()` on the first pending item.

`xfs_defer_finish_one()` creates a done item, removes work items one by one, calls the operation's `finish_item()`, and frees the pending item when empty. If a finish callback returns `-EAGAIN`, the current item is requeued, the done/intent state is replaced with a fresh intent, and the outer loop rolls before retrying. Errors abort committed intents, force an in-core-corruption shutdown, cancel pending work, and cancel transaction-local intake.

Recovery capture first logs intents for all deferred work, moves dfops and remaining reservations to `struct xfs_defer_capture`, commits the transaction, and later continues the captured chain in a new transaction after relocking saved resources.

## State And Persistence
In-memory state is held in pending lists, work item lists, intent/done log-item pointers, low-space flags, and captured resources. Persistent crash-recovery state is the log intent/done item stream generated by per-operation callbacks. Held resources across rolls include up to two buffers and five inodes, with ordered-buffer state preserved. Paused deferred items remain attached to the outgoing transaction until unpaused.

## Dependencies And Integration Points
This engine depends on the transaction subsystem, log item infrastructure, AIL/log tail management, buffer and inode log items, inode sorting/locking, XFS shutdown handling, and operation providers for rmap, refcount, bmap, extent free, attr, and exchange-maps intents. It is used by mapping, reflink, allocation, xattr, parent pointer, and recovery paths that need restartable multi-transaction metadata updates.

## Risks
Intent/done ordering is critical: logging a done too late can replay completed work, while dropping an intent too early can lose required recovery. Resource capture limits are fixed and assert on overflow. Incorrect `-EAGAIN` handling can leak work items, exceed log reservation, or pin the log tail. Paused items can deadlock higher-level logic if callers leave dependencies on unfinished work. Error paths intentionally shut down the filesystem, so false corruption classification is high impact.

## Test Signals
Test with reflink/remap operations that generate bmap, rmap, refcount, and extent-free chains; fault injection during create-intent, transaction roll, finish-item, and relog paths; callbacks that repeatedly return `-EAGAIN`; paused attr/parent-pointer work; log recovery of captured intents; low-space mode movement; held buffer/inode preservation across rolls; and cache init unwind failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.h

## Purpose
`xfs_defer.h` defines the generic deferred-operation interface used by XFS metadata subsystems. It declares pending-work containers, operation callback tables, resource-capture structures, public finish/cancel/recovery APIs, and the pause/barrier controls used to order deferred work.

## Important APIs, Types, And Functions
`struct xfs_defer_pending` links one batch of deferred work, its work-item list, logged intent item, logged done item, callback table, item count, and flags. `XFS_DEFER_PAUSED` marks a batch that should be carried forward without finishing. `struct xfs_defer_op_type` is the provider contract: create/abort intent, create done, finish item, optional finish cleanup, cancel item, recover work, and relog intent.

The header declares operation providers such as `xfs_bmap_update_defer_type`, refcount/rmap providers, extent-free providers, attr, and exchmaps. `struct xfs_defer_resources` captures buffers and inodes that must survive transaction rolls. `struct xfs_defer_capture` stores deferred ops, transaction flags, reservations, log reservation, and held resources for recovery continuation. Public functions include add, finish, cancel, move, capture/continue/abort, recovery start/finish, cache init/destroy, item pause/unpause, and barrier insertion.

## Control Flow
The inline `xfs_defer_add_item()` appends a work item to a pending batch and increments its count. All higher-level flow is implemented in `xfs_defer.c`: callers add work during a permanent-reservation transaction, finish rolls and processes the list, and recovery can capture then continue lists in later transactions.

## State And Persistence
The header describes in-memory structures whose intent/done pointers refer to persistent log items. The resource capture arrays persist references, not on-disk data, across transaction boundaries. Counts and flags drive whether batches are appended, paused, or split by barriers.

## Dependencies And Integration Points
It depends on XFS transaction, log item, btree cursor, buffer, and inode types. Provider declarations tie it to bmap, rmap, refcount, allocation, attr, and exchange-map subsystems. Parent pointer rename paths rely on the five-inode capture limit documented here.

## Risks
Callback implementations must obey the semantics documented by the type table. A provider that fails to cancel items, update unfinished work before `-EAGAIN`, or relog intents correctly can break recovery. The fixed resource limits (`XFS_DEFER_OPS_NR_INODES`, `XFS_DEFER_OPS_NR_BUFS`) are part of correctness assumptions for complex renames and should not be exceeded by future operations without widening the structure and tests.

## Test Signals
Build tests should cover all provider declarations under feature combinations. Runtime signals include mixed deferred-op chains, barriers separating adjacent same-type work, paused/unpaused batches, recovery capture with held inodes and buffers, and provider-specific cancellation after injected failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.c

## Purpose
`xfs_dir2.c` is the generic XFS directory front end. It initializes directory/attribute geometry at mount time, selects the active directory format, dispatches create/lookup/remove/replace operations to shortform/block/leaf/node implementations, validates inode numbers and names, handles directory block growth/shrink, supports ascii-ci hashing/comparison, provides optional live update hooks, and implements higher-level child link/unlink/rename/exchange semantics including parent pointer updates.

## Important APIs, Types, And Functions
Global names `xfs_name_dot` and `xfs_name_dotdot` represent `"."` and `".."`. `xfs_mode_to_ftype()` maps inode mode to on-disk dirent type. `xfs_da_mount()` and `xfs_da_unmount()` allocate and free `m_dir_geo` and `m_attr_geo`. `xfs_dir2_format()` detects shortform, block, leaf, or node format from inode fork format and data-fork EOF.

Directory operation entry points include `xfs_dir_init()`, `xfs_dir_createname()`, `xfs_dir_lookup()`, `xfs_dir_removename()`, `xfs_dir_replace()`, and `xfs_dir_canenter()`, with `_args` variants for prebuilt `xfs_da_args`. Utility functions include `xfs_dir2_grow_inode()`, `xfs_dir2_shrink_inode()`, `xfs_dir2_namecheck()`, `xfs_dir2_hashname()`, and `xfs_dir2_compname()`. Higher-level child APIs include `xfs_dir_create_child()`, `xfs_dir_add_child()`, `xfs_dir_remove_child()`, `xfs_dir_exchange_children()`, and `xfs_dir_rename_children()`.

## Control Flow
Mount setup computes directory geometry from superblock blocklog and dirblklog, selecting v2/v3 header sizes based on CRC support, then derives data/leaf/free logical block locations. Attribute geometry is one filesystem block and reuses node header sizing.

Normal directory operations allocate an `xfs_da_args`, fill name, hash, filetype, fork, transaction, owner, and block reservation fields, and dispatch by `xfs_dir2_format()`. Lookups take a data-map shared lock, translate the internal `-EEXIST` lookup success convention into zero, and optionally return the real case-insensitive name. Add with `inum == 0` becomes a space-only `JUSTCHECK`.

Child create/add/remove/rename functions wrap raw dirent updates with link count maintenance, timestamp logging, `.`/`..` initialization or replacement, unlinked-list removal for `O_TMPFILE`/whiteouts, parent pointer attr operations, and live update hook calls.

## State And Persistence
Persistent state includes directory fork format, directory blocks, link counts, inode timestamps, parent pointer attributes, and directory inode size. `xfs_dir2_grow_inode()` grows data/free spaces and updates `i_disk_size` for data space. `xfs_dir2_shrink_inode()` unmaps blocks and reduces `i_disk_size` only when the removed data block was the trailing block. In-memory mount geometry persists for the mount lifetime.

## Dependencies And Integration Points
This file integrates VFS directory operations with shortform/block/leaf/node directory files, DA btree mapping, bmap, transactions, inode link helpers, parent pointer attr code, AG inode unlink helpers, health/error injection, and optional live hooks for online fsck. It depends on inode locks being held by higher layers for mutation APIs.

## Risks
Format detection must match actual fork layout; an incorrect EOF or `i_disk_size` can route updates to the wrong implementation. Link count and `..` update ordering during rename/exchange is subtle, especially for cross-directory directory renames and whiteouts. Parent pointer updates must remain consistent with dirent changes. `xfs_dir2_shrink_inode()` can return `-ENOSPC` when a no-reservation removal would require bmap btree changes; callers must leave an empty but consistent block.

## Test Signals
Tests should cover transitions among shortform, block, leaf, and node directories; ascii-ci exact and case-only lookups; invalid inode/name rejection; directory creation/removal with link count checks; `O_TMPFILE` link insertion; whiteout rename; cross-directory rename of directories with `..` updates; exchange of files/directories; parent pointer enabled and disabled modes; live hook enablement; and no-space removals that cannot shrink mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.h

## Purpose
`xfs_dir2.h` is the public/private interface for XFS directory version 2/3 operations. It declares directory APIs, buffer verifier symbols, conversion helpers for directory logical address spaces, name validation and ascii-ci helpers, optional live hook interfaces, and parent-pointer-aware child update structures.

## Important APIs, Types, And Functions
The header declares `xfs_name_dot` and `xfs_name_dotdot`, `xfs_dir2_samename()`, `enum xfs_dir2_fmt`, mount lifecycle functions, generic directory mutation/lookups, direct `xfs_da_args` variants, block/data helper APIs, inode-number validation, and buffer ops for block, leaf, free, and data blocks.

Inline conversion helpers translate between directory byte offsets, dataptrs, logical directory blocks (`xfs_dir2_db_t`), DA blocks, and block offsets. `xfs_dir2_block_tail_p()` and `xfs_dir2_leaf_tail_p()` locate tail records based on mount geometry. The ascii-ci helpers transform only supported ASCII/Latin uppercase bytes. `struct xfs_dir_update` carries parent/name/child/parent-pointer args for create/add/remove/rename/exchange helpers.

## Control Flow
Most flow is declarative through prototypes and inline arithmetic. Callers use the conversion helpers heavily when converting leaf addresses to data-entry pointers, logging tail areas, mapping directory spaces, and formatting readdir offsets. When `CONFIG_XFS_LIVE_HOOKS` is disabled, hook calls compile to no-ops; otherwise hook registration and update callbacks are provided by `xfs_dir2.c`.

## State And Persistence
The header itself stores no state, but its conversions define the persistent directory address ABI: data, leaf, and free spaces are separated by large fixed offsets and converted through geometry. `struct xfs_dir_update` drives persistent dirent and parent-pointer updates. The declared buffer ops enforce persistent block format checks for block/data/leaf/free metadata.

## Dependencies And Integration Points
It includes DA format and btree headers and is used by all directory implementation files plus bmap and higher-level inode operations. It integrates with parent pointer code, online fsck hooks, buffer verifiers, and VFS-facing directory functions.

## Risks
Arithmetic helper regressions can corrupt every directory format because dataptrs and DA blocks are stored on disk. The ascii-ci transform is intentionally narrow; treating it as general Unicode casefolding would be incorrect. Hook configuration must avoid lock inversions because enabling/disabling static branches can take CPU hotplug locks. The child update API assumes callers already hold required inode locks.

## Test Signals
Tests should verify offset conversions round-trip for multiple directory block sizes, block/leaf tail pointer placement, name validation around `MAXNAMELEN`, filetype conversion paths, hook stubs in disabled builds, live hook notifications in enabled builds, and parent-pointer child update APIs across create/add/remove/rename/exchange.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_block.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_block.c

## Purpose
`xfs_dir2_block.c` implements the single-block XFS directory format, where directory data entries, an embedded hash-sorted leaf array, and a block tail all live in one directory block. It also verifies block-format buffers and converts between shortform, block, and single-leaf directory formats.

## Important APIs, Types, And Functions
Startup initializes cached hashes for `"."` and `".."` through `xfs_dir_startup()`. Verification is provided by `xfs_dir3_block_buf_ops`, `xfs_dir3_block_header_check()`, and `xfs_dir3_block_read()`. `xfs_dir3_block_init()` formats v2/v3 block headers.

Single-block operations include `xfs_dir2_block_addname()`, `xfs_dir2_block_lookup()`, internal `xfs_dir2_block_lookup_int()`, `xfs_dir2_block_removename()`, and `xfs_dir2_block_replace()`. Local helpers manage space decisions, compaction, leaf/tail logging, and sorting. Format conversion is implemented by `xfs_dir2_leaf_to_block()` and `xfs_dir2_sf_to_block()`.

## Control Flow
Add reads the only block, computes the new data-entry size, checks whether stale leaf slots and free regions can hold the entry and possibly a new leaf entry, and either performs a space-only check, converts to leaf format, or inserts in place. In-place insertion may compact stale leaf entries, consume tail-adjacent free space for a new leaf entry, reuse stale slots, binary-search the insertion point, fill the dirent, update bestfree, and log header/leaf/tail/entry ranges.

Lookup binary-searches the embedded leaf array by hash, rewinds to the first duplicate hash, scans forward comparing names, and preserves the first case-insensitive match while still preferring exact matches. Remove marks the data entry free, marks the leaf address stale, updates bestfree and tail stale count, then tries to convert back to shortform if the resulting size fits. Replace updates only the inode number and filetype in the matched data entry.

`xfs_dir2_sf_to_block()` copies shortform data aside, converts the data fork to extents, allocates block zero, creates `"."`, `".."`, and all shortform entries while preserving saved offsets with holes, sorts the leaf array, and logs the finished block. `xfs_dir2_leaf_to_block()` converts a leaf/data pair back to block format only if trailing data blocks can be trimmed and the first data block has enough tail free space.

## State And Persistence
Persistent state is the block/data header, bestfree array, variable-length data entries, unused extents, embedded leaf entries, and block tail. v3 blocks persist CRC, uuid, owner, LSN, and block address. Mutations are transaction logged with byte-range helpers and validated by `xfs_dir3_data_check()`. Format conversions change the inode data fork from local to extent or remove the separate leaf block via `xfs_da_shrink_inode()`.

## Dependencies And Integration Points
The file depends on DA buffer mapping, directory data helpers, shortform helpers, leaf helpers, transaction logging, buffer verifiers, bmap fork conversion, mount geometry, and health reporting. It is selected by `xfs_dir2_format()` when a directory occupies exactly one directory block.

## Risks
The highest-risk code is in-block space accounting: stale leaf compaction, end-free handling, bestfree rescans, and tag offsets must stay coherent. Lookup must handle duplicate hashes and ascii-ci semantics without returning stale entries. Conversions can lose directory entries if offset preservation or leaf sorting is wrong. Header owner/CRC verification is essential because the block shares data and index structures in one buffer.

## Test Signals
Tests should force adds that reuse stale leaf slots, consume end-free leaf space, compact stale entries, and convert block to leaf. Removal tests should convert block back to shortform and leave block format when too large. Conversion tests should cover shortform entries with holes, v2/v3 block headers, duplicate hashes, ascii-ci case matches, invalid CRC/owner, replace filetype updates, and crash recovery after each logged phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_block.c -->
