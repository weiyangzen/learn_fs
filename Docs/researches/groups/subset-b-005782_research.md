# subset-b-005782 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_data.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_data.c

## Purpose
`xfs_dir2_data.c` implements the data-block side of XFS directory version 2/3 formats. It provides helpers for interpreting directory data entries, maintaining the per-block `bestfree` table, initializing data blocks, verifying directory data buffers, and logging modified regions into transactions. It is shared by shortform/block/leaf/node directory code because all non-shortform formats eventually store names in data blocks.

## Important APIs, Types, and Functions
The main exported helpers are `xfs_dir2_data_bestfree_p`, `xfs_dir2_data_entry_tag_p`, `xfs_dir2_data_get_ftype`, `xfs_dir2_data_put_ftype`, `__xfs_dir3_data_check`, `xfs_dir3_data_read`, `xfs_dir3_data_readahead`, `xfs_dir2_data_freeinsert`, `xfs_dir3_data_init`, `xfs_dir2_data_freescan`, `xfs_dir2_data_make_free`, `xfs_dir2_data_use_free`, and `xfs_dir3_data_end_offset`. The file manipulates `struct xfs_dir2_data_hdr`, v5 `struct xfs_dir3_data_hdr`, active `struct xfs_dir2_data_entry`, unused `struct xfs_dir2_data_unused`, and the fixed three-entry `struct xfs_dir2_data_free` bestfree array.

## Control Flow
Reads go through `xfs_dir3_data_read`, which calls `xfs_da_read_buf` with `xfs_dir3_data_buf_ops`, performs owner checks that require the caller's inode context, marks corrupt buffers and directory health on mismatch, and tags the buffer as `XFS_BLFT_DIR_DATA_BUF` for transactions. Readahead uses `xfs_dir3_data_reada_buf_ops` because opening a directory can speculatively read a block that is either block-format or data-format; `xfs_dir3_data_reada_verify` switches to block or data verification based on magic.

Verification begins with magic, CRC metadata, UUID, block address, and LSN checks, then calls `__xfs_dir3_data_check`. That full checker walks from `geo->data_entry_offset` to `xfs_dir3_data_end_offset`, validates unused records, active entries, offset tags, inode numbers, file types, non-overlap, adjacency of free records, and bestfree ordering. If the buffer is block-format, it also validates that every data entry has a matching sorted leaf entry and that stale counts match.

Free-space mutation is split between `xfs_dir2_data_make_free` and `xfs_dir2_data_use_free`. `make_free` merges a byte range with previous and/or following unused records, updates or rescans bestfree, and logs unused records. `use_free` consumes a range from an unused record, handling exact, front, tail, and middle splits while preserving bestfree invariants or requesting a rescan. `xfs_dir2_data_freescan` reconstructs bestfree from the entire block when local updates are insufficient.

## State and Persistence
Persistent state consists of directory data/block buffers, active entries with trailing offset tags, unused records with free tags and trailing offset tags, v5 metadata headers, and the bestfree array. Mutations are recorded with `xfs_trans_log_buf` through targeted log helpers: `xfs_dir2_data_log_header`, `xfs_dir2_data_log_entry`, and `xfs_dir2_data_log_unused`. v5 write verification refreshes the LSN and CRC and zeroes stale padding in the data header before writeout.

## Dependencies and Integration Points
This file depends on directory geometry conversion helpers from `xfs_dir2.h`, transaction and buffer logging, `xfs_da_read_buf`/`xfs_da_get_buf`, inode health reporting, buffer verifier APIs, and name hashing for block-format validation. It is called heavily by `xfs_dir2_leaf.c`, `xfs_dir2_node.c`, `xfs_dir2_block.c`, and `xfs_dir2_sf.c` during format conversion and add/remove operations.

## Risks and Edge Cases
The highest-risk logic is bestfree maintenance: wrong ordering, missed rescans, or stale offsets can corrupt later allocation decisions. The verifier is intentionally strict about adjacent free records, tag offsets, owner metadata, and block-vs-data magic because directory corruption can otherwise cascade into bogus name lookup. Multi-format readahead is also sensitive because it must assign the correct verifier after reading only the magic. Test signals include xfstests directory add/remove/rename stress, fsck/scrub detection of bad bestfree tables, CRC/owner corruption injection, and coverage for conversion paths that repeatedly split and merge free records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_leaf.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_leaf.c

