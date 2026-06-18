# sources/control-plane/ceph-csi/examples/kms/vault/kms-config.yaml

Purpose: primary Ceph-CSI encryption KMS ConfigMap with `config.json` containing multiple provider definitions.

Important fields and flow: ConfigMap `ceph-csi-encryption-kms-config` maps KMS IDs to JSON objects for Vault, Vault tokens, Vault tenant service accounts, Vault namespaces, metadata secrets, IBM Key Protect, AWS STS, KMIP, and Azure. Entries include backend paths, tenant config/token/SA names, destroy-key flags, TLS verification, secret names, service IDs, and provider-specific endpoint fields.

State, dependencies, and integration: mounted/read by Ceph-CSI encryption code. StorageClasses reference keys such as `vault-test`, `vault-tokens-test`, `vault-tenant-sa-test`, or provider-specific IDs through `encryptionKMSID`.

Risks and test signals: JSON syntax and provider field names are critical; a bad entry can disable encryption setup. Many endpoints and IDs are examples. E2E encryption tests validate passphrase creation, retrieval, and deletion through these configs.
