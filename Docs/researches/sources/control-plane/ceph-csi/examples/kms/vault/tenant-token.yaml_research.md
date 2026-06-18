# sources/control-plane/ceph-csi/examples/kms/vault/tenant-token.yaml

Purpose: tenant Secret containing a Vault token for `vaulttokens` KMS mode.

Important fields and flow: Secret `ceph-csi-kms-token` stores `token: sample_root_token_id`.

State, dependencies, and integration: read by Ceph-CSI when the selected KMS config uses tenant token authentication.

Risks and test signals: sample root token is for dev/test only. The secret must exist in the tenant namespace and be scoped appropriately for production.
