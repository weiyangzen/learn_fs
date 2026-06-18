# sources/cloud-native/buildkit/util/compression/compression.go

## Purpose
Core compression abstraction for layer blobs. It defines Type, Config, compressor/decompressor/finalizer contracts, media-type conversion maps, and compression detection.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compressor, Decompressor, Finalizer, Type, Config, New, SetForce, SetLevel, Default, parse, fromMediaType, IsMediaType, ...`.

## Control Flow, State, And Persistence
DetectLayerMediaType reads blob headers and estargz footer; convertLayerMediaType maps Docker/OCI layer media types; decompress opens content.ReaderAt and delegates to estargz or containerd decompression while closing both readers.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/pkg/archive/compression, github.com/containerd/stargz-snapshotter/estargz, github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/iohelper, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are unsupported media types, estargz detection cost, and warning/fallback for unmapped media types. Coverage is mostly integration-level.
