# sources/cloud-native/buildkit/util/archutil/amd64_check.go

## Purpose
Non-native linux/amd64 support probe wrapper. It calls check with the embedded Binaryamd64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!amd64`. Key declarations observed in the file: `amd64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, amd64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.
