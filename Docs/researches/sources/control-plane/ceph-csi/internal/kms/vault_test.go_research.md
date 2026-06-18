# sources/control-plane/ceph-csi/internal/kms/vault_test.go

## Purpose
`vault_test.go` validates selected helper behavior for the base Vault KMS provider.

## Important APIs, Types, And Functions
The tests cover configuration helpers such as `setConfigString`, `setConfigBoolean`, `initConnection`, and `detectAuthMountPath`, plus provider registration for `vault`.

## Control Flow And Test Behavior
The tests build in-memory config maps, call package-private helpers, and assert resulting values or errors. They avoid live Vault and Kubernetes dependencies.

## Dependencies And Integration Points
The file depends on Vault config constants and the package global registry. It exercises shared helpers used by base Vault and tenant-aware providers.

## Risks And Edge Cases
Because it avoids Vault connections, it cannot catch backend payload shape, auth, or network failures. It also does not prove temporary certificate files are cleaned up.

## Test Signals
The tests provide useful coverage for option parsing and auth mount path derivation. Fetch/store/remove and live provider initialization remain outside this subset.
