# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_api.go

## Purpose
`vault_api.go` provides a lower-level Vault API client path used to detect the KV backend version when the user configures Vault KV without explicitly providing `VAULT_BACKEND`. It complements `vault.go`, which initializes the generic libopenstorage Vault secrets implementation.

## Important APIs, Types, and Functions
`newVaultClient()` builds a HashiCorp `api.Client` from Rook KMS connection details. `BackendVersion()` returns `"v1"` or `"v2"` based on explicit config or Vault mount metadata. `trimSlash()` normalizes mount paths for comparison. The package-level `vaultClient` variable points to `newVaultClient` so tests can replace it.

## Control Flow
`newVaultClient()` starts from `api.DefaultConfig()`, copies the secret config to avoid mutation, applies `configTLS()` so TLS values become readable file paths, configures TLS through the libopenstorage Vault utility, creates the API client, sets the trimmed Vault address, optionally sets Vault Enterprise namespace, authenticates via token or Kubernetes auth, and sets the returned token on the client. Authentication errors are wrapped with a more specific Kubernetes-auth message when `VAULT_AUTH_METHOD` is Kubernetes. `BackendVersion()` first honors explicit backend values `kv`, `kv-v2`, `v1`, or `v2`. Otherwise it initializes a client, calls `Sys().ListMounts()`, finds the configured or default backend path, and maps mount option `version=2` to v2, defaulting matched mounts to v1.

## State and Persistence
This file does not persist secrets. It temporarily creates TLS files via `configTLS()` and removes them before returning from client initialization. It reads Vault system mount metadata and authentication state. It mutates only the local copied config and the created client's address, namespace, and token.

## Dependencies and Integration Points
Dependencies include HashiCorp Vault API, `libopenstorage/secrets/vault/utils`, the generic `GetParam()` helper, Vault backend constants, and the TLS configuration path in `vault.go`. `kms.go` calls `BackendVersion()` during validation for Vault KV engines when backend version is omitted.

## Risks
Backend auto-detection requires live Vault connectivity and list-mount permissions during Rook validation. Lack of permissions or unreachable Vault will reject the cluster KMS config even if normal secret operations might later work with explicit version. The package-level `vaultClient` mock hook is convenient but global. Address trimming removes only trailing newline suffixes through `strings.TrimSuffix(..., "\n")`; other whitespace is handled earlier only if values pass through `GetParam()`.

## Test Signals
No dedicated `vault_api_test.go` is in this work item. Coverage is indirect through `kms_test.go` for the path that may call `BackendVersion()` and through `vault_test.go` for TLS file conversion. Stronger signals would mock `vaultClient.Sys().ListMounts()` for explicit v1/v2, missing mount, namespace, and auth-error cases.
