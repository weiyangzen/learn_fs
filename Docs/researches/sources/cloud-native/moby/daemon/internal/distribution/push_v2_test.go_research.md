# sources/cloud-native/moby/daemon/internal/distribution/push_v2_test.go

## Purpose
Tests v2 push layer metadata selection, existence checks, and auth-sensitive cleanup behavior.

## APIs, Control Flow, and Integration
`TestGetRepositoryMountCandidates` verifies same-registry filtering, target repo exclusion, Docker Hub normalization, HMAC preference, path-component likeness sorting, recency ordering, and max-candidate truncation. `TestLayerAlreadyExists` table-tests metadata filtering, remote stat order, unknown blob cleanup, access-denied tolerance, existing descriptor normalization, duplicate digest checks, and max attempts. `TestWhenEmptyAuthConfig` verifies `hasAuthInfo`. `TestPushRegistryWhenAuthInfoEmpty` ensures unauthorized mount create does not remove metadata when unauthenticated.

## State, Dependencies, and Risks
Tests use mock repos/blob stores/metadata services and progress sink. They exercise the trickiest metadata logic but do not perform real uploads, manifest pushes, compression, or endpoint fallback.
