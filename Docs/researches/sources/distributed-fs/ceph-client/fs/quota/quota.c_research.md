# sources/distributed-fs/ceph-client/fs/quota/quota.c

Purpose: Implements the `quotactl(2)` and `quotactl_fd(2)` syscall front end, including permission checks, command dispatch, user ABI translation, XFS-compatible quota structures, and global quota sync.

Important APIs, types, and functions: Key routines include `check_quotactl_permission()`, `quota_sync_all()`, `qtype_enforce_flag()`, `quota_quotaon()`, `quota_quotaoff()`, `quota_getfmt()`, `quota_getinfo()`, `quota_setinfo()`, `quota_getquota()`, `quota_getnextquota()`, `quota_setquota()`, XFS ABI converters `copy_from_xfs_dqblk()` and `copy_to_xfs_dqblk()`, `quota_setxquota()`, `quota_getxstatev()`, `do_quotactl()`, `quotactl_block()`, and syscall definitions for `quotactl` and `quotactl_fd`.

Control flow: Syscalls split `cmd` into command and quota type, resolve either a block device path or an fd superblock, obtain the proper `s_umount` lock, optionally resolve quota-on file paths first to avoid deadlock, and call `do_quotactl()`. Dispatch validates `s_qcop` support, supported quota type mask, LSM permissions, and command-specific privileges. User ABI structs are translated to generic `qc_*` structs before calling filesystem quota operations.

State and persistence: This file owns no quota storage. It marshals user requests to superblock quota operations that may change on-disk quota files, internal filesystem quota metadata, and quota enforcement state.

Dependencies and integration points: Depends on VFS superblock lookup, mount write access, frozen-superblock handling, security hooks, user-copy helpers, id mapping, block-device lookup, and filesystem `quotactl_ops`. It bridges legacy VFS quota commands and XFS-style `Q_X*` commands.

Risks and test signals: Risks include privilege bypass for owned quota queries, wrong namespace mapping, freeze/write-lock deadlocks, ABI conversion overflow, compat structure alignment bugs, and incorrect project-vs-group state reporting in older XFS stats. Test all commands through both device path and fd syscalls, compat mode, non-init user namespaces, frozen filesystems, quota-on path resolution, and XFS bigtime timer values.
