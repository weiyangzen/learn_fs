# sources/control-plane/ceph-csi/internal/kms/aws_metadata_test.go

## Purpose
`aws_metadata_test.go` is a provider registration smoke test for the AWS metadata KMS backend.

## Important APIs, Types, And Functions
`TestAWSMetadataKMSRegistered` checks that `kmsManager.providers` contains `kmsTypeAWSMetadata`.

## Control Flow And Test Behavior
The test runs in parallel and uses `require.True` on the registry lookup result. Registration happens through the package-level `RegisterProvider` call in `aws_metadata.go`.

## Dependencies And Integration Points
The test depends on global package initialization order and the shared provider registry.

## Risks And Edge Cases
It does not instantiate the provider or mock Kubernetes/AWS dependencies. A provider can be registered but still fail all runtime configuration or encryption paths.

## Test Signals
The only signal is that static registration is wired. Runtime behavior needs separate tests around secrets, config, base64, and AWS API errors.
