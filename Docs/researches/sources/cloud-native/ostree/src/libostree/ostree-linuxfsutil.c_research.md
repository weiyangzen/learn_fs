# sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.c

## Purpose
This file wraps Linux filesystem ioctls used by OSTree while isolating problematic kernel header includes. It supports toggling the immutable flag and freezing/thawing filesystems.

## Important APIs and Control Flow
`_ostree_linuxfs_fd_alter_immutable_flag(fd, new_immutable_state, cancellable, error)` uses `EXT2_IOC_GETFLAGS` and `EXT2_IOC_SETFLAGS` to read and change `EXT2_IMMUTABLE_FL`. A static atomic `no_alter_immutable` disables future attempts after `EPERM`; unsupported filesystems (`EOPNOTSUPP`, `ENOTTY`) are silently ignored. `_ostree_linuxfs_filesystem_freeze(fd)` and `_ostree_linuxfs_filesystem_thaw(fd)` wrap `FIFREEZE` and `FITHAW` with `TEMP_FAILURE_RETRY`.

## State, Dependencies, Integration, Risks, and Tests
Persistent state changes occur on the target inode or mounted filesystem. Process state includes the global atomic capability-disable flag. Dependencies include `ext2fs/ext2_fs.h`, `linux/fs.h`, `sys/ioctl.h`, libglnx error helpers, and `ostree-linuxfsutil.h`. Integration points include commit/deployment code that protects files or coordinates filesystem snapshots. Risks are silently skipped protection on unsupported/unprivileged systems, process-wide disable after one `EPERM`, and freeze/thaw deadlocks if callers fail to pair operations. Tests need privilege-aware coverage and should include unsupported filesystem behavior.
