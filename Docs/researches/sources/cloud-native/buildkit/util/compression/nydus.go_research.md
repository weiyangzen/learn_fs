# sources/cloud-native/buildkit/util/compression/nydus.go

## Purpose
Nydus compression.Type extension. It registers the nydus type, recognizes Nydus media types, and enforces OCI-only support.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `nydus`. Key declarations observed in the file: `nydusType, Nydus, init, Parse, FromMediaType, Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, ...`.

## Control Flow, State, And Persistence
Parse/FromMediaType are extended in init-time wrappers. Compress returns unsupported because conversion requires external Nydus tooling; Decompress handles nydus labels/media where supported.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/pkg/labels, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors, github.com/containerd/nydus-snapshotter/pkg/converter`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are global parse wrapper behavior and unsupported compression attempts. Integration-level coverage only.
