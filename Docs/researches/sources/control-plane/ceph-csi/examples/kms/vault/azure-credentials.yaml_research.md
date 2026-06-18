# sources/control-plane/ceph-csi/examples/kms/vault/azure-credentials.yaml

Purpose: example Secret for Azure Key Vault client certificate material.

Important fields and flow: Secret `ceph-csi-azure-credentials` contains base64 `CLIENT_CERT` under `data`.

State, dependencies, and integration: referenced by Azure KMS provider config entries.

Risks and test signals: empty certificate is a placeholder. Correct certificate, client ID, tenant ID, and vault URL are required for encrypted volume key operations.
