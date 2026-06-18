# sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata.go

## Purpose
`aws_sts_metadata.go` registers the `aws-sts-metadata` provider, which assumes an AWS IAM role via web identity before using AWS KMS to wrap DEKs stored in volume metadata.

## Important APIs, Types, And Functions
`awsSTSMetadataKMS` embeds `awsMetadataKMS` and adds a role ARN. `initAWSSTSMetadataKMS()` reads tenant-scoped Kubernetes Secret data for role ARN, CMK ARN, and region. `EncryptDEK()` and `DecryptDEK()` use a KMS client from `getServiceWithSTS()`. `getWebIdentityToken()` reads the OIDC token file. `getSecrets()` validates supported STS secret keys.

## Control Flow And State
Initialization sets the namespace to the tenant, resolves the secret name, fetches required Secret values, and stores role, CMK, and region. Per operation, `getServiceWithSTS()` reads the mounted OIDC token, calls STS `AssumeRoleWithWebIdentity`, converts temporary credentials into an AWS SDK v1 static credential set, and builds an AWS KMS client.

## State And Persistence Behavior
Encrypted DEKs are returned for metadata storage. Temporary STS credentials are not cached; they are requested per encrypt/decrypt operation. `Destroy()` behavior is inherited as no-op.

## Dependencies And Integration Points
This provider mixes AWS SDK v2 for STS with AWS SDK v1 for KMS. It depends on Kubernetes Secret access and the fixed token file `/run/secrets/tokens/oidc-token`.

## Risks And Edge Cases
Per-operation STS calls can be expensive and sensitive to token file availability. The code dereferences STS credential fields without nil checks. Unknown Kubernetes Secret keys are rejected. The error text for unsupported options references the AWS metadata provider name, not the STS provider name.

## Test Signals
`aws_sts_metadata_test.go` only validates provider registration. There is no coverage for token file errors, STS failures, secret parsing, temporary credential nil values, or AWS KMS behavior.
