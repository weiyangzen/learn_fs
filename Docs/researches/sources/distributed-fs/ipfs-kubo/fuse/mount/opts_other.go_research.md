<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_other.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/opts_other.go

## Purpose

This file provides the Linux/FreeBSD implementation of platform mount option adjustment.

## Important APIs, Types, and Functions

`PlatformMountOpts` is a no-op for `fuse.MountOptions`.

## Control Flow, State, and Integration

It is called by `NewMount`, preserving a common call site while avoiding Darwin-only options on other platforms.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse types only. The main risk is missing future platform-specific options for Linux/FreeBSD. Existing FUSE tests implicitly confirm the no-op does not break mount setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_other.go -->
