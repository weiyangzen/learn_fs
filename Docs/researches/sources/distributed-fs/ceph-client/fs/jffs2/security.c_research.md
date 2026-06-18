# sources/distributed-fs/ceph-client/fs/jffs2/security.c

## Purpose

`security.c` connects JFFS2 extended attributes to the Linux Security Module initial-label and `security.*` xattr interfaces. It lets newly created inodes receive security labels and exposes get/set handlers for the security xattr namespace.

## Important APIs, Types, And Functions

`jffs2_init_security()` calls `security_inode_init_security()` with `jffs2_initxattrs()` as the filesystem callback. `jffs2_initxattrs()` iterates the LSM-provided `struct xattr` array and stores each label through `do_jffs2_setxattr()` using `JFFS2_XPREFIX_SECURITY`.

`jffs2_security_getxattr()` and `jffs2_security_setxattr()` wrap `do_jffs2_getxattr()` and `do_jffs2_setxattr()`. The exported `jffs2_security_xattr_handler` registers the `XATTR_SECURITY_PREFIX` handler.

## Control Flow

On inode creation, higher-level create paths call `jffs2_init_security()` after the initial inode node has been written. The LSM builds the initial label set and calls back into `jffs2_initxattrs()`, which writes each label until one fails. Later VFS xattr operations dispatch through `jffs2_security_xattr_handler` to get or set a named security xattr.

## State And Persistence Behavior

Security labels are persisted as JFFS2 xattr nodes via the generic xattr subsystem, not by this file directly. Errors from xattr writes propagate back to the create path. This means label persistence depends on available flash space, xattr node CRC/accounting, and write-buffer behavior in the lower layers.

## Dependencies And Integration Points

The file depends on Linux xattr and security APIs, JFFS2 xattr prefixes and do-get/do-set helpers, and create flows in `write.c` and VFS inode creation code. The xattr handler is installed on the superblock through `sb->s_xattr = jffs2_xattr_handlers` in `super.c`.

## Risks And Edge Cases

The initial inode node may already exist before label attachment fails, so callers must handle partially created objects through normal cleanup paths. Label writes can fail due to ENOSPC, memory pressure, or flash IO errors. Namespace prefix correctness is security-sensitive: all operations here must use `JFFS2_XPREFIX_SECURITY`.

## Test Signals

Useful tests include creating files under SELinux/Smack/AppArmor label initialization, multiple initial xattrs, failure of the second label write, get/set/remove of `security.*` xattrs, and xattr behavior under low-space conditions.
