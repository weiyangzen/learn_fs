# sources/control-plane/ceph-csi/internal/kms/kmip_test.go

## Purpose
`kmip_test.go` is a smoke test for KMIP KMS provider registration.

## Important APIs, Types, And Functions
`TestKMIPKMSRegistered` checks that `kmsTypeKMIP` is registered in `kmsManager.providers`.

## Control Flow And Test Behavior
The test runs in parallel and performs a single registry assertion.

## Dependencies And Integration Points
It depends on the registration side effect in `kmip.go`.

## Risks And Edge Cases
Registration does not validate certificates, KMIP endpoint compatibility, crypto RPC behavior, local-key encryption, or TTLV handling.

## Test Signals
Static provider wiring is covered; all runtime KMIP behavior is outside this test.
