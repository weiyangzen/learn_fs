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
