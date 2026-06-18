<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/stat_test.go

## Purpose

This test file pins the stat helper behavior used by all FUSE mounts.

## Important APIs, Types, and Functions

`TestDefaultBlksizeAnchor` asserts `DefaultBlksize` remains 1 MiB. `TestBlksizeFromChunker` covers default and custom size chunkers, variable chunkers, malformed inputs, zero sizes, and values above `fuse.MAX_KERNEL_WRITE`.

## Control Flow, State, and Integration

The tests are table-driven and have no persistent state. They protect values that affect FUSE-visible stat output and IO buffer sizing.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse's max kernel write constant. Failures indicate a user-visible stat contract change or parser regression that would ripple into `/ipfs`, `/mfs`, and `/ipns`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat_test.go -->
