# sources/cloud-native/containerd/core/transfer/archive/exporter.go

## Purpose
This file implements an image archive export transfer endpoint backed by a tar writer and serializable over transfer streams.

## Important APIs, Types, and Functions
`ImageExportStream` implements `transfer.ImageExporter` and `transfer.ImageExportStreamer`. Options select platforms, all-platform export, Docker compatibility manifest skipping, and non-distributable blob skipping. `Export` calls `images/archive.Export`. `MarshalAny` and `UnmarshalAny` bridge local writers to remote stream IDs.

## Control Flow
`Export` builds archive options from configured images and platform policy, then writes an OCI/Docker archive to `iis.stream`. `MarshalAny` creates a stream ID, starts a goroutine copying bytes received from the remote stream into the local writer, and marshals the protobuf endpoint. `UnmarshalAny` retrieves the stream and wraps it with `WriteByteStream`.

## State and Persistence
Persistent effects are archive bytes written to the provided writer. The endpoint itself stores writer, media type, platform selectors, and export flags.

## Dependencies and Integration Points
Integrates `core/images/archive`, `core/transfer/plugins`, `core/transfer/streaming`, `core/streaming`, `typeurl`, and transfer protobuf types.

## Risks
The copy goroutine must close the local writer; errors are only logged. Platform defaults select `platforms.DefaultStrict` unless all-platform or explicit platforms are set, so callers must opt into multi-platform export.

## Test Signals
Covered indirectly by transfer import/export and stream roundtrip tests; no file-local unit test.
