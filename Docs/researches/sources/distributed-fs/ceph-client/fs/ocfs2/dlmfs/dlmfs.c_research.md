# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/dlmfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/dlmfs.c` implements the VFS-facing OCFS2 DLMFS filesystem, a minimal kernel interface that lets userspace create DLM domains as directories and lock resources as regular files. Opening a file acquires a cluster lock, closing releases it, reading/writing accesses the lock value block, and polling reports blocking AST pressure. The source was read as a complete 637-line file.

## Important APIs, Types, and Functions

The module lifecycle is `init_dlmfs_fs()` and `exit_dlmfs_fs()`, registered with `module_init()`/`module_exit()`. Filesystem registration uses `struct file_system_type dlmfs_fs_type` with name `ocfs2_dlmfs`, `MODULE_ALIAS_FS("ocfs2_dlmfs")`, `dlmfs_init_fs_context()`, `dlmfs_get_tree()`, and `dlmfs_fill_super()`.

File operations are `dlmfs_file_open()`, `dlmfs_file_release()`, `dlmfs_file_poll()`, `dlmfs_file_read()`, `dlmfs_file_write()`, and default llseek. Inode operations are `dlmfs_mkdir()`, `dlmfs_create()`, `dlmfs_unlink()`, `dlmfs_file_setattr()`, plus `simple_lookup`, `simple_rmdir`, and `simple_getattr`. Superblock operations include `dlmfs_alloc_inode()`, `dlmfs_free_inode()`, `dlmfs_evict_inode()`, and `inode_just_drop()`.

Important state is held in `struct dlmfs_inode_private` and `struct dlmfs_filp_private` from `userdlm.h`, the `dlmfs_inode_cache` slab cache, and the exported `struct workqueue_struct *user_dlm_worker`. The read-only module parameter `capabilities` reports `"bast stackglue"`.

## Control Flow

Mounting `ocfs2_dlmfs` creates an anonymous nodev superblock with a root directory. At the root, `mkdir` is allowed and creates a DLM domain directory. `dlmfs_mkdir()` validates the domain name length, allocates a directory inode, calls `user_dlm_register()` to connect to the OCFS2 cluster stack, stores the returned `ocfs2_cluster_connection`, and makes the dentry persistent. Non-root directories allow regular file creation through `dlmfs_create()`, which rejects names longer than `USER_DLM_LOCK_ID_MAX_LEN - 1` and names beginning with `$`, allocates a file inode, and initializes its embedded `user_lock_res`.

Opening a regular file decodes VFS open flags: read-only becomes PR mode, write-only/read-write becomes EX mode, and `O_NONBLOCK` becomes `DLM_LKF_NOQUEUE`. `dlmfs_file_open()` allocates per-file private data, calls `user_dlm_cluster_lock()`, maps noqueue `-EAGAIN` to `-ETXTBSY`, and stores the acquired level. `dlmfs_file_release()` calls `user_dlm_cluster_unlock()` for the recorded level and frees the file-private structure.

Reads call `user_dlm_read_lvb()` and return zero bytes if the LVB is invalid. Writes clamp the user count to `DLM_LVB_LEN`, copy data from userspace, require an EX lock through `user_dlm_write_lvb()`, and advance `ppos`. `dlmfs_file_poll()` waits on the user lock event queue and reports `EPOLLIN|EPOLLRDNORM` when `USER_LOCK_BLOCKED` is set by a BAST.

Inode eviction destroys live file locks via `user_dlm_destroy_lock()` unless teardown is already active, then drops the parent inode reference. Directory eviction unregisters the cluster connection. Module initialization creates the inode cache, creates a reclaim-safe per-CPU workqueue named `user_dlm`, sets the locking protocol, and registers the filesystem; exit unregisters the filesystem, destroys the workqueue, runs `rcu_barrier()`, and destroys the inode cache.

## State and Persistence Behavior

DLMFS is a virtual filesystem with no on-disk persistence. Persistent-looking dentries are in-memory VFS objects. Domain directories hold cluster connections; lock files hold embedded `user_lock_res` state and a parent inode reference so lock resources are torn down before their domain connection disappears. Open file descriptors hold the acquired lock level in `dlmfs_filp_private`.

The file size is forced to `DLM_LVB_LEN`; `setattr` masks out size changes and only applies normal inode attribute updates. File reads and writes operate on the DLM lock value block associated with the current lock, not on page cache contents.

## Dependencies and Integration Points

This file depends on Linux VFS/fs_context APIs, simple directory helpers, slab allocation, workqueues, poll, uaccess, and OCFS2 stackglue through `userdlm.h`. It integrates directly with `userdlm.c` for cluster connect/disconnect, lock acquisition/release, LVB access, and BAST workqueue processing. Userspace integration is the mounted `ocfs2_dlmfs` filesystem ABI: directories are domains, files are locks, open mode selects lock level, and poll/read/write expose blocking and LVB behavior.

## Risks and Edge Cases

The filesystem ABI is intentionally small but strict. Reserved lock names beginning with `$` are rejected so userspace cannot collide with internal DLM resources such as `$RECOVERY`. `O_APPEND` is cleared because append semantics do not make sense for fixed-size LVB writes. `read()` requires at least a PR lock and `write()` requires EX through `BUG_ON()` checks in `userdlm.c`, so VFS paths must ensure read/write are only used on successfully opened files.

Teardown ordering is delicate: file inodes must release locks before domain directories unregister the cluster connection, and `USER_LOCK_IN_TEARDOWN` avoids duplicate destruction. Error cleanup in `dlmfs_mkdir()` must handle partially allocated inodes and failed cluster registration. The read-only module parameter enforces capability discovery without allowing runtime mutation.

## Test Signals

Useful tests include mounting and unmounting `ocfs2_dlmfs`, creating/removing domain directories and lock files, invalid domain and lock names, opening locks in PR and EX modes, noqueue open conflict returning `-ETXTBSY`, close/unlink teardown while locks are held, read/write bounds at `DLM_LVB_LEN`, poll wakeup after remote BAST, and module load/unload leak checks. Build signals include successful registration of `ocfs2_dlmfs` and presence of the `capabilities` parameter reporting `bast stackglue`.
