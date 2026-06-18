# sources/distributed-fs/ceph-client/fs/nilfs2/Kconfig

## Purpose

`Kconfig` exposes the kernel configuration option for NILFS2 filesystem support. It presents NILFS2 as a tristate filesystem that can be built in, built as module `nilfs2`, or disabled.

## Important APIs, Types, and Functions

The only symbol is `CONFIG_NILFS2_FS`, described as "NILFS2 file system support". It selects `BUFFER_HEAD`, `CRC32`, and `LEGACY_DIRECT_IO`, reflecting dependencies on buffer-head metadata, checksum support, and older direct-I/O infrastructure.

## Control Flow

During kernel configuration, selecting this option enables compilation of the NILFS2 objects listed in the directory Makefile. As a module, the resulting module is named `nilfs2`.

## State and Persistence Behavior

The Kconfig file stores no runtime state. Enabling the option makes the kernel capable of mounting and modifying NILFS2 filesystems, which are log-structured and checkpoint/snapshot based.

## Dependencies and Integration Points

It integrates with the top-level filesystem Kconfig and build system. The help text documents continuous snapshotting, crash recovery, read-only snapshot mounts, and unsupported features noted by this tree's text: atime, extended attributes, and POSIX ACLs.

## Risks and Edge Cases

The selected dependencies must stay aligned with implementation requirements. If the code stops depending on legacy direct I/O or gains xattr/ACL support, the Kconfig text and selects should be revisited.

## Test Signals

Configuration tests should cover `CONFIG_NILFS2_FS=y`, `m`, and `n`. Build tests should verify selected dependencies are pulled in and the module name remains `nilfs2`.
