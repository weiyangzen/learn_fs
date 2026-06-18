
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_list_test.go

## Purpose

This test file validates CRI `ListImages` conversion from internal image-store entries to CRI runtime image records.

## Important APIs, Types, and Functions

The file defines `TestListImages`. It uses `newTestCRIService`, `imagestore.NewFakeStore`, `(*GRPCCRIImageService).ListImages`, and `toCRIImage` indirectly.

## Control Flow

The test builds three fake images with tag and digest references, sizes, and image config users. It installs them into the service's fake image store, calls `ListImages`, checks the returned count, and asserts that all expected CRI image objects are present.

## State and Persistence Behavior

All state is in memory in the fake image store. No containerd metadata or snapshots are consulted.

## Dependencies and Integration Points

Dependencies include image-spec types, CRI runtime API, the CRI image store package, and test assertion libraries. The test protects the list handler and shared image conversion logic.

## Risks and Edge Cases

The test does not assert response ordering, filter behavior, pinned images, empty references, or stale snapshot/content handling. It assumes `ParseImageReferences` splits the provided references into expected tag and digest arrays.

## Test Signals

Passing tests prove that image ID, repo tags, repo digests, size, numeric UID, and username fields are represented correctly in list responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_list_test.go -->
