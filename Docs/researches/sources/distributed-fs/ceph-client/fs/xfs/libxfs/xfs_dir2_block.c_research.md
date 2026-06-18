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
