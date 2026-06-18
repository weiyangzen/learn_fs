# sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa.yaml

Purpose: tenant namespace resources for Vault tenant service-account KMS mode.

Important fields and flow: creates ServiceAccount `ceph-csi-vault-sa` and ConfigMap `ceph-csi-kms-config` with tenant Vault backend, path, and role values.

State, dependencies, and integration: tenant workloads use this service account/config so Ceph-CSI can authenticate to Vault as the tenant.

Risks and test signals: must be created in the tenant namespace and aligned with admin-created Vault role/policy. Encrypted volume provisioning validates the tenant-specific path.
