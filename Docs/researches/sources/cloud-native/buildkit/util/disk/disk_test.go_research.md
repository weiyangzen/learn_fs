# sources/cloud-native/buildkit/util/disk/disk_test.go

## Purpose
Smoke test for platform disk statistics. It calls GetDiskStat("/") and asserts total is positive and free/available are non-negative.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `none`. Key declarations observed in the file: `TestGetDiskStat`.

## Control Flow, State, And Persistence
Control flow is a single platform-dependent call. It does not validate exact filesystem accounting.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signal is basic syscall/API availability on the test platform.
