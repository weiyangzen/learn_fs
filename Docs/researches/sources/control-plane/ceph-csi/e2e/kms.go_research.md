# sources/control-plane/ceph-csi/e2e/kms.go

Purpose: models KMS configurations used by encryption tests and provides validation hooks for reading and verifying deletion of encryption passphrases, especially in HashiCorp Vault.

Important APIs/types/functions: `kmsConfig` defines `canGetPassphrase()`, `getPassphrase()`, `canVerifyKeyDestroyed()`, and `verifyKeyDestroyed()`. `simpleKMS` is a provider-only implementation for KMS modes that cannot be inspected directly. `vaultConfig` embeds `simpleKMS`, adds `backendPath` and `destroyKeys`, and implements Vault CLI-based passphrase and deletion checks. Globals define `noKMS`, `secretsMetadataKMS`, `vaultKMS`, `vaultTokensKMS`, and `vaultTenantSAKMS`.

Control flow: simple KMS implementations return false/empty results. Vault `getPassphrase()` logs in to the in-cluster Vault service with the sample root token, then runs `vault kv get -field=data` for `backendPath+key` inside the Vault pod. `verifyKeyDestroyed()` reads Vault KV metadata `deletion_time`; non-empty stdout means the key metadata still exists and destruction failed, while empty stdout is treated as destroyed.

State and persistence: does not create KMS state itself, but reads state created by CSI encryption flows. Backend paths encode whether keys live under `secret/ceph-csi/`, `secret/`, or `tenant/`; `destroyKeys` expresses expected cleanup strength.

Dependencies and integration points: uses e2e pod exec helpers, `cephCSINamespace`, `metav1.ListOptions` selecting `app=vault`, and CephFS fscrypt validation helpers. It assumes Vault was deployed by `deploy-vault.go` and contains the sample token/config.

Risks: uses a hard-coded root token and Vault DNS name. CLI output parsing treats trimmed stdout/stderr as authoritative; Vault CLI or KV version changes can break expectations. `verifyKeyDestroyed()` assumes empty stdout means destruction even if stderr contains a transient Vault error, so callers must inspect returned message in context.

Test signals: encrypted volume tests can read passphrases while volumes exist, cannot read them after deletion, and for `destroyKeys` configs observe destroyed metadata rather than soft-deleted key records.
