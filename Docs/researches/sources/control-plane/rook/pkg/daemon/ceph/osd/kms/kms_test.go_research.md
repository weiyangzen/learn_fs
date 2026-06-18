# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms_test.go

## Purpose
`kms_test.go` validates the generic KMS configuration gate in `kms.go`. It uses fake Kubernetes clients and mutable `KeyManagementServiceSpec` objects to prove that provider-specific mandatory fields, token secrets, TLS secrets, and environment injection behave as expected before any OSD encryption workflow attempts to talk to a KMS.

## Important APIs, Types, and Functions
The main test is `TestValidateConnectionDetails()`, organized as sequential subtests over one fake namespace. It creates token/TLS `Secret` objects for Vault, IBM Key Protect, and KMIP and then calls `ValidateConnectionDetails()`. `TestSetTokenToEnvVar()` calls `SetTokenToEnvVar()` for Vault and asserts `VAULT_TOKEN` is populated from a Kubernetes Secret key named `token`.

## Control Flow
The validation test starts with an empty `ConnectionDetails` map and verifies the missing `KMS_PROVIDER` error. It then mutates shared specs across subtests: KMIP fails before CA and endpoint are present, succeeds after secret data and endpoint are added, Vault fails for absent token Secret, empty token data, missing `VAULT_ADDR`, and missing/empty TLS Secret data, then succeeds once the TLS Secret contains `cert`. IBM fails without token auth, then fails with missing service API key, then missing instance ID, and finally succeeds after both fields are available. Azure validation walks through missing vault URL, tenant ID, client ID, certificate secret name, and success.

## State and Persistence
All persistent state is fake Kubernetes state in the test client. The tests intentionally mutate `kms.ConnectionDetails`, token Secret `Data`, and provider specs over time, so later subtests depend on earlier setup. `TestSetTokenToEnvVar()` mutates process environment and explicitly unsets `VAULT_TOKEN` afterward.

## Dependencies and Integration Points
The test depends on Rook's Kubernetes fake client helper, `cephv1.KeyManagementServiceSpec`, corev1 Secret types, `libopenstorage/secrets` provider constants, and Azure key names. It indirectly covers Vault validation in `vault.go` and mandatory detail constants from IBM, KMIP, and Azure KMS implementations.

## Risks
The subtests are order-dependent because they reuse and mutate the same spec and fake client state. Running subtests in parallel would be unsafe. Assertions focus on exact error strings, which is good for user-facing diagnostics but brittle during error wrapping changes. The test does not cover unsupported provider behavior after `NewConfig()`, backend put/get/delete dispatch, or concurrency effects from process-wide environment variables.

## Test Signals
The strongest signals are exact failures for missing token keys, TLS key names, provider fields, and Azure mandatory fields. The environment test confirms Vault token propagation. Useful additional signals would mock `secrets.Secrets` backends for idempotent `putSecret()` and unsupported-provider paths.
