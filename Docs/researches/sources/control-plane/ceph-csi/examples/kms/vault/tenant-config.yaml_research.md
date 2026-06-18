# sources/control-plane/ceph-csi/examples/kms/vault/tenant-config.yaml

Purpose: tenant-side ConfigMap for overriding Vault connection settings.

Important fields and flow: ConfigMap `ceph-csi-kms-config` contains `vaultAddress`, `vaultBackend`, `vaultBackendPath`, TLS server name, and CA verification flag.

State, dependencies, and integration: created in a tenant namespace for Vault token or tenant-service-account KMS modes, allowing per-tenant backend selection.

Risks and test signals: must live in the namespace expected by the KMS config and match tenant credentials. Successful encrypted PVC creation in that namespace validates it.
