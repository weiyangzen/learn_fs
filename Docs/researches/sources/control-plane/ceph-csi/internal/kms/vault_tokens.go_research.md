# sources/control-plane/ceph-csi/internal/kms/vault_tokens.go

## Purpose
`vault_tokens.go` implements the `vaulttokens` provider, a tenant-aware Vault KMS where each tenant supplies a Vault token through a Kubernetes Secret. It also converts legacy Vault environment-style config into Ceph-CSI JSON config.

## Important APIs, Types, And Functions
`standardVault` models legacy `VAULT_*` keys. `vaultTokenConf` models Ceph-CSI config keys and `convertStdVaultToCSIConfig()`. `transformConfig()` converts legacy maps. `vaultTenantConnection` holds common tenant config, while `vaultTokensKMS` adds `TokenName`. Main methods are `initVaultTokensKMS`, `FetchDEK`, `StoreDEK`, `RemoveDEK`, `configureTenant`, `init`, `parseConfig`, `setTokenName`, `initCertificates`, `getToken`, `getCertificate`, `isTenantConfigOption`, `parseTenantConfig`, `setTenantAuthNamespace`, and `fetchTenantConfig`.

## Control Flow And State
Initialization optionally transforms legacy ConfigMap format, initializes Vault connection config, applies defaults, parses global config, applies nested tenant and tenant ConfigMap overrides, fetches the tenant token from a Secret, initializes certificates from tenant or CSI namespace fallback, and connects to Vault. Tenant ConfigMaps are filtered to allow only selected Vault connection options. Fetch/store/remove delegate to libopenstorage secrets using the tenant key context.

## State And Persistence Behavior
Vault tokens are read from Kubernetes Secrets and stored in memory as `api.EnvVaultToken`. CA and client certificate material can be written to temp files and later removed through inherited `Destroy()`. Passphrases are persisted in Vault as nested `data.passphrase` objects.

## Dependencies And Integration Points
The file depends on HashiCorp Vault API env keys, libopenstorage secrets, Kubernetes ConfigMap/Secret helpers, temporary file helpers, and base Vault connection code. `vault_sa.go` reuses the tenant connection and config filtering pattern.

## Risks And Edge Cases
`fetchTenantConfig()` only accepts `map[string]map[string]any`, which may not match maps produced by generic JSON unmarshal without additional conversion. Tenant ConfigMap unsupported options are silently ignored. Certificate fallback uses pod namespace from environment. Token retrieval requires the `token` key. Multiple parse layers mutate the same config maps, so precedence must be tested carefully.

## Test Signals
`vault_tokens_test.go` covers config parsing, provider initialization failure paths, legacy transform behavior, default transform values, registration, and tenant auth namespace override logic. It does not connect to Vault, fetch real Kubernetes Secrets/ConfigMaps, or exercise certificate temp file cleanup.
