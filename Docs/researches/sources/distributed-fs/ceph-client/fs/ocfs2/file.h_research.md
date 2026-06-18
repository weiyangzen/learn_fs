# sources/distributed-fs/ceph-client/fs/ocfs2/file.h

Purpose: declares OCFS2 file and inode operation tables plus helper routines used by allocation, truncate, setattr, atime, file-space, and refcount/CoW paths.

Important APIs and types: exposes `ocfs2_fops`, `ocfs2_dops`, lockless variants, `ocfs2_file_iops`, and `ocfs2_special_file_iops`. Defines `struct ocfs2_file_private` with directory seek cookie, backing file pointer, mutex, and file flock lock resource. Declares allocation and size helpers such as `ocfs2_add_inode_data`, `ocfs2_set_inode_size`, `ocfs2_simple_size_update`, `ocfs2_truncate_file`, `ocfs2_extend_no_holes`, `ocfs2_zero_extend`, `ocfs2_change_file_space`, `ocfs2_check_range_for_refcount`, and `ocfs2_remove_inode_range`.

Control flow: no active control flow beyond declarations. The operation table symbols are installed on OCFS2 inodes, and helper declarations allow other modules to participate in file growth, truncation, allocation changes, and VFS attribute handling.

State and persistence behavior: `ocfs2_file_private` is per-open runtime state and owns the file-specific flock lock resource initialized in `file.c` and dropped on release. The declared helpers persist inode size, extents, quota, timestamps, and refcount changes through journaled implementations.

Dependencies and integration points: included by `file.c`, `dlmglue.c`, allocation/refcount code, inode setup, and ioctl paths. It bridges VFS operation registration with OCFS2 internals.

Risks: operation-table variants must remain synchronized except for POSIX lock callbacks. Any layout change to `ocfs2_file_private` must stay compatible with file-lock initialization/freeing and directory llseek cookie use.

Test signals: build coverage, regular and directory open/release, clustered flock paths, localflocks/no-plock mounts choosing lockless operation tables, and external callers of truncate/allocation helpers.
