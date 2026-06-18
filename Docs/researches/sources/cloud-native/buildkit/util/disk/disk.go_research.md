# sources/cloud-native/buildkit/util/disk/disk.go

## Purpose
Shared disk statistics type. DiskStat holds Total, Free, and Available byte counts returned by platform-specific GetDiskStat implementations.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `none`. Key declarations observed in the file: `DiskStat`.

## Control Flow, State, And Persistence
No control flow. Platform files fill this struct from statfs/statvfs/GetDiskFreeSpaceEx equivalents.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is semantic differences between free and available across platforms. disk_test.go checks positive values on the running platform.
