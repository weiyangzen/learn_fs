# sources/distributed-fs/ceph-client/fs/f2fs/Makefile

## Purpose

`fs/f2fs/Makefile` defines how the F2FS kernel object is assembled from mandatory and optional source files.

## Important Build Rules

`obj-$(CONFIG_F2FS_FS) += f2fs.o` builds the aggregate F2FS object when the root filesystem symbol is enabled. The base `f2fs-y` list includes directory, file, inode, name, hash, superblock, inline-data, checkpoint, garbage collection, data, node, segment, recovery, shrinker, extent cache, and sysfs code. Conditional additions include `debug.o` for `CONFIG_F2FS_STAT_FS`, `xattr.o` for `CONFIG_F2FS_FS_XATTR`, `acl.o` for `CONFIG_F2FS_FS_POSIX_ACL`, `verity.o` for `CONFIG_FS_VERITY`, `compress.o` for `CONFIG_F2FS_FS_COMPRESSION`, and `iostat.o` for `CONFIG_F2FS_IOSTAT`.

## Control Flow

The Makefile mirrors Kconfig feature selection. Core mount and filesystem operation code is always part of `f2fs.o` when F2FS is enabled. Optional feature objects are linked only when their config symbols are enabled, which means callers must use conditional declarations or stubs, as seen in `acl.h`.

## State and Persistence Behavior

This file has no runtime state, but it controls which code can interpret or produce feature-specific persistent metadata. Including or excluding `compress.o`, `acl.o`, or `xattr.o` changes support for compressed clusters, POSIX ACL xattrs, and generic xattrs in the built filesystem.

## Dependencies and Integration Points

It integrates with the kernel kbuild system and symbols defined in `Kconfig`. It is the bridge between configuration and implementation for files researched in this subset: `checkpoint.o` is mandatory, `acl.o` is conditional on POSIX ACL support, and `compress.o` is conditional on compression support.

## Risks and Edge Cases

Build breakage can occur if optional code is referenced without a stub when the object is not linked. Feature combinations must stay aligned with Kconfig dependencies. Because `checkpoint.o` is mandatory, checkpoint regressions affect every F2FS build.

## Test Signals

Compile F2FS with minimal config, full config, xattr-only, ACL-enabled, compression-enabled, fs-verity-enabled, and iostat-enabled variants. Verify object inclusion with `make V=1` or generated build artifacts.
