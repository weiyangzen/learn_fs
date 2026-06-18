<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/mount_unix.go

## Purpose

This file mounts the `/ipns` FUSE filesystem and wraps unmount so local MFS roots are closed and published. It is the daemon-facing entry point for the IPNS mount.

## Important APIs, Types, and Functions

`mutableCacheTime` is one second for entry and attr caching. `Mount` builds CoreAPI, reads repo config, derives MFS root options from import config, gets the self key, calls `CreateRoot`, fills `fs.Options`, and calls `fusemnt.NewMount`. `ipnsMount` embeds `mount.Mount` and overrides `Unmount` to close the `Root`.

## Control Flow, State, and Integration

Mount creation configures current UID/GID, optional `AllowOther`, `FsName=ipns`, `MaxReadAhead`, `IPFS_FUSE_DEBUG`, and `WritableMountCapabilities`. On mount failure after root creation, it closes the root to avoid losing in-memory state. On unmount, root close is attempted even if the low-level unmount returns an error.

## Dependencies, Risks, and Test Signals

Dependencies include coreapi, config, go-fuse, `fuse/mount`, and the IPNS root implementation. Risks include failing to close roots, incorrect cache duration for mutable names, and misconfigured `AllowOther`. Tests mount with the same options, verify persistence, and exercise external unmount via node-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/mount_unix.go -->
