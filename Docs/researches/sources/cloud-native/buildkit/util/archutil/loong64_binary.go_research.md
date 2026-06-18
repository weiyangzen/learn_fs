# sources/cloud-native/buildkit/util/archutil/loong64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/loong64. The Binaryloong64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!loong64`. Key declarations observed in the file: `Binaryloong64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !loong64 prevents compiling the probe constant on native loong64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.
