<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull_test.go -->
# sources/cloud-native/cri-o/server/image_pull_test.go

## Purpose

This suite tests core `PullImage` success and failure paths.

## Important APIs, Types, and Functions

It calls `sut.PullImage`, uses mocked `CandidatesForPotentiallyShortImageName`, `PullImage`, and `ImageStatusByName`, and uses parsed storage references and IDs.

## Control Flow

The success test resolves a short image name, pulls a repo digest, looks that digest up in storage, and expects the response image ref to be the storage image ID. Failure tests cover invalid base64 auth, storage pull errors, and candidate resolution errors for empty image input.

## State and Persistence Behavior

No real images are pulled. The in-memory pull deduplication map is exercised but not asserted directly.

## Dependencies and Integration Points

The tests depend on gomock image server expectations, CRI image/auth types, and internal storage reference parsers.

## Risks and Edge Cases

They do not cover duplicate concurrent pulls, credential-provider auth files, progress timeout, artifact resolution, or separate pull cgroups.

## Test Signals

The tests confirm that CRI `PullImageResponse.ImageRef` returns the resolved image ID, not merely the pulled named reference.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull_test.go -->
