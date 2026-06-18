# sources/cloud-native/containerd/core/images/archive/exporter.go

Purpose: OCI/Docker-compatible image archive exporter.

Important APIs/functions: export options include `WithPlatform`, `WithAllPlatforms`, `WithSkipDockerManifest`, `WithImage`, `WithImages`, `WithManifest`, `WithBlobFilter`, `WithSkipNonDistributableBlobs`, `WithReferrersProvider`, and `WithSkipMissing`. Core helpers include `addNameAnnotation`, `copySourceLabels`, `Export`, `getRecords`, `filterReferrers`, `blobRecord`, `ociLayoutFile`, `ociIndexRecord`, `manifestsRecord`, and `writeTar`.

Control flow and state: `Export` builds tar records beginning with `oci-layout`, copies distribution source labels into descriptors, walks manifest/index trees to collect blob records, handles platform selection and index resolution for Docker `manifest.json`, optionally includes referrers, writes `index.json`, optionally writes Docker-compatible `manifest.json`, creates blob directory records, sorts records by path, skips duplicate tar names, and verifies copy sizes/digests.

Dependencies and integration: content info/reader provider, image handlers/walkers, OCI/Docker media types, platforms matching, labels, errdefs, tar/json.

Risks: `WithSkipMissing` can export a manifest without descendants if a child is missing, which is intentional but subtle. Platform sorting assumes a non-nil platform comparer when multiple manifests are selected. Duplicate tar path suppression can hide descriptor duplication. Blob filtering returns empty records that must be filtered by `writeTar`.

Test signals: no direct file tests in this subset; archive integration tests should verify OCI layout, Docker manifest compatibility, missing blob semantics, referrers, non-distributable filtering, and digest validation.
