# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_test.go

Purpose: tests overlay layer parsing, upperdir selection, stat comparison, and file comparison helpers.

Important APIs and flow: `TestGetOverlayLayers` covers lower/upper ordering, lower-only mounts, known option skipping, and unknown option errors. `TestGetUpperdir` covers bind bottom layers, overlay-over-bind and overlay-over-overlay cases, unsupported mount types, multiple mount configs, layer mismatch, and too many upper layers. Additional tests validate `compareSysStat`, symlink/content comparison, and related helper outcomes.

State and persistence: mostly in-memory mount structs, plus temporary files for content comparison tests.

Dependencies and integration: validates the assumptions used before the committer packs diffs from containerd nydus snapshots.

Risks and test signals: strong branch coverage for parser logic. It does not perform real overlay mounts or full `Changes` traversal with kernel whiteout/opaque xattrs in all cases.
