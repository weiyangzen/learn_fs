# sources/distributed-fs/ceph-client/fs/kernfs/symlink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/symlink.c` implements kernfs symlink node creation and dynamic relative target path generation for VFS `get_link`. The source was read as a complete 155-line file.

## Important APIs, Types, and Functions

The exported creation API is `kernfs_create_link`. Internal helpers are `kernfs_get_target_path`, `kernfs_getlink`, and `kernfs_iop_get_link`. `kernfs_symlink_iops` wires symlink lookup behavior together with common kernfs xattr, setattr, getattr, and permission operations.

## Control Flow

Creation inherits target ownership if target attributes exist, allocates a `KERNFS_LINK` node with mode `0777`, copies namespace tagging from the target when parent namespace support is enabled, stores `target_kn`, takes a reference to the target, and adds the node to the tree. Link resolution allocates a PAGE_SIZE buffer, takes `root->kernfs_rwsem`, computes the relative path from the symlink parent to the target by walking up to a common base and then reverse-filling target names, and returns the buffer via delayed-call cleanup.

## State and Persistence Behavior

The symlink node owns a reference to `target_kn`; path strings are generated on demand and freed after lookup. Ownership is persisted in the symlink node mode/uid/gid and follows target attributes at creation time, not dynamically after later target ownership changes.

## Dependencies and Integration Points

The file depends on node allocation/addition from kernfs directory code, parent/name helpers from `kernfs-internal.h`, `kfree_link` from `libfs.c`, and VFS symlink `get_link` delayed-call conventions. It uses kernfs common inode operations for metadata and permissions.

## Risks and Edge Cases

Relative path synthesis can fail with `-ENAMETOOLONG` when traversal exceeds `PATH_MAX` or `-EINVAL` if no meaningful target path is produced. Correct locking around parent/name traversal is essential during rename. Namespace copying assumes target and parent namespace semantics remain compatible.

## Test Signals

Tests should cover symlinks within one directory, across sibling and ancestor paths, deep paths near `PATH_MAX`, namespace-tagged kernfs trees, target removal lifetime, and concurrent rename/readlink under lockdep and KASAN.
