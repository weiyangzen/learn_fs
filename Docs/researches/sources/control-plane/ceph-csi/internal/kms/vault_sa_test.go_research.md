# sources/control-plane/ceph-csi/internal/kms/vault_sa_test.go

## Purpose
`vault_sa_test.go` verifies static registration and configuration parsing for the Vault tenant ServiceAccount provider.

## Important APIs, Types, And Functions
`TestVaultTenantSAKMSRegistered` checks the provider registry. `TestTenantSAParseConfig` exercises `vaultTenantSA.parseConfig()` and related tenant-specific options.

## Control Flow And Test Behavior
The tests instantiate provider structs directly and validate configured fields and Vault auth settings after parsing sample maps.

## Dependencies And Integration Points
The tests depend on shared Vault config helper behavior and provider registration from `vault_sa.go`.

## Risks And Edge Cases
They do not mock Kubernetes ServiceAccounts or tokens and do not establish Vault connections. Temp token file handling and RBAC failures remain untested.

## Test Signals
The tests cover static wiring and selected option parsing. Authentication and external service behavior remain integration-test concerns.
