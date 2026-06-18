# sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata_test.go

## Purpose
`aws_sts_metadata_test.go` confirms that the AWS STS metadata KMS provider is registered during package initialization.

## Important APIs, Types, And Functions
`TestAWSSTSMetadataKMSRegistered` looks up `kmsTypeAWSSTSMetadata` in `kmsManager.providers`.

## Control Flow And Test Behavior
The test is parallel and performs a single registry assertion.

## Dependencies And Integration Points
It depends on the provider registration side effect in `aws_sts_metadata.go`.

## Risks And Edge Cases
Registration does not prove the provider can read OIDC tokens, assume a role, parse tenant Secrets, or call AWS KMS.

## Test Signals
The file provides static wiring coverage only. Provider initialization and STS/KMS paths remain untested here.
