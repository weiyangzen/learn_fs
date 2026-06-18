# sources/cloud-native/containerd/core/transfer/local/import.go

## Purpose
This file implements local transfer from an image archive/importer into content, image store records, and optional snapshots.

## Important APIs, Types, and Functions
`localTransferService.importStream` calls `ImageImporter.Import`, walks the imported index, stores top-level and child image references, applies optional filters, and optionally creates an `unpack.Unpacker`. `mergeMap` combines descriptor annotations.

## Control Flow
After lease setup and progress emission, import writes blobs and returns an index descriptor. The handler saves the index and, for the top-level index, reads and annotates manifests with `io.containerd.import.ref-source=annotation` before walking children. If the destination supports unpack, matched unpack configs are converted to `unpack.WithUnpackPlatform`. The image graph is walked with `images.WalkNotEmpty`, unpack completion is awaited, and each collected descriptor is stored as images.

## State and Persistence
Persistent effects include content blobs, image records, and optional snapshots. The temporary lease protects imported content during processing. Descriptor annotations guide image-name persistence.

## Dependencies and Integration Points
Uses `content.ReadBlob`, `images.Children`, `images.WalkNotEmpty`, transfer filtering/storing/unpack interfaces, `unpack.NewUnpacker`, and local supported platform matching.

## Risks
Import assumes the top-level descriptor is an OCI index JSON. Unsupported unpack configs are silently skipped through matching. Errors during walk require waiting for unpacker cleanup. `ErrNotFound` from image storage is logged and ignored, allowing descriptors without names.

## Test Signals
Indirectly covered by transfer import/export tests and image store tests for annotation-derived names.
