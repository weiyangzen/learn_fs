# Research: sources/distributed-fs/ceph-client/include/linux/path.h

Purpose: `path.h` defines the VFS `struct path` pair of mount and dentry plus reference-management helpers.

Important APIs/types/functions: `struct path` contains `struct vfsmount *mnt` and `struct dentry *dentry` with layout randomization. APIs are `path_get()`, `path_put()`, `path_equal()`, and `__free_path_put` for cleanup attributes.

Control flow and state: path users hold a counted reference with `path_get()` and release it with `path_put()`. `path_equal()` compares identity by pointer equality of both mount and dentry. State is the referenced VFS object pair; persistence is lifetime-managed by mount/dentry refcounts.

Dependencies and integration points: integrates throughout VFS, file descriptors, namespace lookup, open paths, mount handling, security hooks, and cleanup-attribute based automatic release.

Risks and test signals: risks include leaking references, using uninitialized paths with cleanup attributes, comparing dentries without mount context, and use-after-put. Tests should exercise lookup/open/close paths, mount namespace cases, cleanup-attribute paths initialized to zero, and refcount debugging.
