# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault.go

## Purpose
`vault.go` contains Rook's Vault-specific KMS bootstrap and validation logic. It converts CephCluster Vault connection details into the shape expected by `libopenstorage/secrets/vault`, handles TLS material stored in Kubernetes Secrets, validates user configuration, and builds Vault namespace key context for secret operations.

## Important APIs, Types, and Functions
The key public functions are `InitVault()`, `buildVaultKeyContext()`, and `validateVaultConnectionDetails()`. `InitVault()` copies the input config, calls `configTLS()`, converts the resulting map to `map[string]interface{}`, and returns a `secrets.Secrets` Vault implementation. `configTLS()` rewrites TLS connection values from Kubernetes Secret names to temporary certificate/key file paths. `getRemoveCertFilesFunc()` returns cleanup logic for those files. `tlsSecretKeyToCheck()` maps Vault TLS env names to expected Kubernetes Secret keys. `Config.IsVault()` identifies the provider.

## Control Flow
`configTLS()` loops over `cephv1.VaultTLSConnectionDetails`. If a configured TLS value is already under `/etc/vault`, it is treated as a mounted path and left unchanged. Otherwise it fetches the named Kubernetes Secret, creates a temporary file, writes the configured key's bytes with mode `0400`, replaces the config value with the file name, and tracks the file for deferred cleanup. A deferred closure always constructs a cleanup function; on error it immediately removes already-created files and returns nil cleanup to callers. `InitVault()` defers the cleanup after constructing the Vault secret store.

## State and Persistence
TLS files are temporary filesystem state. They exist only long enough for the Vault library to read them, then are closed and removed. The input config is copied before modification so repeated initialization does not permanently replace Secret names with temp paths. Vault namespace state is passed as `secrets.KeyVaultNamespace` in key context only when `VAULT_NAMESPACE` is configured.

## Dependencies and Integration Points
This file integrates with Kubernetes Secrets, Vault API env constants, `libopenstorage/secrets/vault`, and the generic `kms.go` dispatcher. It also supplies validation used by `ValidateConnectionDetails()`, and file paths/constants used by `volumes.go` when mounting Vault secrets into pods.

## Risks
TLS validation checks only existence and non-empty secret data, not certificate validity or key pairing. `configTLS()` uses temporary files outside the pod-mounted `/etc/vault` path when running daemon-side code, so host/container filesystem permissions and cleanup are important. Secret key mapping is asymmetric: `VAULT_CACERT` and `VAULT_CLIENT_CERT` both expect `cert`, while `VAULT_CLIENT_KEY` expects `key`. Any change to Vault TLS connection detail lists must keep this mapping aligned with volume projection logic.

## Test Signals
`vault_test.go` covers TLS key mapping, no-TLS config, already-mounted `/etc/vault` paths, missing Secret errors, successful CA/client cert/client key temp-file generation and cleanup, cleanup on temp file creation failure, and namespace key-context behavior. There is no live Vault integration here; actual auth and secret-store construction depend on provider integration tests.
