<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/inode.c -->
# sources/distributed-fs/ceph-client/fs/devpts/inode.c

Purpose: implements the `devpts` filesystem used for Unix98 pseudo-terminal slave nodes, including mount option parsing, per-instance PTY allocation, `/dev/pts/ptmx`, sysctl limits, and creation/removal of numbered slave device nodes.

Important APIs/types/functions: exports `devpts_mntget`, `devpts_acquire`, `devpts_release`, `devpts_new_index`, `devpts_kill_index`, `devpts_pty_new`, `devpts_get_priv`, and `devpts_pty_kill`. Key state includes global sysctl values `pty_limit`, `pty_reserve`, `pty_count`; per-mount `struct pts_fs_info` with an `ida` of allocated PTYs, mount options, superblock, and borrowed ptmx inode; and `struct pts_mount_opts` for uid/gid/mode/ptmxmode/reserve/max.

Control flow: filesystem context initialization allocates `pts_fs_info`, initializes the IDA and defaults, and reserves PTYs for the initial mount namespace. Mount parsing accepts uid, gid, mode, ptmxmode, newinstance, and max. `devpts_fill_super` creates an anonymous superblock, root directory, and a `ptmx` character node with major `TTYAUX_MAJOR` minor 2. PTY allocation increments the global count, checks global limit minus reserve for non-reserved mounts, and allocates a per-instance IDA index. `devpts_pty_new` creates a numbered character-device inode under the devpts root, assigns uid/gid from mount options or current credentials, stores private TTY data in `d_fsdata`, marks the dentry persistent, and sends fsnotify create. `devpts_pty_kill` clears private data, drops link count, unhashes, emits unlink notification, and makes the persistent dentry discardable.

State and persistence: devpts is in-memory. Per-mount IDA state persists for the life of the superblock. The global PTY count and sysctl limits persist for the kernel lifetime. Device nodes persist while the corresponding PTY exists; removal discards their dcache references. Mount options persist in `s_fs_info` and remount updates ptmx mode plus node creation defaults.

Dependencies and integration: integrates with the TTY core, `devpts_fs.h`, mount/namei helpers, fs_context parser, IDA allocator, sysctl under `kernel/pty`, VFS simple directory operations, dcache persistent helpers, fsnotify, user namespace mount support (`FS_USERNS_MOUNT`), and path helpers for finding a suitable devpts mount when `/dev/ptmx` is a symlink or bind mount.

Risks: PTY accounting must roll back on allocation failure or the system can leak capacity. `devpts_mntget` path walking must reject mismatched devpts instances, especially with bind-mounted `ptmx`. Mount option remount semantics intentionally reset defaults in ways that are UAPI-sensitive. Persistent dentry handling must pair `devpts_pty_new` and `devpts_pty_kill` to avoid stale slave nodes or dangling `d_fsdata`.

Test signals: mount devpts with uid/gid/mode/ptmxmode/max combinations, open `/dev/ptmx` through direct, symlink, and bind-mount layouts, allocate until global and per-instance limits, verify reserve behavior outside the initial namespace, create/remove PTYs while watching fsnotify, remount ptmxmode, and run PTY stress tests under mount namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/inode.c -->
