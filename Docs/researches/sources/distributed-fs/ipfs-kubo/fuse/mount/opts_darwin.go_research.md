<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_darwin.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/opts_darwin.go

## Purpose

This Darwin-specific file adjusts macFUSE mount options to improve Finder presentation and avoid Apple metadata side effects.

## Important APIs, Types, and Functions

`PlatformMountOpts` appends `volname=<FsName>` when available, plus `noapplexattr` and `noappledouble`.

## Control Flow, State, and Integration

The function mutates `fuse.MountOptions` before `fs.Mount`. It is called by `NewMount` for every Kubo FUSE mount on macOS.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse mount options. The risk is macFUSE option drift or disabling useful Finder metadata unexpectedly. The intended signal is reduced ENOATTR chatter and avoidance of `._` sidecar files; platform-specific manual and integration testing are most relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_darwin.go -->