## Purpose
`xfs_dir2_leaf.c` implements XFS leaf-format directories. Leaf-format directories store names in data blocks and keep a single leaf1 block containing sorted hash entries plus a tail-side bestfree table for all data blocks. The file also handles transitions between block, leaf, and node formats as directory size changes.

## Important APIs, Types, and Functions
Key public functions include `xfs_dir2_leaf_hdr_from_disk`, `xfs_dir2_leaf_hdr_to_disk`, `xfs_dir3_leaf_check_int`, `xfs_dir3_leaf_read`, `xfs_dir3_leafn_read`, `xfs_dir3_leaf_get_buf`, `xfs_dir2_block_to_leaf`, `xfs_dir2_leaf_addname`, `xfs_dir3_leaf_compact`, `xfs_dir3_leaf_compact_x1`, `xfs_dir3_leaf_log_ents`, `xfs_dir3_leaf_log_header`, `xfs_dir2_leaf_lookup`, `xfs_dir2_leaf_removename`, `xfs_dir2_leaf_replace`, `xfs_dir2_leaf_search_hash`, `xfs_dir2_leaf_trim_data`, and `xfs_dir2_node_to_leaf`. The central abstraction is `struct xfs_dir3_icleaf_hdr`, an in-core header that hides v4/v5 on-disk header layout differences and points at the on-disk leaf entries.

## Control Flow
Leaf buffer reads use `xfs_dir3_leaf_read` for leaf1 blocks and `xfs_dir3_leafn_read` for node leaf blocks. The verifier checks DA block metadata, decodes the leaf header, validates entry bounds, verifies hash ordering and stale counts under expensive checking, and applies v5 owner checks outside the generic verifier.

`xfs_dir2_block_to_leaf` grows the directory into the leaf range, initializes a leaf1 block, copies the block-format leaf entries to it, turns the original block into a pure data block, frees the former inline leaf/tail area, and initializes the leaf bests table from the data block bestfree value. `xfs_dir2_leaf_addname` reads the leaf, finds the hash insertion point, tries same-hash data blocks first, scans the bests table for space, allocates and initializes a data block if needed, consumes data-block free space, writes the new dirent, updates the leaf bests entry, inserts or reuses a leaf entry, and logs all touched leaf/data regions. If the leaf block cannot hold the metadata, it converts to node form and retries through `xfs_dir2_node_addname`.

Lookup is handled by `xfs_dir2_leaf_lookup_int`, which binary-searches the sorted hash table, walks equal-hash entries, reads data blocks lazily as the data block number changes, and preserves case-insensitive matches while looking for exact matches. Removal marks the leaf entry stale, frees the data entry, updates the leaf bests table, may remove empty data blocks, and then tries `xfs_dir2_leaf_to_block`. Replacement changes only the data entry inode/filetype and logs that entry.

`xfs_dir2_node_to_leaf` is the down-conversion from node to leaf when the node root is a single leafn and the separate free-space block can fit back into a leaf1 tail. It trims trailing empty free blocks, verifies only one leaf remains, copies free-space bests into the leaf tail, changes the magic and buffer type, frees the free-space block, and may further convert to block format.

## State and Persistence
Persistent leaf state includes sorted hash/address entries, stale entry count, v5 DA metadata, forward/back sibling fields for leafn, leaf1 tail `bestcount`, and the leaf1 bests table. Data block mutations are delegated to `xfs_dir2_data_*`. Leaf mutations are persisted via `xfs_trans_log_buf` ranges for headers, entries, tail, and bests. Buffer ops assign leaf1 or leafn type so log recovery and verifiers interpret the block correctly.

