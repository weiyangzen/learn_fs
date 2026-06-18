# sources/cloud-native/buildkit/util/disk/disk_windows.go

## Purpose
Windows disk statistics implementation. It calls GetDiskFreeSpaceEx via x/sys/windows and returns total/free/available bytes.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `windows`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow converts the root path to UTF-16, invokes the Windows API, and maps available/free/total outputs to DiskStat.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors, golang.org/x/sys/windows`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are path formatting and Windows API semantics. disk_test.go is the smoke test.
