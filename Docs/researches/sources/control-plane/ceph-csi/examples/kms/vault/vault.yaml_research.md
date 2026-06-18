# sources/control-plane/ceph-csi/examples/kms/vault/vault.yaml

Purpose: complete in-cluster HashiCorp Vault dev deployment for Ceph-CSI KMS e2e testing.

Important fields and flow: creates headless Service `vault`, Deployment `vault` with a dev Vault server and monitor sidecar, ConfigMap `init-scripts` containing `init-vault.sh`, and Job `vault-init-job`. The init script waits for Vault, logs in with `VAULT_DEV_ROOT_TOKEN_ID`, enables Kubernetes auth under the cluster identifier, writes token reviewer config, writes a policy for `secret/data/ceph-csi/*` and metadata, creates a role bound to Ceph-CSI service accounts, and disables issuer validation.

State, dependencies, and integration: creates Kubernetes service/deployment/config/job resources and mutates Vault auth, policy, and secret engine configuration. It integrates with token-review RBAC and KMS configs that point to `http://vault.default.svc.cluster.local:8200`.

Risks and test signals: dev Vault, root token, old fixed image version, disabled issuer validation, and default namespace assumptions make this non-production. Job success and encrypted volume passphrase operations are the primary signals.
