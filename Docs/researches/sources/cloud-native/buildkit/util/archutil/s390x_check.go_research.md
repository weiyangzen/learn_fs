# sources/cloud-native/buildkit/util/archutil/s390x_check.go

## Purpose
Non-native linux/s390x support probe wrapper. It calls check with the embedded Binarys390x probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!s390x`. Key declarations observed in the file: `s390xSupported`.

## Control Flow, State, And Persistence
Control flow is one function, s390xSupported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.