## Dependencies and Integration Points
This file integrates with data-block free-space code, `xfs_dir2_block.c` for block conversion, `xfs_dir2_node.c` for node conversion and leafn behavior, DA btree buffer reading, geometry helpers, tracing, transaction logging, and directory health marking. Case-insensitive lookup support is delegated to `xfs_dir2_compname` and `xfs_dir_cilookup_result`.

## Risks and Test Signals
Risk centers on preserving sorted hash order while reusing stale entries, keeping leaf bests synchronized with data bestfree, and handling conversion thresholds without leaking or misclassifying buffers. Another subtle area is case-insensitive lookup state when multiple equal hashes span different data blocks. Good tests include repeated create/unlink cycles in one directory, hash-collision workloads, no-space-reservation conversion failures, fsstress format churn between block/leaf/node forms, and corruption tests for stale counts, bestcount, owner, and CRC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_leaf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_node.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_node.c

## Purpose
`xfs_dir2_node.c` implements node-format XFS directories. Node-format directories scale beyond a single leaf block by using DA btree leafn blocks for sorted hash entries and separate free-space blocks that summarize the largest free region in each data block. It also owns conversion between leaf and node forms, leafn split/join helpers, and free-space block lifecycle.

## Important APIs, Types, and Functions
Public functions include `xfs_dir2_free_hdr_from_disk`, `xfs_dir2_leaf_to_node`, `xfs_dir2_leaf_lasthash`, `xfs_dir2_leafn_lookup_int`, `xfs_dir2_leafn_order`, `xfs_dir2_leafn_split`, `xfs_dir2_leafn_toosmall`, `xfs_dir2_leafn_unbalance`, `xfs_dir2_node_addname`, `xfs_dir2_node_lookup`, `xfs_dir2_node_removename`, `xfs_dir2_node_replace`, `xfs_dir2_node_trim_free`, and `xfs_dir2_free_read`. Internal helpers map data block numbers to free-space block numbers and indexes, verify free-space blocks, allocate free/data blocks, rebalance leafn entries, and update free-space accounting after removals.

## Control Flow
Free-space buffer IO is handled through `xfs_dir3_free_buf_ops`; read paths verify magic/CRC/UUID/blkno/LSN and then validate `firstdb`, `nvalid`, `nused`, and owner through `xfs_dir3_free_header_check`. `xfs_dir2_free_read` requires a present block, while `xfs_dir2_free_try_read` allows holes for sparse free-space ranges.

`xfs_dir2_leaf_to_node` allocates the first free-space block, copies the leaf1 bests table into it, counts used entries, logs the new free block, and changes the old leaf1 block to a leafn block. `xfs_dir2_node_addname` allocates a DA lookup state, performs `xfs_da3_node_lookup_int` to find the insertion leaf and possibly a useful free-space block, writes the data entry through `xfs_dir2_node_addname_int`, and inserts the leaf entry with `xfs_dir2_leafn_add`. If the target leaf cannot fit, DA split machinery calls `xfs_dir2_leafn_split`, which creates another leafn block, rebalances entries, links siblings, and inserts into the selected leaf.

`xfs_dir2_node_addname_int` first calls `xfs_dir2_node_find_freeblk` to reuse a data block with enough free space or discover that allocation is needed. Allocation goes through `xfs_dir2_node_add_datablk`, which initializes a data block and creates or extends the corresponding free-space block. The new dirent consumes data free space via `xfs_dir2_data_use_free`, updates the free-space bests entry, and returns the data block and offset to the caller so the leaf entry can point at it.

Lookup paths are split by operation mode. For addname, `xfs_dir2_leafn_lookup_for_addname` searches equal-hash entries and returns a free-space block if it finds room near a same-hash data block. For ordinary lookup/remove/replace, `xfs_dir2_leafn_lookup_for_entry` reads data blocks, compares names, tracks case-insensitive matches, and stores the matched data block in `state->extrablk`.

Removal uses `xfs_dir2_leafn_remove` to mark the leaf entry stale, free the data entry, update the corresponding free-space block, remove empty data blocks where possible, and tell the DA layer whether a join is worthwhile. `xfs_dir2_node_removename` then fixes btree hash values, joins underfull leaves, and attempts `xfs_dir2_node_to_leaf`. `xfs_dir2_node_trim_free` removes trailing empty free-space blocks.

