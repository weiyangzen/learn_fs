# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.h

Purpose: Defines `struct xfs_ifork` and the public fork/extent-tree APIs used throughout XFS inode and bmap code.

Important APIs and types: `struct xfs_ifork` stores fork bytes, btree root, extent tree sequence, tree height, data pointer, extent count, root size, format, and lazy-read flag. Macros estimate worst-case extent count growth for common operations. Inline helpers expose max extents, fork format, fork extent counts, disk fork extent counters, cursor peeking, iteration via `for_each_xfs_iext`, and `xfs_need_iread_extents`.

Control flow: the header provides selection and iteration primitives. `xfs_iext_next_extent` and `xfs_iext_prev_extent` move a cursor then decode the pointed extent; peek helpers copy the cursor first. `xfs_need_iread_extents` uses acquire semantics paired with release stores during fork formatting to ensure readers see valid format state when lazy btree extents must be loaded.

State and persistence: the state is in-core but mirrors persistent fork format and extent counts. Disk extent-count helpers understand the large extent counter feature and choose the correct dinode fields.

Dependencies and integration: included by inode conversion, bmap, attr, recovery, and flush code. It declares functions implemented by `xfs_inode_fork.c` and `xfs_iext_tree.c`.

Risks and test signals: errors in max extent limits or disk counter selection affect ENOSPC/EFBIG behavior and verifier decisions. Test signals include feature matrices for large extent counters, attr/data/CoW fork iteration, lazy btree extent read races, and build coverage for all consumers of fork constants.
