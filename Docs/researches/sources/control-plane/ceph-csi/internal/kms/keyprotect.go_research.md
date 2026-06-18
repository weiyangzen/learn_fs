# sources/control-plane/ceph-csi/internal/kms/keyprotect.go

## Purpose
`keyprotect.go` registers the IBM Key Protect metadata KMS provider, which wraps DEKs with a configured customer root key and expects encrypted DEKs to be stored in volume metadata.

## Important APIs, Types, And Functions
`keyProtectKMS` stores namespace, Kubernetes Secret name, IBM Key Protect client, API key, CRK, service instance ID, URLs, region, session token, and optional CRK ARN. `initKeyProtectKMS()` parses config and Secret data. `EncryptDEK()` calls `client.Wrap` with volume ID as additional authenticated data. `DecryptDEK()` calls `client.Unwrap`. `RequiresDEKStore()` returns metadata storage. `getService()` builds a Key Protect client.

## Control Flow And State
Initialization resolves defaults for secret name, base URL, and token URL, requires service instance ID and root key credentials, and permits optional session token, region, and CRK ARN. Encrypt/decrypt build or replace the client before each operation, then base64 encode or decode wrapped bytes.

## State And Persistence Behavior
DEKs are persisted outside this provider as encrypted metadata. The provider holds credentials in memory. `Destroy()` is a no-op.

## Dependencies And Integration Points
The file depends on `github.com/IBM/keyprotect-go-client` and Kubernetes Secret helpers. It integrates with the shared KMS registry and `DEKStoreMetadata` workflow.

## Risks And Edge Cases
Per-operation client creation adds overhead. Strict Secret key validation can reject shared Secrets. Optional fields such as region/session token/CRK ARN are parsed but not used in `getService()`. Because volume ID is authenticated data, decrypting with a different volume ID should fail.

## Test Signals
`keyprotect_test.go` only validates registration. There is no coverage for config defaults, Secret parsing, client construction, wrap/unwrap, base64 errors, or AAD mismatch behavior.