## State and Persistence
Persistent state spans data blocks, leafn blocks, DA internal nodes, and free-space blocks. Free-space headers record the first represented data block, valid entry count, and used entry count; `bests[]` entries are either `NULLDATAOFF` or the largest free extent in a data block. All changes are transaction-logged through leaf/data/free log helpers, and buffer types are set to `XFS_BLFT_DIR_FREE_BUF` or `XFS_BLFT_DIR_LEAFN_BUF` for recovery.

## Dependencies and Integration Points
The file depends on DA btree lookup/split/join/path-shift functions, bmap helpers for last offsets, directory geometry conversions, `xfs_dir2_data.c` for data-block mutation, `xfs_dir2_leaf.c` for shared leaf helpers and node-to-leaf conversion, transaction logging, and health/corruption reporting. It is the scalability layer underneath VFS directory operations routed through higher-level XFS directory code.

## Risks and Test Signals
Subtle risks include mismatches between data block numbers and free-space block positions, stale leaf entries distorting split/join thresholds, free-space holes during no-space-reservation operations, and failure to update ancestor hash values after insertion/removal. Tests should stress huge directories, hash collisions, repeated add/remove under ENOSPC injection, sparse free-space block trimming, DA split/join recovery, and scrub detection for invalid `firstdb`, `nvalid`, `nused`, stale counts, and data/free summary mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_priv.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_priv.h

## Purpose
`xfs_dir2_priv.h` is the private interface shared by XFS directory v2/v3 implementation files. It centralizes in-core header abstractions, cross-file prototypes, and small sizing/hash helpers needed by shortform, block, data, leaf, node, and readdir code.

## Important APIs, Types, and Functions
The header defines `struct xfs_dir3_icleaf_hdr` and `struct xfs_dir3_icfree_hdr`, which normalize v4 and v5 on-disk leaf/free headers into host-endian fields plus pointers to the on-disk entry arrays. It declares directory hash and comparison helpers, block-format operations, data-block verifier/free-space helpers, leaf-format operations, node-format operations, shortform operations, and `xfs_readdir`.

Inline helpers include `xfs_dir2_data_unusedsize`, which rounds unused-record length to directory alignment, and `xfs_dir2_data_entsize`, which computes active dirent size including inode, name, optional filetype byte, trailing tag, and alignment. The header also exposes `xfs_dir2_hashname` and `xfs_dir2_compname`, allowing code to use ASCII case-insensitive behavior when mounted that way.

## Control Flow and Integration
This file does not implement control flow directly, but it defines the coupling between implementation files. For example, leaf and node code call data helpers to consume/free data-block ranges; exchange-map post-operation conversion can call shortform conversion helpers; and block/leaf/node conversion routines depend on the declared APIs to move directories across formats.

## State and Persistence
The header describes state layouts indirectly through header abstractions and sizing functions. The in-core header structs are not separately persisted; they are decoded from and encoded back to on-disk buffers by implementation files. The inline size helpers must remain consistent with on-disk directory record layout because their outputs control parsing, allocation, and transaction log ranges.

## Dependencies and Integration Points
The declarations assume types from XFS mount, inode, transaction, DA args/state, buffer, directory format, and VFS directory iteration layers. It is included by many libxfs directory files and provides the private ABI that keeps those files independent of v4/v5 header differences.

## Risks and Test Signals
The main risk is contract drift: if an implementation changes a function signature or directory record layout without updating this header, callers can misparse directory buffers. The sizing helpers are especially critical because off-by-one or missing filetype/tag bytes would corrupt entry walking. Test signals include successful compilation across all directory implementation units, xfstests coverage for filesystems with and without ftype/CRC, and scrub/fsck validation after directory format conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_sf.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_sf.c

## Purpose
`xfs_dir2_sf.c` implements shortform XFS directories, where directory contents live entirely inside the inode data fork in local format. It supports creation, lookup, add/remove/replace, verification, conversion from block format back to shortform, and conversion between 4-byte and 8-byte inode-number encodings.

