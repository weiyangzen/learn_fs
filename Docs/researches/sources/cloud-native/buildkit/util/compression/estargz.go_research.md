# sources/cloud-native/buildkit/util/compression/estargz.go

## Purpose
eStargz compression.Type implementation. It converts tar streams into seekable gzip layers and records TOC/uncompressed-size annotations.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `EStargzAnnotations, estargzLabel, Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, Is, decompressEStargz, compressionInfo, ...`.

## Control Flow, State, And Persistence
Compress wires an io.Pipe through estargz writer and blob-info calculation, finalize returns annotations, Is checks labels/footers, Decompress uses estargz reader. It maintains per-compression closure state under a mutex.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/pkg/archive/compression, github.com/containerd/containerd/v2/pkg/labels, github.com/containerd/stargz-snapshotter/estargz, github.com/moby/buildkit/util/iohelper, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are goroutine/pipe error propagation, annotation correctness, and content store reads. Integration tests elsewhere are the main signal.
