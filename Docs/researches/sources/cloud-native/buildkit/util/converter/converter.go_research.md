# sources/cloud-native/buildkit/util/converter/converter.go

## Purpose
Layer conversion pipeline for recompressing blobs and optionally rewriting tar timestamps. It returns containerd converter functions only when conversion is needed.

## Important APIs, Types, And Functions
Package: `converter`. Build tags: `none`. Key declarations observed in the file: `New, NewWithRewriteTimestamp, conversion, bufioPool, rewriteTimestampInTarHeader, convert, onceWriteCloser, Close, labelRewrittenTimestamp`.

## Control Flow, State, And Persistence
NewWithRewriteTimestamp checks compression NeedsConversion and timestamp annotation, selects decompressor from current media type, streams decompressed data through optional tarconverter, computes diffID, compresses to a new content writer, commits labels, and applies compression finalizer annotations.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images/converter, github.com/containerd/containerd/v2/pkg/labels, github.com/containerd/errdefs, github.com/moby/buildkit/identity, github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/compression, github.com/moby/buildkit/util/converter/tarconverter, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are large streaming failures, immutable diffID bypass, media-type mismatches, and timestamp reproducibility. tarconverter tests cover tar padding for the timestamp rewrite reader.
