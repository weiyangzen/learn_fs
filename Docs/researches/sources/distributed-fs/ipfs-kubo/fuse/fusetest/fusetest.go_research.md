<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/fusetest.go -->
# sources/distributed-fs/ipfs-kubo/fuse/fusetest/fusetest.go

## Purpose

`fusetest.go` provides shared test utilities for mounting go-fuse filesystems and asserting POSIX stat behavior. It prevents each FUSE package from duplicating environment detection, mount cleanup, and stat assertions.

## Important APIs, Types, and Functions

`SkipUnlessFUSE` implements the `TEST_FUSE` decision order. `TestMount` creates a temp mountpoint, fills default `fs.Options` with null permissions and current UID/GID, calls `fs.Mount`, and registers unmount cleanup. `AssertStatfsNonZero` verifies real filesystem space data. `AssertStatBlocks` validates `st_blocks` and `st_blksize`. `MountError` fails when `TEST_FUSE=1` and otherwise skips on mount errors.

## Control Flow, State, and Integration

The file controls test-time lifecycle only: temp dirs are owned by `testing.T`, and mounted servers are unmounted in cleanup. It integrates with `/ipfs`, `/ipns`, `/mfs`, and writable suite tests.

## Dependencies, Risks, and Test Signals

Dependencies are `hanwen/go-fuse/v2/fs`, `syscall`, `os`, and `testify/require`. Risks include platform-specific `syscall.Stat_t` assumptions and cleanup relying on `server.Unmount`. Test signals are non-zero statfs values, correctly rounded 512-byte block counts, and fatal behavior when CI declares FUSE mandatory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/fusetest.go -->
