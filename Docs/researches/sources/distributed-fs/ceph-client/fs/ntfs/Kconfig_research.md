# sources/distributed-fs/ceph-client/fs/ntfs/Kconfig

## Purpose

This Kconfig file declares the legacy NTFS filesystem driver and its optional debugging and POSIX ACL support.

## Important APIs, Types, and Functions

Symbols are `NTFS_FS`, `NTFS_DEBUG`, and `NTFS_FS_POSIX_ACL`. `NTFS_FS` is a tristate that selects `NLS` and `FS_IOMAP`. `NTFS_DEBUG` depends on `NTFS_FS` and enables extra consistency checks/debug messages. `NTFS_FS_POSIX_ACL` depends on `NTFS_FS` and selects `FS_POSIX_ACL`.

## Control Flow

There is no runtime control flow. Kconfig selects dependencies and controls whether the NTFS driver is built in, modular, or omitted, and whether debug/ACL code paths are compiled.

## State and Persistence Behavior

The file owns no runtime state. It influences compiled feature availability and module build output.

## Dependencies and Integration Points

It integrates with the NTFS Makefile, NLS subsystem, iomap infrastructure, POSIX ACL support, and optional debug/sysctl behavior documented in the help text.

## Risks and Edge Cases

Selecting `FS_IOMAP` is required by the current NTFS address-space and iomap code. The ACL help text notes Linux-only ACL behavior that Windows ignores, which can surprise dual-boot or shared-media users. Debug support can be expensive when enabled at runtime.

## Test Signals

Build matrix coverage should include built-in, module, debug, and ACL combinations. Mount/read/write tests should run with `NTFS_FS=m/y`; ACL-specific xattr/permission tests apply only when ACL support is enabled.
