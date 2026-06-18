<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/export_test.go -->
# sources/cloud-native/containerd/integration/client/export_test.go

## Purpose
Exercises image export behavior across full multi-platform exports, sparse exports with missing content, Docker manifest compatibility, OCI-only export, index-only export, and valid OCI `org.opencontainers.image.ref.name` annotations.

## APIs, Types, And Functions
`TestExportAllCases` is table-driven with prepare/check functions. Helpers include `isImageInArchive`, `getPlatformManifest`, `assertOCITar`, and `assertOCIIndexAnnotationRefName`. It uses `client.Fetch`, `client.Export`, `archive.WithImage`, `archive.WithManifest`, `archive.WithPlatform`, `archive.WithSkipMissing`, `archive.WithSkipDockerManifest`, `images.Walk`, `images.Children`, `images.LimitManifests`, and `content.Store`.

## Control Flow And State
Each case creates a unique namespace and client, prepares content by fetching one platform or full metadata, optionally deletes non-index blobs to simulate sparse content, exports to a temp file, seeks back, validates OCI tar members, and inspects whether selected descriptors' blobs are present. One case exports a digest reference and decodes `index.json` to validate annotation grammar.

## Persistence And Integration Points
The tests persist temporary tar archives and daemon content under per-test namespaces. They integrate with platform matchers, OCI archive layout, Docker `manifest.json` compatibility, content store deletion, and descriptor graph walking.

## Risks And Test Signals
Failures indicate broken missing-content handling, unexpected Docker manifest inclusion/exclusion, wrong platform filtering, incomplete descriptor closure in exported archives, or invalid ref-name annotations. Windows skips some all-platform cases because the test index does not carry the same platform breadth there.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/export_test.go -->
