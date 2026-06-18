# sources/cloud-native/containerd/core/transfer/archive/importer.go

## Purpose
This file implements an image archive import endpoint backed by a tar reader and serializable over transfer streams.

## Important APIs, Types, and Functions
`ImageImportStream` implements `transfer.ImageImporter` and `transfer.ImageImportStreamer`. `WithForceCompression` requests import compression. `Import` imports an archive index into a content store. `MarshalAny` sends the reader over a stream; `UnmarshalAny` receives it.

## Control Flow
`Import` optionally decompresses the input when media type is empty, applies compression import options, and calls `archive.ImportIndex`. For proxying, `MarshalAny` creates a stream and starts `SendStream`; `UnmarshalAny` resolves the stream and exposes `ReceiveStream` as the input reader.

## State and Persistence
Persistent effects are blobs and an import index written into the content store. Runtime state includes stream reader, media type, and compression flag.

## Dependencies and Integration Points
Uses image archive import, transfer streaming, compression detection, `typeurl`, and transfer protobuf registration from the paired exporter file.

## Risks
Compression handling depends on empty media type; callers providing an incorrect non-empty type can bypass decompression. Stream send errors are logged inside the streaming layer and not always returned synchronously to `MarshalAny`.

## Test Signals
Import behavior is exercised through local transfer import paths and streaming tests indirectly.
