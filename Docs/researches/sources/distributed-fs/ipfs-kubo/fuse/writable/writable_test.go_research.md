<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/writable/writable_test.go

## Purpose

This file contains focused unit tests for writable FUSE helpers that do not require full kernel-level flows.

## Important APIs, Types, and Functions

`TestNewDirNormalizesBlksize` verifies zero block size falls back to `DefaultBlksize` and explicit values pass through. `TestSymlinkSetattrChmodNoError` verifies symlink chmod-like setattr requests succeed without storing permissions. `TestStatfsReportsSpace` verifies statfs proxies repo filesystem data and handles empty repo paths.

## Control Flow, State, and Integration

The tests instantiate `Config`, `Dir`, and `Symlink` directly, avoiding FUSE mounts except for go-fuse structs. They validate behavior that may not be forwarded by Linux VFS in normal integration tests.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse structs, merkledag DAG service stubs, and shared mount constants. Failures signal regressions in block-size defaults, symlink POSIX compatibility, or Finder-facing statfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable_test.go -->
