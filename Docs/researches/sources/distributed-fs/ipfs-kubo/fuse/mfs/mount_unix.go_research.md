<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mfs/mount_unix.go

## Purpose

This file provides the daemon-facing mount entry point for `/mfs`. It reads repo configuration, creates the MFS FUSE root, and mounts it with writable options.

## Important APIs, Types, and Functions

`mutableCacheTime` is one second. `Mount` reads `ipfs.Repo.Config`, calls `NewFileSystem`, prepares `fs.Options`, and delegates to `fusemnt.NewMount`.

## Control Flow, State, and Integration

The mount uses null permissions, current UID/GID, mutable entry/attr cache, optional `AllowOther`, `FsName=mfs`, `MaxReadAhead`, `IPFS_FUSE_DEBUG`, and `WritableMountCapabilities`. State persists through `ipfs.FilesRoot` and the repo.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse, config, Kubo core, and `fuse/mount`. Risks are incorrect mount options, missing atomic truncate capability, stale mutable cache behavior, and repo config read failures. MFS tests and node mount tests exercise this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mount_unix.go -->
