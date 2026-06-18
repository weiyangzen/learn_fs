# sources/cloud-native/buildkit/util/disk/disk_netbsd.go

## Purpose
netbsd disk statistics implementation. It calls the platform statfs/statvfs syscall and converts block counts into byte totals.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `netbsd`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow wraps syscall errors with the root path and fills DiskStat Total, Free, and Available using platform-specific block-size fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors, golang.org/x/sys/unix`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are OS-specific field semantics and integer overflow on unusual filesystems. disk_test.go is the smoke test on supported platforms.
