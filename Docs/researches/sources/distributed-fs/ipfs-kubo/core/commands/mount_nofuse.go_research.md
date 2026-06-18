# sources/distributed-fs/ipfs-kubo/core/commands/mount_nofuse.go

## Purpose

`mount_nofuse.go` provides the non-Windows, non-FUSE build stub for `ipfs mount`. It keeps the command visible while clearly explaining that the binary was compiled without usable FUSE support.

## Important APIs, Types, and Functions

The file defines only `MountCmd`, a `cmds.Command` with `Experimental` status and help text. Its build tag is `!windows && (nofuse || !(linux || darwin || freebsd))`, complementing the real Unix implementation and the Windows stub.

## Control Flow

There is no `Run` function. Invoking the command in this build mode surfaces help/status rather than attempting mount setup. The user-facing behavior is documentation-driven: use a Kubo binary compiled with FUSE support and see the project repository/FUSE docs.

## State and Persistence Behavior

No state is read or written. The command does not inspect repo config, online status, or mount points.

## Dependencies and Integration Points

The only runtime dependency is `go-ipfs-cmds`. Integration is compile-time: the build tags ensure exactly one `MountCmd` definition is selected among Unix FUSE, no-FUSE, and Windows variants.

## Risks and Test Signals

The key risk is build-tag drift causing duplicate or missing `MountCmd` definitions for a platform. Build matrix tests should cover Linux/Darwin/FreeBSD with and without `nofuse`, unsupported Unix-like platforms, and Windows. UX tests can assert the stub help text mentions missing FUSE support and does not imply a mount operation occurred.
