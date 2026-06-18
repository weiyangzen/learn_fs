# sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.h

## Purpose
`refcounttree.h` declares the OCFS2 refcount tree interface used by inode, xattr, truncate, write, and reflink paths. It exposes the in-memory tree lock/cache structure and the operations required to mutate shared extents safely.

## Important APIs, types, and functions
`struct ocfs2_refcount_tree` contains rb-tree linkage, root block number, generation, kref lifetime, local rw semaphore, DLM lock resource, removal flag, metadata-cache lock, `ocfs2_caching_info`, I/O mutex, and superblock pointer. `struct ocfs2_post_refcount` lets callers attach extra journal credits and a callback to run inside COW or add-refcount transactions. Declarations cover tree lock/unlock/purge, refcount increase/decrease, COW for inode data and xattrs, duplicate-by-page/JBD helpers, writeback sync, adding refcount flags, removing tree ownership, reflink ioctl/remap helpers, double-inode lock helpers, and destination size update.

## Control flow
Callers lock a tree with `ocfs2_lock_refcount_tree`, perform record or extent changes through the exported helpers, then release with `ocfs2_unlock_refcount_tree`. File write paths use `ocfs2_refcount_cow` before modifying shared data. Truncate/delete paths prepare credits and decrease physical refcounts. Xattr code uses the xattr-specific COW and delete-need helpers. Reflink and clone operations use the inode lock helpers and remap/update functions to share physical extents.

## State and persistence
The header itself has no persistent state, but it defines the runtime object that protects persistent refcount blocks. Its API assumes callers already hold the relevant inode locks and pass journal handles, metadata allocators, buffer heads, and deallocation contexts according to the implementation's lock ordering.

## Dependencies and integration points
It depends on OCFS2 core types, buffer heads, JBD handles, extent trees, cached deallocation contexts, and inode/xattr structures defined elsewhere. It is included by OCFS2 allocation, file, inode, xattr, and reflink paths that need shared-extent behavior.

## Risks and test signals
Interface risks include callers forgetting to hold the refcount tree lock, underestimating `ocfs2_post_refcount.credits`, using page duplication where JBD duplication is required, or mixing inodes that point to different refcount trees. Test signals are compile coverage of all call sites, lockdep for lock/unlock pairing, reflink range tests, xattr COW tests, and ENOSPC paths where prepared credits or metadata reservations are too small.
