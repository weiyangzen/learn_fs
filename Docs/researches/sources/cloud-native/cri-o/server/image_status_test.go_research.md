<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status_test.go -->
# sources/cloud-native/cri-o/server/image_status_test.go

## Purpose

This suite tests storage-backed CRI image status behavior.

## Important APIs, Types, and Functions

It calls `sut.ImageStatus`, mocks image server resolution/status methods, and uses parsed storage references and IDs.

## Control Flow

Tests verify normal short-name status, verbose status with OCI image config JSON, full image ID status, unknown image returning an empty successful response, status retrieval errors, short-name resolution errors, and missing image validation.

## State and Persistence Behavior

All storage interactions are mocked. No real image state is changed.

## Dependencies and Integration Points

The suite depends on gomock, containers/image no-such-image errors, OpenContainers image spec, CRI image status requests, and internal storage parsing helpers.

## Risks and Edge Cases

Artifact fallback, image user parsing variations, and hex-like resolver suppression are not covered.

## Test Signals

The tests confirm CRI-compatible not-found behavior: unknown images return a successful response without an image instead of an error.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status_test.go -->
