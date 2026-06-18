<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mode.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/mode.go

## Purpose

This file defines shared POSIX modes, FUSE read-ahead size, and CID xattr names used across readonly and writable FUSE filesystems.

## Important APIs, Types, and Functions

Constants include writable defaults `DefaultFileModeRW=0644`, `DefaultDirModeRW=0755`, readonly defaults `DefaultFileModeRO=0444`, `DefaultDirModeRO=0555`, execute-only `NamespaceRootMode=0111`, `SymlinkMode=0777`, `MaxReadAhead=64 MiB`, `XattrCID="ipfs.cid"`, and deprecated `XattrCIDDeprecated="ipfs_cid"`.

## Control Flow, State, and Integration

There is no control flow. The constants are used in attr filling, mount options, xattr handlers, and tests. They form a user-visible filesystem contract.

## Dependencies, Risks, and Test Signals

Dependency is `os.FileMode`. Risks include silently changing permissions, causing `ls`, `find`, or traversal behavior regressions, or breaking tools using old xattr names. FUSE tests check namespace mode, default file/dir modes, symlink mode, and xattr behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mode.go -->
