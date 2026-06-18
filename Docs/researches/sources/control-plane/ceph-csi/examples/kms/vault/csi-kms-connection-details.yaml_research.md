# sources/control-plane/ceph-csi/examples/kms/vault/csi-kms-connection-details.yaml

Purpose: alternative ConfigMap format for Ceph-CSI encryption KMS provider definitions when the mounted `ceph-csi-encryption-kms-config` file is absent.

Important fields and flow: ConfigMap `csi-kms-connection-details` stores one JSON blob per KMS ID key. Entries cover Vault Kubernetes auth, Vault token tenants, Vault tenant service accounts, metadata secrets, AWS metadata, IBM Key Protect, AWS STS metadata, KMIP, and Azure Key Vault. StorageClasses reference these keys through `encryptionKMSID`.

State, dependencies, and integration: read by Ceph-CSI RBD/CephFS encryption code to choose and configure passphrase storage. It integrates with companion Secrets and tenant objects in the same directory.

Risks and test signals: many values are placeholders or point at in-cluster dev Vault. Incorrect provider key names break StorageClass references. Successful encrypted volume lifecycle and key deletion checks validate the selected entry.
