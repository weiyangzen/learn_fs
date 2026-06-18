# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.h

Purpose: Defines block reservation macros for XFS metadata operations and declares the runtime namespace space reservation helpers.

Important APIs, types, and functions: Defines macros for contiguous bmap/rmap/rtrmap capacities, rmap/rtrmap add space, next extent additions, swap rmap space, directory/attribute tree entry and removal space, inode allocation/free space, add-attr-fork, attr remove/set, direct I/O, growfs, growfs realtime, quota allocation, and qino creation reservations. Declares parent/create/mkdir/link/symlink/remove/rename space helpers.

Control flow: Higher-level reservation functions combine these macros based on operation semantics and feature bits. Macros derive worst-case split and join space from mount btree geometry and directory geometry.

State and persistence: Header-only formulas store no state but depend on mount caches such as btree max/min records, inode allocation geometry, directory geometry, and feature flags.

Dependencies and integration points: Used by transaction reservation code, namespace operation setup, bmap, attr, quota, growfs, and realtime paths.

Risks and test signals: Risks include division-by-zero if geometry is uninitialized, stale formulas for new btree types, under-reserving rtrmap operations, and overflows for large requested extent counts. Test reservation calculations after mount geometry setup, realtime rmap feature paths, attr fork operations, growfs, quota allocation, and ENOSPC stress.
