<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/doc.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/doc.go

## Purpose

This package doc identifies `fuse/readonly` as the FUSE filesystem for accessing files stored in IPFS.

## Important APIs, Types, and Functions

The file contains only the package declaration and doc comment. The implementation lives in `readonly_unix.go` and mount setup in `mount_unix.go`.

## Control Flow, State, and Integration

There is no executable flow or state.

## Dependencies, Risks, and Test Signals

The risk is documentation drift if the package grows beyond read-only `/ipfs`. Package-level docs are indirectly checked by Go doc generation and normal package builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/doc.go -->
