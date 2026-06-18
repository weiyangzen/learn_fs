# sources/distributed-fs/ceph-client/fs/nsfs.c

## Purpose

`nsfs.c` implements the namespace pseudo filesystem used for namespace file descriptors such as `/proc/<pid>/ns/*`. It provides stable dentries/inodes for namespace objects, namespace ioctls, namespace path opening helpers, exportfs file-handle support, pseudo-fs initialization, and active-reference helpers for namespace proxy state.

## Important APIs, Types, and Functions

Important exported helpers include `nsfs_get_root()`, `ns_get_path_cb()`, `ns_get_path()`, `open_namespace_file()`, `open_namespace()`, `open_related_ns()`, `ns_get_name()`, `proc_ns_file()`, `ns_match()`, `is_current_namespace()`, `nsfs_init()`, `nsproxy_ns_active_get()`, and `nsproxy_ns_active_put()`. The main file op is `ns_ioctl()`. Exportfs support is provided by `nsfs_encode_fh()`, `nsfs_fh_to_dentry()`, `nsfs_export_open()`, and `nsfs_export_permission()`. Stashed dentry integration uses `nsfs_init_inode()`, `nsfs_put_data()`, and `nsfs_stashed_ops`.

## Control Flow

Namespace paths are created through `path_from_stashed()` using the namespace's stashed dentry and the global `nsfs_mnt`; this consumes or transfers namespace references depending on the helper. `ns_ioctl()` first validates the command and permissions, then handles related namespace opening, type/owner/id queries, pid translation relative to pid namespaces, mount namespace info, and next/previous mount namespace iteration with optional info copy and fd publication. Exportfs encoding writes namespace id/type/inum into a file handle; decoding validates the handle, looks up the namespace in the namespace tree under RCU, checks visibility/ownership rules, obtains a reference, and recreates a path from the stashed dentry.

## State and Persistence Behavior

Global state is `nsfs_mnt` and `nsfs_root_path`. Each nsfs inode stores `struct ns_common *` in `i_private`, uses the namespace inode number, and takes an active namespace reference in `nsfs_init_inode()`. Eviction drops the active ref, clears the inode, and calls the namespace put operation. Stashed dentries allow namespace file descriptors and bind mounts to preserve access to namespaces after tasks exit, and can resurrect namespace subtrees when other objects still pin them.

## Dependencies and Integration Points

The file integrates with proc namespace operations, namespace-specific `get/put/get_parent` callbacks, mount namespace tree iteration, pid/user/net/ipc/time/uts/cgroup namespace internals, pseudo fs helpers, exportfs, fd helpers, seq path display, and VFS file opening. It deliberately clears `SB_NOUSER` on the mounted nsfs superblock so namespace file handles can be user-visible where allowed.

## Risks and Edge Cases

Visibility and lifetime checks are critical. Some exportfs decoding is intentionally racy around active references but relies on `nsfs_init_inode()` resurrection behavior. PID namespace decoding rejects inactive current pid namespaces without a child reaper. Next/previous mount namespace ioctls require `may_see_all_namespaces()`. Extensible ioctl size handling must be forward/backward compatible. Namespace references are consumed by path creation helpers, so double put or leaked references are key risks.

## Test Signals

Signals include proc namespace fd open/readlink/ioctl tests, user namespace owner uid queries, pid translation ioctls, mount namespace info and next/previous iteration, permission checks without namespace visibility, bind-mounted namespace lifetime after task exit, exportfs file-handle encode/decode/open, and namespace teardown with active nsproxy references.
