# sources/distributed-fs/ceph-client/fs/btrfs/acl.h

## Purpose
Declares the Btrfs ACL API and provides compile-time stubs when POSIX ACL support is disabled. It lets the rest of Btrfs reference ACL hooks without scattering feature-conditionals through call sites.

## Important APIs, Types, And Functions
When `CONFIG_BTRFS_FS_POSIX_ACL` is enabled, it declares `btrfs_get_acl()`, `btrfs_set_acl()`, and `__btrfs_set_acl()`, with forward declarations for `struct posix_acl`, `struct inode`, `struct btrfs_trans_handle`, `struct mnt_idmap`, and `struct dentry`. When disabled, `btrfs_get_acl` and `btrfs_set_acl` are defined as `NULL`, and `__btrfs_set_acl()` is an inline stub returning `-EOPNOTSUPP`.

## Control Flow
This header has no runtime control flow beyond the disabled inline stub. Compile-time configuration decides whether inode operation tables receive real ACL functions or NULL hooks.

## State And Persistence
The header itself has no state. With ACL support disabled, attempts to set ACLs through internal paths fail without persisting xattrs. With support enabled, state behavior is defined by `acl.c`.

## Dependencies And Integration Points
It connects Kconfig, the Makefile's conditional `acl.o`, Btrfs inode operations, and internal transaction code that may need `__btrfs_set_acl()`. The disabled stubs keep builds valid when `CONFIG_BTRFS_FS_POSIX_ACL=n`.

## Risks
The main risk is mismatched expectations between call sites and configuration. Callers that require ACL persistence must handle `-EOPNOTSUPP` when disabled. Defining VFS hooks as NULL must remain acceptable to the inode operation setup code.

## Test Signals
Build coverage should include ACL enabled and disabled configurations. Runtime tests in disabled builds should confirm ACL syscalls fail with unsupported-operation behavior and do not create ACL xattrs, while enabled builds should use the real implementation.
