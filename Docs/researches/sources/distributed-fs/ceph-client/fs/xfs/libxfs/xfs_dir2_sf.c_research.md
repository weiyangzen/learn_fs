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
