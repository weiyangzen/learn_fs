<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devpts_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/devpts_fs.h

## Purpose
Declares the internal devpts interface used by the Unix98 pty implementation to allocate, publish, and remove pseudo-terminal slave nodes in the devpts filesystem.

## Important APIs, Types, And Functions
With `CONFIG_UNIX98_PTYS`, the header exposes `struct pts_fs_info`, `devpts_mntget()`, `devpts_acquire()`, `devpts_release()`, `devpts_new_index()`, `devpts_kill_index()`, `devpts_pty_new()`, `devpts_get_priv()`, `devpts_pty_kill()`, and `ptm_open_peer()`. Without Unix98 ptys, `ptm_open_peer()` is an inline stub returning `-EIO`.

## Control Flow
PTY master open paths acquire a devpts instance, reserve an index, create the slave dentry with private tty data, and later unlink and release the index when the tty is torn down. `ptm_open_peer()` lets the master side open the peer slave with supplied file flags.

## State And Persistence
State lives in the devpts mount, `pts_fs_info`, allocated pty indices, dentries, and private data attached to devpts nodes. It is filesystem/runtime state, not durable storage.

## Dependencies And Integration Points
Depends on VFS types such as `struct file`, `struct vfsmount`, and `struct dentry`, and on tty internals. It is used by `drivers/tty/pty.c` and devpts filesystem code.

## Risks And Edge Cases
Incorrect acquire/release or index kill ordering can leak pty numbers or leave stale dentries. Namespace and mount-instance handling are sensitive because devpts instances can be per-namespace. The `CONFIG_UNIX98_PTYS=n` stub must keep callers from assuming peer open support.

## Test Signals
PTY tests should cover `/dev/ptmx` open, peer open, close/unlink, multiple devpts mounts, namespace isolation, index reuse, and disabled Unix98 pty builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devpts_fs.h -->
