# sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service_test.go

## Purpose
Tests filesystem-backed v2 distribution metadata mapping behavior.

## APIs, Control Flow, and Integration
`TestV2MetadataService` creates an `FSMetadataStore`, adds metadata entries for several DiffIDs including 100 entries for capping, verifies returned metadata equals the newest 50 where applicable, expects errors for nonexistent DiffID/digest lookups, then overwrites a digest mapping and confirms `GetDiffID` returns the latest DiffID.

## State, Dependencies, and Risks
State is temporary on-disk metadata. Tests cover the main persistence contract but not HMAC computation/checking, remove semantics, nil-store behavior, malformed JSON, or concurrent access. `randomDigest` uses pseudo-random bytes for test data.
