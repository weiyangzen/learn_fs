# sources/control-plane/ceph-csi/internal/kms/vault_tokens_test.go

## Purpose
`vault_tokens_test.go` validates tenant-token Vault configuration conversion, parsing, registration, and namespace override semantics.

## Important APIs, Types, And Functions
Tests include `TestParseConfig`, `TestInitVaultTokensKMS`, `TestStdVaultToCSIConfig`, `TestTransformConfig`, `TestTransformConfigDefaults`, `TestVaultTokensKMSRegistered`, and `TestSetTenantAuthNamespace`.

## Control Flow And Test Behavior
The tests construct in-memory Vault config maps and structs, call conversion/parsing helpers, and assert resulting fields. Initialization tests focus on expected errors without live external services.

## Dependencies And Integration Points
The file exercises shared `vaultConnection` parsing, tenant connection config, legacy environment-key conversion, and provider registry state.

## Risks And Edge Cases
The tests do not establish Vault connections or mock Kubernetes token/certificate retrieval. Map type assumptions for nested tenants and ConfigMap data are only partially covered.

## Test Signals
The suite gives good confidence in config transformations and default handling. Runtime behavior around tokens, certificates, Vault reads/writes, and delete semantics remains uncovered here.
