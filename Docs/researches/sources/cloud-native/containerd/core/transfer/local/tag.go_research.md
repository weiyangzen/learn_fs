# sources/cloud-native/containerd/core/transfer/local/tag.go

## Purpose
This file implements a local image-to-image-store transfer used for tagging or copying image references.

## Important APIs, Types, and Functions
`localTransferService.tag` accepts an `ImageGetter` source and `ImageStorer` destination.

## Control Flow
The method ensures a lease, retrieves the source image from `ts.images`, then stores the same target descriptor through the destination image storer.

## State and Persistence
It reads an existing image record and creates or updates destination image records. The content itself is not copied.

## Dependencies and Integration Points
Uses transfer getter/storer interfaces and local lease handling. Typically the destination is `transfer/image.Store`.

## Risks
The destination controls the final name and labels; this method does not validate content availability beyond the existing source image target.

## Test Signals
Indirectly covered by client image/tag workflows outside this file.