## Important APIs, Types, and Functions
Important functions include `xfs_dir2_sf_entsize`, `xfs_dir2_sf_nextentry`, `xfs_dir2_sf_get_ino`, `xfs_dir2_sf_put_ino`, `xfs_dir2_sf_get_parent_ino`, `xfs_dir2_sf_put_parent_ino`, `xfs_dir2_sf_get_ftype`, `xfs_dir2_sf_put_ftype`, `xfs_dir2_block_sfsize`, `xfs_dir2_block_to_sf`, `xfs_dir2_sf_addname`, `xfs_dir2_sf_verify`, `xfs_dir2_sf_create`, `xfs_dir2_sf_lookup`, `xfs_dir2_sf_removename`, and `xfs_dir2_sf_replace`. Internal helpers decide easy vs hard insertion and convert all inode fields between 4-byte and 8-byte representations.

## Control Flow
Shortform entries are variable-length: each stores name length, a synthetic data-block offset, name bytes, optional filetype, and a 4- or 8-byte inode number. The header stores entry count, `i8count`, and parent inode. Accessors compute the inode-number location dynamically based on name length, filetype support, and `i8count`.

`xfs_dir2_sf_create` converts a zero-length extent directory to local format if needed, allocates the shortform header in the inode data fork, stores the parent inode, and logs core plus data. Lookup special-cases `.` and `..`, then scans all entries with `xfs_dir2_compname`, preserving case-insensitive matches until an exact match is found.

`xfs_dir2_sf_addname` computes the new entry size, determines whether adding a large inode requires converting to 8-byte inode storage, and decides if the result fits in the inode and could still fit after conversion to block form. If not, it converts to block form and delegates to block addname. The easy add appends at the end after inode data reallocation. The hard add rebuilds the local buffer to insert into a synthetic offset hole, optionally after converting to 8-byte inode numbers.

Removal scans for the exact entry, slides later bytes down, shrinks the inode data fork, decrements counts, and may convert back to 4-byte inode storage when the last large inode disappears. Replacement updates `..` or a named entry, may first convert to 8-byte inode storage or to block form if the expanded shortform no longer fits, adjusts `i8count`, updates filetype, and logs inode data.

`xfs_dir2_block_sfsize` and `xfs_dir2_block_to_sf` support down-conversion from block directories. The size calculator iterates block leaf entries, skips `.`, stores `..` as parent, counts normal entries and large inodes, and bails if the result exceeds local fork capacity. The converter copies active data entries into a temporary shortform buffer, shrinks away the data block, initializes the local fork, and logs the inode.

## State and Persistence
All persistent state is inode-local: `dp->i_df.if_data`, `if_bytes`, `if_format`, and `i_disk_size`. Mutations use `xfs_idata_realloc`, `xfs_init_local_fork`, and `xfs_trans_log_inode` with `XFS_ILOG_CORE` and/or `XFS_ILOG_DDATA`. Shortform has no buffer CRC of its own; it is verified as part of inode local data.

## Dependencies and Integration Points
The file integrates with block-format conversion (`xfs_dir2_sf_to_block`, `xfs_dir2_block_addname`, `xfs_dir2_block_replace`), data/block sizing helpers, inode local fork management, transaction logging, mount features such as ftype, and directory comparison utilities.

## Risks and Test Signals
Risks include variable-length entry walking past inode data, incorrect `i8count`, offsets that cannot represent a future block-format layout, and conversion failures around ENOSPC. Verification checks minimum header size, entry bounds, nonzero names, monotonic synthetic offsets, valid inode numbers, filetype range, exact end pointer, and block-format fit. Tests should cover small-directory create/remove/rename, large inode-number transitions, ftype on/off filesystems, case-insensitive lookup, shortform-to-block-to-shortform churn, and corrupt local directory data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_sf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dquot_buf.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dquot_buf.c

## Purpose
`xfs_dquot_buf.c` verifies, repairs, and converts on-disk quota records and implements quota inode loading/creation for both legacy superblock quota inode pointers and metadata-directory quota files. It protects quota buffers during read/write/readahead and maps quota health failures to filesystem sickness flags.

