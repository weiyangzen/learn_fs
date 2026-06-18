# sources/control-plane/ceph-csi/internal/kms/secretskms_test.go

## Purpose
`secretskms_test.go` provides the most substantive KMS unit coverage in this subset, focused on default secrets KMS and metadata encryption helpers.

## Important APIs, Types, And Functions
Tests include `TestNewSecretsKMS`, `TestGenerateNonce`, `TestGenerateKeyFromPassphrase`, `TestInitSecretsMetadataKMS`, `TestWorkflowSecretsMetadataKMS`, and `TestSecretsMetadataKMSRegistered`.

## Control Flow And Test Behavior
The tests validate missing and present StorageClass passphrases, generated nonce length, deterministic scrypt output for varied inputs, metadata provider initialization, and a complete metadata KMS encrypt/decrypt workflow using in-memory secrets.

## Dependencies And Integration Points
The tests use `testify/require` and package-private helpers. They avoid Kubernetes API calls by using StorageClass secrets fallback rather than configured user Secret retrieval.

## Risks And Edge Cases
The workflow tests do not verify wrong volume ID or wrong passphrase failure. Empty passphrase and salt are explicitly accepted by the key derivation test, documenting current behavior. Random nonce uniqueness is not tested.

## Test Signals
The file gives meaningful confidence in local crypto helper wiring and metadata provider happy path. External Kubernetes Secret retrieval and malformed ciphertext handling remain uncovered.
