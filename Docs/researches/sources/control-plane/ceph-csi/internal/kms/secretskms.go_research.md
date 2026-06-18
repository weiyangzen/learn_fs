# sources/control-plane/ceph-csi/internal/kms/secretskms.go

## Purpose
`secretskms.go` implements the default Kubernetes-secret KMS and the `metadata` KMS that encrypts per-volume DEKs with a passphrase-derived key and stores encrypted DEKs in volume metadata.

## Important APIs, Types, And Functions
`secretsKMS` embeds `integratedDEK` and stores one passphrase from StorageClass secrets. `secretsMetadataKMS` stores `ProviderInitArgs` and implements metadata DEK encryption. `encryptedMetadataDEK` is JSON with encrypted DEK bytes and nonce. `newSecretsKMS`, `initSecretsMetadataKMS`, `FetchDEK`, `EncryptDEK`, `DecryptDEK`, `GetSecret`, `fetchEncryptionPassphrase`, `generateKeyFromPassphrase`, and `generateNonce` are the main functions.

## Control Flow And State
The default provider requires `encryptionPassphrase` in supplied secrets and returns that same passphrase for any key. The metadata provider first tries to fetch a user-provided Kubernetes Secret from configured name/namespace, falling back to StorageClass secrets when that config is missing. Encryption derives a 32-byte scrypt key from passphrase and volume ID, encrypts with `symmetricEncrypt`, and JSON-serializes the result. Decryption reverses the process with the same passphrase and volume ID.

## State And Persistence Behavior
`secretsKMS` stores no per-volume DEKs and performs no external writes. `secretsMetadataKMS` requires the caller to store encrypted DEK JSON in metadata. Passphrases are held in memory and may be fetched from tenant or StorageClass Kubernetes Secrets.

## Dependencies And Integration Points
This file uses Kubernetes Secret helpers, scrypt, random nonce generation, JSON, and symmetric helpers from `kmip.go`. It registers both the default and metadata providers with `kms.go`.

## Risks And Edge Cases
The passphrase and volume ID must be stable; changing either makes metadata DEKs undecryptable. Empty passphrases and salts are accepted by scrypt. User-provided Secret lookup depends on tenant namespace defaults. `StoreDEK` and `RemoveDEK` are no-ops for both providers, so callers must understand whether metadata storage is required.

## Test Signals
`secretskms_test.go` covers default passphrase requirement, nonce length, scrypt determinism and key length, metadata initialization, an encrypt/decrypt workflow, and registration. It does not cover Kubernetes user Secret fetching with mocked API failures, corrupted encrypted JSON, wrong volume IDs, or random nonce uniqueness statistically.
