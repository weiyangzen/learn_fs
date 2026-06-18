<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/deploy-validate-vault.sh -->
# sources/control-plane/rook/tests/scripts/deploy-validate-vault.sh

Purpose: integration helper for deploying a TLS-enabled Vault instance and validating Rook KMS behavior for OSD and RGW encryption, including key rotation.

Important APIs and control flow: startup installs `jq` and Helm on Linux. `deploy_vault` generates TLS files, creates Kubernetes TLS/client/CA Secrets, writes Helm values, installs Vault, initializes/unseals it, enables kv v1, kv v2, and transit engines, writes a Rook policy, and either configures Kubernetes auth or creates a token and patches `tests/manifests/test-kms-vault.yaml`. Validation paths inspect RGW pod Vault env/config, use curl with mounted TLS credentials to fetch KV or transit data keys, compare OSD PVC count to Vault secret count, and poll for rotated OSD key changes. The main case dispatches `deploy`, `validate_osd`, `validate_rgw`, or `validate_key_rotation`.

State, persistence, and integration: creates Vault Helm resources, multiple Kubernetes Secrets, Vault auth/policy/secret-engine state, and mutates a manifest token placeholder. Dependencies include Helm, kubectl, jq, OpenSSL/TLS generation script, Vault CLI in pod, Rook service accounts, and test manifests. Risks include plaintext token handling, in-place manifest mutation, broad Vault policy privileges, shell parsing of pod descriptions, and frequent key rotation timing. Test signals are Vault pod readiness, successful key fetch through RGW pod credentials, OSD secret count equality, and observed key rotation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/deploy-validate-vault.sh -->
