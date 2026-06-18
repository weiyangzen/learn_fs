# sources/cloud-native/buildkit/util/compression/uncompressed.go

## Purpose
Uncompressed compression.Type implementation. It passes data through without compression and maps to OCI uncompressed layer media type.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String`.

## Control Flow, State, And Persistence
Compress returns a nop write closer, Decompress opens raw blob content, and NeedsConversion detects compressed input unless Force is false and type already matches.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/moby/buildkit/util/iohelper, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are media-type/diffID expectations and large raw layer streams. Integration-level coverage only.
