# sources/distributed-fs/ceph-client/fs/btrfs/Makefile

## Purpose
Defines how the monolithic `btrfs.o` object is built, including warning policy, core source membership, and conditional feature/test objects. It is the build-system map from Kconfig symbols to Btrfs compilation units.

## Important APIs, Types, And Functions
The file uses kbuild variables. `subdir-ccflags-y` enables a subset of `W=1` warnings and disables several noisy `-Wextra` diagnostics. `obj-$(CONFIG_BTRFS_FS) := btrfs.o` makes Btrfs conditional on the main Kconfig symbol. `btrfs-y` lists core objects such as `super.o`, `ctree.o`, `accessors.o`, `xattr.o`, `async-thread.o`, `inode.o`, `volumes.o`, `send.o`, `qgroup.o`, and many more. Conditional additions include `acl.o`, `ref-verify.o`, `zoned.o`, `verity.o`, and multiple `tests/*.o` objects.

## Control Flow
During kbuild, enabled Kconfig symbols expand the object lists. Core `btrfs-y` objects are linked into `btrfs.o` whenever `CONFIG_BTRFS_FS` is enabled. Feature symbols append their specific objects. If both `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` and `CONFIG_BLK_DEV_ZONED=y` are set, `tests/zoned-tests.o` is added as well.

## State And Persistence
This file has no runtime state, but it persists build policy through compiler flags and link membership. The produced state is a kernel built-in or module containing exactly the selected objects.

## Dependencies And Integration Points
It integrates Kconfig with Btrfs source files. It directly ties `CONFIG_BTRFS_FS_POSIX_ACL` to `acl.o`, `CONFIG_BTRFS_DEBUG` to `ref-verify.o`, `CONFIG_BLK_DEV_ZONED` to zoned support, `CONFIG_FS_VERITY` to verity support, and `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` to developer regression test objects.

## Risks
Missing an object from `btrfs-y` can create link errors or, worse, omit runtime functionality. Overly aggressive warnings can break builds on some compilers, while disabled warnings may hide real issues. Conditional test objects must match the feature symbols they exercise or module-load sanity tests can become incomplete.

## Test Signals
Useful signals are allmodconfig/allyesconfig builds, minimal Btrfs module builds, ACL/debug/zoned/verity combinations, and sanity-test builds. Compiler-warning CI should confirm the selected warning subset remains supported across GCC and Clang.
