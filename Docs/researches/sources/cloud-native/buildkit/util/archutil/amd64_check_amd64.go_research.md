# sources/cloud-native/buildkit/util/archutil/amd64_check_amd64.go

## Purpose
Native amd64 support detector. It returns the current AMD64 microarchitecture variant using github.com/tonistiigi/go-archvariant.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `amd64`. Key declarations observed in the file: `amd64Supported`.

## Control Flow, State, And Persistence
amd64Supported has no persistence and does not execute probe binaries on native amd64. detect.go expands the returned variant into v2/v3/v4 platform variants.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/tonistiigi/go-archvariant`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is variant detection dependency and consistency with OCI platform variant semantics. No local test.
