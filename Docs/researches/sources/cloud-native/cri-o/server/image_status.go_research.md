<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status.go -->
# sources/cloud-native/cri-o/server/image_status.go

## Purpose

This file implements CRI image status lookup for storage images and OCI artifacts, plus image user parsing and verbose image info.

## Important APIs, Types, and Functions

`ImageStatus(ctx, req)` validates image input, checks storage image status, falls back to artifact status, and builds `types.ImageStatusResponse`. `storageImageStatus(ctx, spec)` resolves an image by ID prefix or short-name candidates. `getUserFromImage`, `createImageInfo`, and `isHexString` support conversion and error handling.

## Control Flow

Image status rejects missing image specs. Storage lookup first tries heuristic ID-prefix resolution and calls `ImageStatusByID`. If that is not applicable, it resolves potential short-name candidates and tries `ImageStatusByName` until one succeeds, ignoring no-such-image and returning the last non-notfound error. If short-name resolution fails for a string that looks like a hex ID/digest of length at least 3, it returns not found instead of surfacing the resolver error. If storage status is nil, artifact status is attempted; found artifacts are returned as CRI images, not-found returns an empty response, and other errors are logged. Verbose storage responses include labels and OCI config JSON.

## State and Persistence Behavior

The file reads image and artifact stores only. It does not mutate storage.

## Dependencies and Integration Points

It depends on containers/image storage errors, containers/storage errors, internal storage image server APIs, artifact store APIs, goccy JSON, OpenContainers image spec, CRI image/status types, and shared storage reference parsing behavior.

## Risks and Edge Cases

Unknown images return an empty successful response, matching CRI expectations. Hex-looking resolver failures are suppressed to avoid confusing ID-prefix lookups. `getUserFromImage` ignores groups after `:` and treats numeric users as UID. Artifact errors after storage miss are logged but not returned except when found path succeeds.

## Test Signals

Tests cover normal status, verbose info JSON, full ID lookup, unknown image success, storage status error, short-name resolution error, and missing image validation. Artifact fallback and hex resolver suppression are not directly covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_status.go -->
