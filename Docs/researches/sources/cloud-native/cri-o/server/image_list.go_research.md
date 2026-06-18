<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list.go -->
# sources/cloud-native/cri-o/server/image_list.go

## Purpose

This file implements CRI image listing and streaming, including normal container images and OCI artifacts exposed as CRI images.

## Important APIs, Types, and Functions

`ListImages`, `StreamImages`, and `listImages` provide unary and chunked stream APIs. `ConvertImage` converts internal `storage.ImageResult` to CRI `types.Image`.

## Control Flow

For an image filter with a non-empty image spec, `listImages` reuses `storageImageStatus` to return at most the matching storage image, then also attempts artifact status and appends the artifact CRI image if found. Without a filter, it lists all storage images, converts each, lists artifacts, logs artifact-list errors as warnings, and appends artifact images. Streaming chunks the list by `streamChunkSize`.

## State and Persistence Behavior

The file reads image and artifact stores only. It does not mutate storage.

## Dependencies and Integration Points

It integrates with storage image status/list APIs, artifact store status/list APIs, CRI image protobufs, shared image status helper, and stream chunking.

## Risks and Edge Cases

Filter semantics are lookup-like, not broad label/query filtering, because kubelet historically does not use filters. Artifact status errors other than not-found are logged in filtered mode but do not fail the whole request after a storage image match. `ConvertImage` falls back to `PreviousName@Digest` when repo digests are missing.

## Test Signals

Tests cover list success, filter success, list error, filter status error, and `ConvertImage` behavior for nil input, repo tags/digests, numeric user, and previous-name digest fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list.go -->
