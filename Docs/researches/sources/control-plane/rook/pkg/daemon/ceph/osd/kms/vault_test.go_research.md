# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_test.go

## Purpose
`vault_test.go` verifies the Vault-specific TLS and namespace helpers. Its focus is not live Vault behavior; it locks down how Rook maps Vault TLS env options to Kubernetes Secret keys, rewrites Secret names into temporary files, cleans those files, and builds Vault namespace key context.

## Important APIs, Types, and Functions
`Test_tlsSecretKeyToCheck()` covers the mapping from Vault TLS option names to Kubernetes Secret keys. `Test_configTLS()` is the largest test and drives `configTLS()` through no-op, mounted-path, missing-secret, successful temp-file, advanced CA/client cert/client key, and temp-file failure scenarios. `Test_buildVaultKeyContext()` checks whether `VAULT_NAMESPACE` produces a one-entry key context.

## Control Flow
The TLS test sets debug logging, creates a fake Kubernetes client, and repeatedly calls `configTLS()` with different maps. For Kubernetes-secret TLS values, it creates Secret objects containing `cert` or `key` data and asserts resulting config values differ from the original Secret names and point to existing files. It then calls the returned cleanup function and checks those files are gone. The failure subtest replaces package-level `createTmpFile` and `getRemoveCertFiles` to simulate a temp-file creation failure and verify cleanup runs before returning.

## State and Persistence
The test uses fake Kubernetes Secret state and temporary files on disk. It mutates global package variables `createTmpFile` and `getRemoveCertFiles` in the failure scenario, and sets debug-related environment/log state. The cleanup assertions are important because real Vault initialization briefly writes sensitive TLS material to temp files.

## Dependencies and Integration Points
The test depends on Rook's fake Kubernetes client helper, corev1 Secrets, package-level test hooks from `vault.go`, HashiCorp Vault env option strings, and testify assertions. It also implicitly aligns with `volumes.go`, because both must agree that CA/client cert data is keyed by `cert` and client key data is keyed by `key`.

## Risks
The test's global hook replacement is not reset in a defer in the shown code path, so adding later subtests could inherit mocked functions if not careful. Secret objects are reused through one fake client namespace, making some subtests dependent on earlier created Secrets. It does not exercise malformed file writes except temp creation failure, nor does it validate actual certificate content.

## Test Signals
Strong signals include file existence after TLS conversion and no-file-exists after cleanup, preserving already-mounted `/etc/vault` paths, and returning nil cleanup on errors. Additional useful tests would reset global hooks explicitly and cover `os.WriteFile` failures.
