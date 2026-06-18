# sources/cloud-native/buildkit/util/compression/zstd.go

## Purpose
Zstandard compression.Type implementation. It writes zstd-compressed OCI layers with optional compression levels.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, zstdWriter, toZstdEncoderLevel`.

## Control Flow, State, And Persistence
Compress returns a zstd encoder writer, Decompress uses common decompression, NeedsConversion checks force/type, and toZstdEncoderLevel maps integer levels into klauspost/compress levels.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/klauspost/compress/zstd, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are level mapping and OCI-only consumer support. Integration-level coverage only.
