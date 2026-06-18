# sources/distributed-fs/ceph-client/fs/xfs/xfs_dir2_readdir.c

Purpose: Implements XFS directory iteration for shortform, block, leaf, and node directories, converting XFS directory cookies and filetype metadata into VFS `dir_context` emissions.

Important APIs, types, and functions: Exports `xfs_readdir()` and `xfs_dir3_get_dtype()`. Internal paths are `xfs_dir2_sf_getdents()`, `xfs_dir2_block_getdents()`, `xfs_dir2_leaf_readbuf()`, and `xfs_dir2_leaf_getdents()`.

Control flow: `xfs_readdir()` rejects shutdown/zapped forks, sets up `xfs_da_args`, and selects the reader by directory format. Shortform emits `.` and `..` plus inline entries. Block format reads one block, drops the data-map lock, skips unused regions, and emits live entries. Leaf/node format walks mapped data blocks below `XFS_DIR2_LEAF_OFFSET`, uses a readahead cursor, skips holes/unused records, and advances stable cookies.

State and persistence: Mutates `ctx->pos` and user-visible output only. Invalid names mark the directory data fork sick.

Dependencies and integration points: Uses VFS directory iteration, XFS inode IO/data locks, bmap extent lookup, dir buffer verifiers, block-plugged readahead, health reporting, stats, and tracepoints.

Risks and test signals: Risks are cookie truncation, skipped/repeated entries around holes, lock leaks, invalid name handling, and readahead verifier gaps. Test all directory formats, tiny buffers, seekdir/telldir, concurrent mutation, corrupt names, sparse large directories, and ftype on/off filesystems.
