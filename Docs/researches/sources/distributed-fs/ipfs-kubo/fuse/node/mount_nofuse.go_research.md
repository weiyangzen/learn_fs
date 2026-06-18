<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_nofuse.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_nofuse.go

## Purpose

This build-tagged stub makes Kubo compile with `nofuse` on non-Windows platforms while returning a clear runtime error for mount requests.

## Important APIs, Types, and Functions

`Mount` returns `errors.New("not compiled in")`; `Unmount` is a no-op.

## Control Flow, State, and Integration

No state is created. This file replaces the real FUSE implementation under `!windows && nofuse`.

## Dependencies, Risks, and Test Signals

Dependencies are minimal. The risk is callers not surfacing the error clearly. Build-tag CI or manual `go build -tags nofuse` verifies this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_nofuse.go -->
