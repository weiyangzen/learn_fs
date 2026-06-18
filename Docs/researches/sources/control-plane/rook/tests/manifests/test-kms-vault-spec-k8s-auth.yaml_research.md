<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-k8s-auth.yaml -->
# sources/control-plane/rook/tests/manifests/test-kms-vault-spec-k8s-auth.yaml

Purpose: Vault KMS cluster spec fragment using Kubernetes authentication. It is used with the Vault deployment/validation script to test Rook-managed encryption and key rotation.

Important structure: under `spec.security.kms.connectionDetails`, it sets Vault provider, in-cluster HTTPS address, backend path `rook/ver1`, `kv` engine, TLS file Secret names, `VAULT_SKIP_VERIFY`, auth method `kubernetes`, and role `rook-ceph`. `keyRotation` is enabled on a one-minute cron schedule.

State, persistence, and integration: when merged into a `CephCluster`, Rook OSDs authenticate to Vault with Kubernetes service accounts and store encryption keys under the configured backend. Dependencies include Vault TLS/client Secrets, the role set up by `deploy-validate-vault.sh`, and Rook service accounts. Risks include skip-verify in tests, frequent key rotation, and role/SA name coupling. Test signals are Vault secret count matching OSD PVC count and key material changing during rotation validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-k8s-auth.yaml -->
