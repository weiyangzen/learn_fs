
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_list.go

## Purpose

This file implements CRI `ListImages` for the gRPC image service wrapper. It exposes images known to the CRI in-memory image store as CRI runtime image records.

## Important APIs, Types, and Functions

The only function is `(*GRPCCRIImageService).ListImages`. It calls `c.imageStore.List` and converts each `imagestore.Image` using `toCRIImage`.

## Control Flow

The handler ignores request filters, retrieves all images from the in-memory store, appends converted CRI images to a slice, and returns a `runtime.ListImagesResponse`.

## State and Persistence Behavior

The function is read-only. It does not verify containerd content or snapshot existence at list time and does not refresh the image store.

## Dependencies and Integration Points

Dependencies include context and CRI runtime API. It integrates with `image_status.go` for conversion logic and with `imagestore.Store`, which is refreshed by pulls, startup checks, and image events.

## Risks and Edge Cases

The handler may report stale images if content or snapshots are removed outside CRI after the in-memory store was updated. CRI list filters are not implemented. Image order follows store order and is not explicitly sorted.

## Test Signals

`image_list_test.go` verifies conversion of IDs, repo tags, repo digests, size, numeric UID, and username values for multiple fake images.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list.go -->
