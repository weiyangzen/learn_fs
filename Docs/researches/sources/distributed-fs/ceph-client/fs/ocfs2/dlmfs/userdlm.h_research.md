# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.h

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.h` declares the shared DLMFS userspace-lock data structures, constants, and function interfaces used by `dlmfs.c` and `userdlm.c`. The source was read as a complete 95-line header.

## Important APIs, Types, and Functions

The header defines `USER_LOCK_*` flag bits, `USER_DLM_LOCK_ID_MAX_LEN`, `struct user_lock_res`, `struct dlmfs_inode_private`, `struct dlmfs_filp_private`, `DLMFS_MAGIC`, and `DLMFS_I()`. It declares `user_dlm_worker` and all public user-DLM helpers: initialization, destroy, cluster lock/unlock, LVB read/write, cluster register/unregister, and locking protocol setup.

`struct user_lock_res` contains the spinlock-protected user lock state: flags, lock name and length, current level, local PR/EX holder counters, OCFS2 DLM lksb, requested and blocking levels, wait queue, and work item. `struct dlmfs_inode_private` embeds the user lock resource for regular files, a cluster connection for directories, a parent inode reference for file teardown ordering, and the VFS inode. `struct dlmfs_filp_private` stores the lock level acquired by one open file.

## Control Flow

The header has no runtime control flow. Its inline `DLMFS_I()` maps from a VFS inode to the containing `dlmfs_inode_private` with `container_of()`.

## State and Persistence Behavior

The header defines in-memory state layouts only. `USER_LOCK_ATTACHED`, `USER_LOCK_BUSY`, `USER_LOCK_BLOCKED`, `USER_LOCK_IN_TEARDOWN`, `USER_LOCK_QUEUED`, and `USER_LOCK_IN_CANCEL` describe the state machine implemented in `userdlm.c`. No persistent storage format is defined.

## Dependencies and Integration Points

The header depends on Linux module/fs/types/workqueue declarations and OCFS2 stackglue types included indirectly by implementation files. It is the contract between the VFS layer in `dlmfs.c` and the locking policy in `userdlm.c`; both must agree on embedded inode layout, lock-resource layout, and workqueue ownership. `DLMFS_MAGIC` identifies the mounted virtual filesystem.

## Risks and Edge Cases

Layout changes affect `container_of()` users and VFS inode allocation, so `ip_vfs_inode` must remain the embedded inode used by `DLMFS_I()`. Lock names are capped at 32 bytes including the implementation's validation margin; callers must reject overly long dentries before copying into `l_name`. Flag meanings are coupled to AST/BAST/unlock AST behavior, so adding flags or lock levels requires updating the state machine in `userdlm.c`.

## Test Signals

Compile coverage verifies prototype and layout agreement between `dlmfs.c` and `userdlm.c`. Runtime signals include correct `DLMFS_I()` behavior for allocated inodes, successful workqueue processing through `l_work`, name-length validation before `user_dlm_lock_res_init()`, and `DLMFS_MAGIC` appearing in statfs output for mounted DLMFS.