## Important APIs, Types, and Functions
Important functions include `xfs_calc_dquots_per_chunk`, `xfs_dquot_verify`, `xfs_dqblk_verify`, `xfs_dqblk_repair`, buffer verifier callbacks for `xfs_dquot_buf_ops` and `xfs_dquot_buf_ra_ops`, timestamp conversion helpers `xfs_dquot_from_disk_ts` and `xfs_dquot_to_disk_ts`, `xfs_dqinode_sick_mask`, `xfs_dqinode_load`, `xfs_dqinode_metadir_create`, userspace-only `xfs_dqinode_metadir_link`, `xfs_dqinode_mkdir_parent`, and `xfs_dqinode_load_parent`.

## Control Flow
`xfs_dquot_verify` validates the embedded `struct xfs_disk_dquot`: magic, version, quota type mask and record type, bigtime compatibility, id consistency when an expected id is provided, and soft-limit timer invariants for nonzero ids. `xfs_dqblk_verify` adds v5 UUID verification around the full `struct xfs_dqblk`. `xfs_dqblk_repair` zeroes a quota record, fills magic/version/type/id, and updates UUID/CRC on CRC-enabled filesystems.

Read verification first checks CRCs for every dquot in the buffer if metadata CRCs are enabled, using either `mp->m_quotainfo->qi_dqperchunk` or a manual chunk calculation during log recovery. It then verifies each dquot with monotonically increasing ids starting at the first record's id. Readahead verification suppresses detailed reporting and marks the buffer not done on failure so a later real read will report through normal verifier paths. Write verification checks structure only because dquot CRCs are refreshed when dquots are flushed into the buffer.

Quota inode loading branches on metadir support. Without metadir, it selects the superblock quota inode field for user/group/project quota, rejects `NULLFSINO`, and calls `xfs_trans_metafile_iget`. With metadir, it resolves a path under `/quota` via `xfs_metadir_load`. Loaded quota inodes must use extents or btree data forks and project id zero; failures mark the corresponding quota sick mask. Metadir create/link helpers wrap metadata directory updates, log inode core, commit, and finish inode setup.

## State and Persistence
Persistent state includes arrays of `struct xfs_dqblk` in quota files, each containing a disk dquot, UUID, and CRC on modern filesystems. Quota inode state may live in legacy superblock inode fields or metadir entries under `quota`. The file itself does not mutate quota counters except repair initialization and metadir inode creation/linking; it verifies and logs metadata inode creation through transaction helpers.

## Dependencies and Integration Points
Dependencies include quota type definitions, mount quota info, CRC helpers, buffer verifier APIs, bigtime conversion, metadata inode lookup, metadir operations, health reporting, and transaction logging. It integrates with log recovery by supporting verification before quota info is initialized.

## Risks and Test Signals
Risks include false corruption reports during quotaoff/log recovery, accepting quota records with invalid timers, mishandling bigtime flags on filesystems without bigtime, and loading a non-quota inode as a quota file. Test signals include quotaon/quotacheck after crash recovery, CRC corruption injection, metadir quota creation/load, legacy quota inode loading, user/group/project type coverage, bigtime quota timers, and readahead verifier behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dquot_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_errortag.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_errortag.h

## Purpose
`xfs_errortag.h` defines the XFS error injection tag namespace and, when included with `XFS_ERRTAG` defined, generates the table of sysfs error-injection knobs and default randomization factors. It is a small but central testability header used by `XFS_TEST_ERROR` sites across XFS.

## Important APIs, Types, and Macros
The header defines consecutive `XFS_ERRTAG_*` numeric constants from `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` set to the count boundary. `XFS_RANDOM_DEFAULT` is the standard default probability denominator. The `XFS_ERRTAGS` macro expands a list of `XFS_ERRTAG(name, sysfs_name, default)` invocations when a consumer defines `XFS_ERRTAG` before inclusion.

