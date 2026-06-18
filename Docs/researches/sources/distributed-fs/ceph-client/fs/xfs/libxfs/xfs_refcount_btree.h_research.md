# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.h

## Purpose
`xfs_refcount_btree.h` declares the on-disk refcount btree block layout helpers and the public cursor/geometry functions for per-AG refcount btrees.

## Important APIs and layout
`XFS_REFCOUNT_BLOCK_LEN` defines the v5 short btree header size. `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, and `XFS_REFCOUNT_PTR_ADDR` compute record, key, and pointer addresses inside a refcountbt block; these macros are also part of the userspace-visible libxfs contract. The header declares cursor creation, max records, maxlevels computation, size/reserve calculations, staged-tree commit, and cursor-cache lifecycle functions.

## Control flow and state
The declarations support three main flows: normal refcount update cursors, mount-time geometry/reservation setup, and online repair staging. Persistent state is still AGF-rooted, but this header defines how code accesses btree block interiors and asks the implementation to compute space requirements.

## Dependencies, risks, and test signals
The header depends on generic XFS btree types, mount/perag types, and staged fake roots. Address macros must match the on-disk format exactly; any mismatch corrupts userspace tools and kernel traversal. Tests should include block layout validation across leaf and internal nodes, min block size geometry, and staged repair commit callers.
