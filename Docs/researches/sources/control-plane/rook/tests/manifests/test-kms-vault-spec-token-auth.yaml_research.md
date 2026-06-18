<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-token-auth.yaml -->
# sources/control-plane/rook/tests/manifests/test-kms-vault-spec-token-auth.yaml

Purpose: Vault KMS cluster spec fragment using token authentication. It drives tests where Rook reads a Vault token from a Kubernetes Secret.

Important structure: configures Vault provider, HTTPS address, backend path `rook/ver1`, `kv` engine, TLS client/cert Secret names, `VAULT_AUTH_METHOD: token`, `tokenSecretName: rook-vault-token`, and one-minute key rotation.

State, persistence, and integration: cluster reconciliation mounts/reads the Vault token Secret and uses the configured backend for encryption keys. Dependencies include the generated `rook-vault-token` Secret and Vault TLS Secrets from the deployment script. Risks include token leakage, skip-verify test setting, and fragment-only validity. Test signals are successful OSD key creation and rotation through Vault token auth.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-token-auth.yaml -->
