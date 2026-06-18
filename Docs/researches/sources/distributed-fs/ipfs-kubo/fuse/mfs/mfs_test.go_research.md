<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_test.go

## Purpose

This file tests the `/mfs` FUSE mount by running the shared writable suite and MFS-specific persistence/stat assertions. It ensures the local mutable file store behaves correctly through FUSE.

## Important APIs, Types, and Functions

`testMount` mounts a root with mutable cache time, max readahead, and writable capabilities. `mfsMount` creates a node, maps `writable.Config` into `config.Mounts`, and returns a mounted `NewFileSystem`. `TestWritableSuite` runs the shared conformance tests. Other tests verify data persistence across remounts, stat block accounting with a configured chunker, symlink stat fields, and statfs reporting.

## Control Flow, State, and Integration

The tests write through FUSE into `ipfs.FilesRoot`, remount against the same node, and read state back. `TestStatBlocks` configures `Import.UnixFSChunker` to `size-65536`, writes multi-block and small files, and asserts POSIX stat fields.

## Dependencies, Risks, and Test Signals

Dependencies include Kubo core/node config, go-fuse, `fusetest`, `fuse/mount`, and `fuse/writable`. Risks covered include attr cache zeros after create, wrong block accounting, missing statfs on macOS, lost MFS state after unmount/remount, and symlink metadata errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_test.go -->
