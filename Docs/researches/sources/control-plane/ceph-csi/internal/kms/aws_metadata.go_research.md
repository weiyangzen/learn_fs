# sources/control-plane/ceph-csi/internal/kms/aws_metadata.go

## Purpose
`aws_metadata.go` registers the `aws-metadata` KMS provider, which uses AWS KMS to wrap per-volume DEKs and stores the encrypted DEK in volume metadata rather than in AWS.

## Important APIs, Types, And Functions
`awsMetadataKMS` stores Kubernetes secret lookup settings and AWS region, access key, secret key, optional session token, and CMK ARN. `initAWSMetadataKMS()` parses config and Kubernetes Secret data. `EncryptDEK()` calls AWS KMS `Encrypt` and base64-encodes the ciphertext. `DecryptDEK()` base64-decodes and calls AWS KMS `Decrypt`. `RequiresDEKStore()` returns `DEKStoreMetadata`. `getSecrets()` and `getService()` fetch credentials and build an AWS SDK client.

## Control Flow And State
Initialization reads an optional secret name from config, requires AWS region, fetches a Kubernetes Secret in the Ceph-CSI pod namespace, validates supported secret keys, and stores credential fields in memory. Each encrypt/decrypt operation creates a fresh AWS session and KMS client.

## State And Persistence Behavior
The provider does not persist DEKs in AWS; it expects the caller to store the returned encrypted blob in metadata. AWS credentials and CMK are held in process memory. `Destroy()` has no cleanup.

## Dependencies And Integration Points
The provider uses AWS SDK v1 session/credentials/KMS APIs and `internal/util/k8s.GetSecret`. It is selected by `GetKMS()` through provider registration in `kms.go`.

## Risks And Edge Cases
Creating a new session for each operation can add latency. `DecryptDEK()` does not specify a key ID, relying on ciphertext metadata. The secret parser rejects unknown keys, which is strict but can break shared Kubernetes Secrets. The code accepts an optional session token but does not refresh credentials.

## Test Signals
`aws_metadata_test.go` only asserts provider registration. There is no unit coverage for config parsing, Kubernetes Secret handling, AWS client construction, encryption/decryption, strict unknown-key rejection, or invalid base64.