Notable tags in this subset include directory/DA failure tags such as `DA_READ_BUF`, `DA_LEAF_SPLIT`, `ATTR_LEAF_TO_NODE`, quota-independent bmap/refcount/rmap finish tags, writeback delay tags, `EXCHMAPS_FINISH_ONE`, metadir reservation, force-zero-range, and zone reset tags. `XFS_ERRTAG_DROP_WRITES` remains defined even though drop-write support was removed so userspace can reject that obsolete value cleanly.

## Control Flow and State
The header uses a dual-include pattern. Bare inclusion defines the numeric constants under the include guard. Inclusion with `XFS_ERRTAG` defined reopens the guarded region and defines `XFS_ERRTAGS` as a macro table. There is no runtime state here; consumers use the constants to index configured error injection behavior and use the generated table to expose or initialize knobs.

## Dependencies and Integration Points
`xfs_exchmaps.c` includes this header to test `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`. Other XFS subsystems include it to inject failures into btree checks, allocation reads, inode flushes, log IO, delayed writes, scrub repair, and metadata reservation paths. The consecutive numbering requirement is important because arrays are sized by the maximum tag.

## Risks and Test Signals
Risks are mostly maintenance-related: adding a tag out of order, failing to update `XFS_ERRTAG_MAX`, or mismatching numeric names and generated sysfs names can break error-injection tests. Default probabilities also matter because some tags are expected to fire always while IO delay/error tags default to lower frequency or millisecond values. Test signals include building both bare and macro-table inclusion paths, sysfs error tag enumeration, and xfstests that rely on specific injection knobs such as `exchmaps_finish_one`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_errortag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.c

## Purpose
`xfs_exchmaps.c` implements the libxfs side of exchange-range / file mapping exchange. It estimates required work and reservations, creates deferred exchange intents, performs one resumable exchange step per transaction, updates quotas and inode sizes, handles reflink/large-extent-count state, and performs post-operation conversion back to shortform formats when possible.

## Important APIs, Types, and Functions
Public functions include `xfs_exchmaps_check_forks`, `xfs_exchmaps_finish_one`, `xfs_exchmaps_estimate_overhead`, `xfs_exchmaps_intent_init_cache`, `xfs_exchmaps_intent_destroy_cache`, `xfs_exchmaps_init_intent`, `xfs_exchmaps_estimate`, `xfs_exchmaps_ensure_reflink`, `xfs_exchmaps_upgrade_extent_counts`, and `xfs_exchange_mappings`. Internal structures include the global `xfs_exchmaps_intent_cache`, `struct xfs_exchmaps_adjacent` for estimate-time neighbor tracking, and `struct xfs_exchmaps_intent` from the header.

## Control Flow
Callers first validate fork eligibility with `xfs_exchmaps_check_forks`, which rejects missing or local-format forks. `xfs_exchmaps_estimate` creates a temporary intent, walks mappings with `xfs_exchmaps_find_mappings`, counts exchange steps, accounts moved data/rt blocks, simulates extent-count deltas with neighbor-aware merge logic, checks extent counter limits, and calls `xfs_exchmaps_estimate_overhead` to reserve bmbt/rmapbt growth. The estimator also honors `XFS_EXCHMAPS_INO1_WRITTEN`, which can skip holes/unwritten mappings from inode1, with special rules for realtime files with multi-FSB allocation units.

Actual scheduling occurs in `xfs_exchange_mappings`. It asserts both inodes are exclusively ILOCKed and the filesystem supports exchange range, creates an intent from the request, queues it with `xfs_exchmaps_defer_add`, sets reflink flags on the opposite inode when needed before rmap updates, and upgrades both inode extent counters if the filesystem supports large counts.

Deferred execution calls `xfs_exchmaps_finish_one`. If work remains, it finds the next pair of different mappings, unmaps both extents, swaps logical offsets, maps the opposite physical mapping into each inode, updates quota block counts, advances the intent cursor, and grows on-disk sizes before post-EOF mappings can exist. When the main range is complete, optional `XFS_EXCHMAPS_SET_SIZES` swaps final sizes. If only post-op work remains, it attempts to convert inode2's attr fork, directory data fork, or symlink target back to shortform and clears reflink flags that can be exchanged away. Returning `-EAGAIN` asks the deferred-op framework for another transaction; error injection can force `-EIO` through `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`.

