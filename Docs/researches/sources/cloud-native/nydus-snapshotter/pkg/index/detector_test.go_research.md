# Research: sources/cloud-native/nydus-snapshotter/pkg/index/detector_test.go

This file tests local index-selection logic without registry IO. `TestHasNydusFeatures` verifies nil platform, no OS features, one Nydus feature, multiple features, and unrelated features. `TestFindNydusManifestInIndex` builds synthetic OCI indexes and checks original-manifest absence, no alternative, successful same-platform Nydus alternative, multiple alternatives returning the first match, different architecture ignored, artifact-type match, and wrong artifact type ignored.

These tests give confidence that index alternatives are selected by matching the original descriptor's platform and either `nydus.remoteimage.v1` OS feature or Nydus artifact type. They also lock in first-match behavior when multiple alternatives exist.

Coverage gaps include nil platform fields on descriptors, variant/OSVersion matching details, malformed JSON, max-size truncation, remote fetch errors, metadata-layer validation in the fetched manifest, and `fetchMetadata` unpack cleanup. No persistent files are written; all state is in memory. The tests are valuable because filesystem index detection depends on this function to avoid mounting an ordinary OCI layer when a Nydus alternative is advertised.
