
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_status_test.go

## Purpose

This test file validates CRI image status conversion and image user parsing in the image service package.

## Important APIs, Types, and Functions

Tests are `TestImageStatus` and `TestGetUserFromImage`. They use `newTestCRIService`, `imagestore.NewFakeStore`, `(*CRIImageService).ImageStatus`, `(*GRPCCRIImageService).ImageStatus`, and `getUserFromImage`.

## Control Flow

`TestImageStatus` first queries a missing image ID and expects an empty successful response. It then installs a fake image with tag and digest references, size, chain ID, and config user, calls image status through the gRPC wrapper, and compares the expected CRI image. `TestGetUserFromImage` is table-driven over numeric and named users with optional group components.

## State and Persistence Behavior

All state is held in a fake in-memory image store. There are no containerd metadata, content, or snapshot operations.

## Dependencies and Integration Points

Dependencies include CRI runtime API, image-spec, CRI image store, and assertion libraries. The tests protect code used by both image status and image list responses.

## Risks and Edge Cases

Verbose image info is not tested. Pinned status and empty references are not covered. The missing image path only validates local store miss behavior, not containerd store reconciliation.

## Test Signals

Passing tests confirm CRI-compatible missing image semantics and correct conversion of ID, repo tag, repo digest, size, and username/UID fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status_test.go -->
