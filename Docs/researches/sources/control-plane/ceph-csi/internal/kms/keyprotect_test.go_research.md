# sources/control-plane/ceph-csi/internal/kms/keyprotect_test.go

## Purpose
`keyprotect_test.go` confirms registration of the IBM Key Protect metadata KMS provider.

## Important APIs, Types, And Functions
`TestKeyProtectMetadataKMSRegistered` checks the global registry for `kmsTypeKeyProtectMetadata`.

## Control Flow And Test Behavior
The test is parallel and performs a single provider map lookup.

## Dependencies And Integration Points
It relies on package initialization in `keyprotect.go`.

## Risks And Edge Cases
No IBM client, configuration, Secret, or encryption behavior is exercised.

## Test Signals
The test covers static wiring only. Runtime provider paths require additional mocks or integration tests.
