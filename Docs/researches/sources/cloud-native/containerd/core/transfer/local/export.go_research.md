# sources/cloud-native/containerd/core/transfer/local/export.go

## Purpose
This file implements local transfer from an image getter or lookup source to an image archive/exporter destination.

## Important APIs, Types, and Functions
`localTransferService.exportStream` accepts `transfer.ImageGetter`, `transfer.ImageExporter`, and transfer options.

## Control Flow
The method ensures a lease exists, emits progress start, obtains one or more images through `ImageLookup` or `Get`, calls `Export` with the service content store, then emits completion progress.

## State and Persistence
The method reads image records from `ts.images` and content blobs from `ts.content`; it writes exported bytes through the destination. A temporary lease protects resources during export when no lease is already present.

## Dependencies and Integration Points
Integrates transfer interfaces, local service lease handling, content store, and image store. Archive exporter is a common destination.

## Risks
If `ImageLookup` returns multiple images, destination export must handle the full set. Lease deletion is deferred, so destination errors still trigger cleanup.

## Test Signals
Covered through higher-level transfer/export integration; no file-local unit test.
