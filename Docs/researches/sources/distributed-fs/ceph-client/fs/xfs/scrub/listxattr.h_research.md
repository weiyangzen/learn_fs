<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.h

Purpose: Declares callback types and the public xattr walker used by XFS scrub code.

Important APIs, types, and functions: Defines `xchk_xattr_fn` for per-attribute callbacks with flags, name, optional value pointer, value length, and private data. Defines `xchk_xattrleaf_fn` for per-leaf progress callbacks. Declares `xchk_xattr_walk()`.

Control flow: Callers provide callbacks and private state, hold the inode ILOCK, and invoke `xchk_xattr_walk()` to receive each attr entry in fork order. The leaf callback can be used for periodic processing between node-format leaf blocks.

State and persistence: No state is defined. Callback consumers own any state transitions; the walker is read-only.

Dependencies and integration points: Depends on `struct xfs_scrub` and `struct xfs_inode`. It is an integration point for attr, parent-pointer, and repair code that needs a uniform attr enumeration surface.

Risks and test signals: Callback ABI mistakes can mishandle remote values where `value == NULL`. Test consumers with local and remote attrs, namespace flags, long names/values, and callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.h -->
