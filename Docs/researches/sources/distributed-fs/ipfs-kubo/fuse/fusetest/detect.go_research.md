<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/detect.go -->
# sources/distributed-fs/ipfs-kubo/fuse/fusetest/detect.go

## Purpose

This file centralizes platform and environment detection for FUSE tests on supported go-fuse platforms. It lets tests skip cleanly when FUSE is unavailable while still allowing CI to force failures when FUSE is expected.

## Important APIs, Types, and Functions

`fuseFlagFromEnv` reads `TEST_FUSE`, with legacy `TEST_NO_FUSE=1` treated as `TEST_FUSE=0`. `fuseAvailable` verifies `runtime.GOOS`, then checks `fusermount` or `fusermount3` on Linux and `umount` on Darwin/FreeBSD.

## Control Flow, State, and Integration

There is no persisted state. The helper calls `t.Skip` with targeted messages for unsupported OSes and missing mount helpers. It is consumed by `SkipUnlessFUSE` in `fusetest.go` and therefore gates all shared FUSE integration tests.

## Dependencies, Risks, and Test Signals

Dependencies are `os/exec`, `runtime`, and Go's testing package. The main risk is false positives: helper binaries may exist while kernel permissions, `/dev/fuse`, or macFUSE setup still prevent mounting. That risk is handled later by `MountError`, which skips or fails based on `TEST_FUSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/detect.go -->
