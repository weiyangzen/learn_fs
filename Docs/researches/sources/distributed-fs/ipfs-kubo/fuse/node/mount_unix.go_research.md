<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_unix.go

## Purpose

`mount_unix.go` orchestrates mounting and unmounting all supported Kubo FUSE filesystems: read-only `/ipfs`, writable `/ipns`, and writable `/mfs`.

## Important APIs, Types, and Functions

`platformFuseChecks` is overridable by OS-specific files. `Mount` first unmounts live mounts, runs platform checks, then calls `doMount`. `Unmount` best-effort unmounts active entries in `node.Mounts`. `doMount` mounts `/ipfs`, `/ipns` when the node is online, and `/mfs` concurrently, normalizes common fusermount errors, rolls back partial success, and stores mount handles on the node.

## Control Flow, State, and Integration

Mounts are attempted in parallel using `sync.WaitGroup`. If any mount fails, successful mounts are immediately unmounted and the first relevant error is returned. Node state is updated only after all required mounts succeed. Offline nodes skip `/ipns`.

## Dependencies, Risks, and Test Signals

Dependencies are Kubo core, `fuse/readonly`, `fuse/ipns`, `fuse/mfs`, and `fuse/mount`. Risks include partial mount cleanup failures, concurrent mount ordering, brittle fusermount error strings, and nil `Ipns` mount for offline nodes. Node tests verify external unmount state, and CLI FUSE tests exercise daemon integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_unix.go -->
