# sources/control-plane/ceph-csi/internal/kms/vault.go

## Purpose
`vault.go` implements the base HashiCorp Vault KMS provider using Kubernetes service account authentication and stores passphrases directly in Vault.

## Important APIs, Types, And Functions
`vaultConnection` stores the libopenstorage secrets client, Vault config map, key context, and destroy-key behavior. `vaultKMS` embeds `vaultConnection` and `integratedDEK`, adding `vaultPassphrasePath`. Helpers include `setConfigString`, `setConfigBoolean`, `initConnection`, `initCertificates`, `connectVault`, `getDeleteKeyContext`, and `detectAuthMountPath`. Provider methods include `initVaultKMS`, `FetchDEK`, `StoreDEK`, and `RemoveDEK`.

## Control Flow And State
`initConnection()` validates and merges Vault address, backend, backend path, destroy behavior, TLS server name, namespaces, CA verification, and key context. `initCertificates()` writes a CA certificate from supplied secrets into a temporary file and adds its path to Vault config. `initVaultKMS()` configures Kubernetes auth mount path, role, passphrase root/path, service-account token path, connects to Vault, and returns the provider.

## State And Persistence Behavior
DEKs/passphrases are stored as Vault secrets with shape `data.passphrase`, often under a configured passphrase path. Temporary certificate files are removed by `Destroy()`. Delete context can request hard destroy for KV-v2-style secrets.

## Dependencies And Integration Points
The file depends on HashiCorp Vault API constants, libopenstorage secrets/vault integration, temporary file helpers, and the shared KMS provider registry. Tenant-aware Vault variants reuse `vaultConnection`.

## Risks And Edge Cases
Connection config is a mutable map reused across parse layers, so partial updates can persist. Temp certificate files must be cleaned by `Destroy()`. `setConfigBoolean()` expects string booleans, not native JSON booleans. The provider assumes Vault secret payloads use nested `data.passphrase`; incompatible backends fail at read time.

## Test Signals
`vault_test.go` covers selected config parsing and auth mount path behavior. It does not connect to Vault, validate certificate temp file cleanup, exercise Fetch/Store/Remove, or test all configuration merge paths.