## State and Persistence
Persistent mutations include bmbt mappings in two inodes, quota block counters, inode disk sizes, reflink flags, large extent-count flags, and possible fork format conversions for attr/dir/symlink data. Recovery state is carried by logged exchange-map intent/done items outside this file; `xfs_exchmaps_finish_one` advances the in-core intent so the deferred item can be relogged for remaining work. COW fork tags are refreshed after completion for data-fork exchanges.

## Dependencies and Integration Points
This file integrates with bmap read/map/unmap APIs, deferred operations and exchange-map log items, transaction and quota accounting, reflink/rmap behavior, inode fork management, directory and attr shortform conversion, remote symlink conversion, extent count limits, tracepoints, error injection, and health marking on corrupt same-physical-block state mismatches.

## Risks and Test Signals
Risks include exchanging delalloc or unexpected mappings, adding mappings past EOF before size logging, underestimating extent/rmap reservation, quota accounting drift, reflink flag inconsistency, and partial-operation recovery after crashes. Realtime unwritten extent skipping is especially subtle because swaps must respect allocation-unit boundaries. Tests should cover crash recovery of deferred exchange intents, reflink and non-reflink pairs, attr-fork exchanges, size-swapping, same-inode exchanges, realtime files, extent-count overflow injection, quota accounting, shortform post-op conversion, and `exchmaps_finish_one` error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.h

## Purpose
`xfs_exchmaps.h` declares the in-core request and intent interfaces for XFS mapping exchange. It defines the state carried across deferred exchange transactions, request parameters used by callers and estimators, internal flags, fork selection helpers, and public entry points implemented by `xfs_exchmaps.c`.

## Important APIs, Types, and Macros
`struct xfs_exchmaps_intent` stores the deferred operation state: list linkage, participating inodes, current offsets in both files, remaining block count, optional final sizes, and flags. `struct xfs_exchmaps_req` is the caller-facing request plus estimator outputs: source inodes, start offsets, block count, operation flags, affected data/rt block counts per inode, reserved blocks, and estimated number of exchange steps.

The internal flag `__XFS_EXCHMAPS_INO2_SHORTFORM` requests post-op conversion of inode2 back to local/shortform format where possible. `XFS_EXCHMAPS_INTERNAL_FLAGS` separates internal-only flags from logged/user-visible flags. `XFS_EXCHMAPS_PARAMS` limits flags accepted by estimation to attr fork selection, size setting, and inode1-written optimization. Inline helpers `xfs_exchmaps_whichfork` and `xfs_exchmaps_reqfork` select data or attr fork from intent/request flags.

## Control Flow and Integration
The header exposes the lifecycle used by higher-level code: estimate via `xfs_exchmaps_estimate` or `xfs_exchmaps_estimate_overhead`, initialize/destroy the slab cache, allocate an intent, precondition reflink and extent-count state in a transaction, finish one deferred step, validate forks, and schedule the exchange with `xfs_exchange_mappings`. The declarations decouple callers and log item code from implementation details in `xfs_exchmaps.c`.

## State and Persistence
The request is mostly transient, but its estimator fields drive transaction reservation and quota reservation decisions. The intent becomes deferred operation state and is eventually represented by exchange-map intent log items, making the operation recoverable across crashes. Negative `xmi_isize*` values mean no size update is required; otherwise the finish path uses them to keep on-disk sizes coherent while moving mappings.

## Dependencies and Integration Points
The header depends on XFS inode, transaction, fork, and flag definitions from surrounding libxfs headers. It is included by exchange-map implementation, log item/deferred-op code, and higher-level exchange-range callers that need estimates and scheduling.

## Risks and Test Signals
Risks include mixing internal flags into logged/public flags, passing unsupported flags to estimation, or failing to initialize the estimator-output fields before use. Fork selection must match both estimator and executor behavior, especially for attr-fork exchanges where size swapping is invalid. Test signals include compile-time checks for flag separation, exchange-range reservation tests, attr/data fork coverage, slab cache init/destroy paths, and crash recovery with partially completed intents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.h -->
