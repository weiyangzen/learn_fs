# sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa-admin.yaml

Purpose: administrator example for preparing Vault access for a tenant service account.

Important fields and flow: ConfigMap `vault-tenant-sa-script` contains `add-tenant-sa.sh`, which logs into Vault, enables a tenant KV store, writes a tenant policy, and configures a Vault Kubernetes auth role bound to `ceph-csi-vault-sa` in namespace `tenant`. Job `vault-tenant-sa` runs that script using service account `rbd-csi-vault-token-review`.

State, dependencies, and integration: creates ConfigMap and Job in `default`, mutates Vault policy/auth/secret-engine state, and enables tenant KMS mode used with `tenant-sa.yaml`.

Risks and test signals: intended for examples/testing; it uses a root token and `vault:latest`, and assumes Vault is reachable at `vault.default.svc`. Successful job completion indicates tenant Vault role setup.
