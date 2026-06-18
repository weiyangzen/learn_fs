# sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test_inject.go

## Purpose
Test-only injection helpers for the OCI artifact datastore.

## APIs and Integration
`Store.SetImpl` replaces the datastore implementation interface with a mock. `ArtifactData.SetData` mutates raw data for tests. Both are compiled only with the `test` build tag and support `store_test.go` plus future datastore tests.

## Risks
The helpers bypass production encapsulation and should remain test-build-only.
