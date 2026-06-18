# sources/cloud-native/buildkit/util/compression/gzip.go

## Purpose
gzip implementation of compression.Type for layer blobs. It compresses with containerd gzip writer and uses common decompression logic.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, gzipWriter`.

## Control Flow, State, And Persistence
NeedsConversion checks Force and media type/compression detection; NeedsComputeDiffBySelf is true when level/force require recompute; MediaType returns OCI gzip layer type.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are level handling and media-type mismatch. Covered indirectly by converter/exporter integration.
