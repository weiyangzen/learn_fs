<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/mount_unix.go

## Purpose

This file is the daemon-facing mount entry point for read-only `/ipfs`.

## Important APIs, Types, and Functions

`Mount` reads repo config, constructs `NewRoot`, fills `fs.Options` with current UID/GID, immutable attr/entry timeout, `AllowOther`, `FsName=ipfs`, `MaxReadAhead`, and `IPFS_FUSE_DEBUG`, then calls `fusemnt.NewMount`.

## Control Flow, State, and Integration

The function creates no content state; it exposes existing blockstore/DAG content through a FUSE root. Mount state is managed by the returned `fuse/mount.Mount`.

## Dependencies, Risks, and Test Signals

Dependencies are go-fuse, config, Kubo core, and `fuse/mount`. Risks include bad `AllowOther`, excessive immutable cache if mutable paths slip into `/ipfs`, and missing repo config. Readonly and node mount tests exercise the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/mount_unix.go -->
