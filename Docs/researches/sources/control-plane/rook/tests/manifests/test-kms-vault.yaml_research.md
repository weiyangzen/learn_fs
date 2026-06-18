<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault.yaml -->
# sources/control-plane/rook/tests/manifests/test-kms-vault.yaml

Purpose: Secret manifest template for Vault token authentication tests. The deployment script replaces the placeholder with a base64-encoded Vault token.

Important structure: defines `v1/Secret` named `rook-vault-token` in namespace `rook-ceph` with `data.token: ROOK_TOKEN`.

State, persistence, and integration: creates a Kubernetes Secret consumed by `tokenSecretName: rook-vault-token` in token-auth KMS fragments. Dependencies include `deploy-validate-vault.sh` performing placeholder substitution after creating a Vault policy token. Risks include placeholder misuse, token exposure, and stale file mutation in the working tree. Test signals are Rook successfully authenticating to Vault and creating/rotating encryption keys.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault.yaml -->
