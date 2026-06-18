# sources/control-plane/ceph-csi/internal/kms/vault_sa.go

## Purpose
`vault_sa.go` implements the `vaulttenantsa` provider, a tenant-aware Vault KMS that authenticates to Vault using a ServiceAccount from the tenant namespace.

## Important APIs, Types, And Functions
`vaultTenantSA` embeds `vaultTenantConnection` and stores tenant ServiceAccount name plus temporary token directory. `initVaultTenantSA()` handles legacy config transformation, base Vault config, tenant overrides, ServiceAccount token path setup, certificate setup, and Vault connection. Methods include `Destroy`, `configureTenant`, `parseConfig`, `isTenantSAConfigOption`, `setServiceAccountName`, `getToken`, `getTokenPath`, and `createToken`.

## Control Flow And State
Initialization sets defaults for tenant config name, tenant ServiceAccount name, auth mount path, and Vault role. Tenant config can override allowed options globally, from nested tenant config, and from the tenant ConfigMap. `getToken()` first tries the Kubernetes TokenRequest API through `createToken()`, then falls back to legacy ServiceAccount referenced token Secrets. `getTokenPath()` writes the token to a temporary `0600` file and points Vault Kubernetes auth at it.

## State And Persistence Behavior
The provider creates a temporary token directory and removes it in `Destroy()`. Passphrases are stored in Vault through inherited `vaultTenantConnection` methods. Tenant-specific config is held in mutable Vault config/key-context maps.

## Dependencies And Integration Points
This provider uses Kubernetes ServiceAccount, Secret, and token APIs through Ceph-CSI helpers, libopenstorage Vault auth settings, and shared Vault tenant config parsing from `vault_tokens.go`.

## Risks And Edge Cases
Temporary token cleanup depends on `Destroy()`. TokenRequest failures fall back to legacy Secrets, but both paths require Kubernetes RBAC. Tenant ConfigMaps are filtered by `isTenantSAConfigOption`; unsupported keys are silently ignored. ServiceAccount tokens written to disk must remain protected by filesystem permissions and lifecycle.

## Test Signals
`vault_sa_test.go` checks provider registration and tenant SA config parsing. It does not exercise TokenRequest, legacy token Secret fallback, temp token path creation, Vault connection, or cleanup behavior.
