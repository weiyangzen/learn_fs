# sources/distributed-fs/ceph-client/fs/ext4/Makefile

## Purpose

`fs/ext4/Makefile` defines how the ext4 kernel object is assembled from core source files and optional feature objects. It is the build-system map from `CONFIG_EXT4_*`, `CONFIG_FS_VERITY`, and `CONFIG_FS_ENCRYPTION` to compiled code.

## Important APIs, types, and functions

- `obj-$(CONFIG_EXT4_FS) += ext4.o` builds ext4 as built-in or module based on the main Kconfig symbol.
- `ext4-y` lists core objects, including block allocation, bitmap, block validity, directories, journaling glue, extents, file operations, fsmap, fsync, hash, inode allocation, indirect blocks, inline data, ioctl, mballoc, migration, MMP, move extent, namei, page IO, readpage, resize, superblock, symlink, sysfs, xattrs, fast commit, and orphan handling.
- `ext4-$(CONFIG_EXT4_FS_POSIX_ACL) += acl.o`.
- `ext4-$(CONFIG_EXT4_FS_SECURITY) += xattr_security.o`.
- `ext4-test-objs` and `obj-$(CONFIG_EXT4_KUNIT_TESTS)` build ext4 KUnit tests.
- `ext4-$(CONFIG_FS_VERITY) += verity.o` and `ext4-$(CONFIG_FS_ENCRYPTION) += crypto.o`.

## Control flow

There is no runtime control flow. Kbuild concatenates object lists according to config symbols and links them into `ext4.o` or `ext4.ko`. Optional files contribute symbols that core ext4 code references through conditional compilation.

## State and persistence behavior

The Makefile does not manage state directly, but object inclusion controls available runtime features and therefore how persistent ext4 metadata is interpreted. Encryption contexts need `crypto.o`; verity metadata needs `verity.o`; ACL/security xattrs need their handlers.

## Dependencies and integration points

The file is coupled to `Kconfig`, ext4 source file names, and Kbuild conventions for composite objects. It also lists KUnit test object composition separately from the production ext4 object.

## Risks and edge cases

Missing an object from `ext4-y` can produce link failures or silently remove feature support. Adding a config-gated source without matching Kconfig dependencies can leave unresolved symbols in some build matrices. Test object lists must not be linked into production ext4 unless KUnit is selected.

## Test signals

Build ext4 built-in and as a module across ACL/security/encryption/verity/KUnit combinations, verify expected symbols are present, and run `modinfo` or link-map checks for optional object inclusion.
