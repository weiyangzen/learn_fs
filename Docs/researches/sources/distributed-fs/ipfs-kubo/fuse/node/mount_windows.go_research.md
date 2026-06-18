<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_windows.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_windows.go

## Purpose

This Windows stub makes the node mount API compile while reporting that FUSE-style mounting is unsupported.

## Important APIs, Types, and Functions

`Mount` returns `errors.New("not implemented")`; `Unmount` is a no-op.

## Control Flow, State, and Integration

No state is mutated. It preserves API shape across platforms.

## Dependencies, Risks, and Test Signals

Dependency is just Kubo core type signatures. The risk is user-facing command paths needing clearer Windows guidance. Windows builds validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_windows.go -->
