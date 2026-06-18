# sources/cloud-native/nydus-snapshotter/pkg/converter/merge_unix_test.go

Purpose: tests the digest-list reconciliation logic used when building final nydus manifest layer lists after merging bootstraps.

Important APIs and functions: helper `d` creates synthetic SHA256 digests; `TestMergeManifestBlobDigests` table-tests `mergeManifestBlobDigests`.

Control flow: each case passes `nydusBlobDigests` in OCI layer order and `originalBlobDigests` from nydus-image merge output. Expected results preserve all original nydus layer digests, including metadata-only layers missing from builder output, and append chunk-dict-only blobs not already in the layer list.

State and persistence: pure unit test.

Dependencies and integration points: validates a subtle part of `MergeLayers`/`convertManifest` where manifest layers must preserve OCI order while including extra dictionary blobs.

Risks and gaps: does not test full `MergeLayers` descriptor construction, backend sizing, fs version metadata, encryption annotations, or actual nydus-image merge output parsing.

Test signals: specifically guards reverse conversion correctness for metadata-only layers and chunk-dict images.
