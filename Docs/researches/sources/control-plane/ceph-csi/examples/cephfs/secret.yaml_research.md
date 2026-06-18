# sources/control-plane/ceph-csi/examples/cephfs/secret.yaml

Purpose: example Kubernetes Secret for CephFS CSI credentials and optional encryption passphrase.

Important fields and flow: Secret `csi-cephfs-secret` in `default` uses `stringData` for `userID`, `userKey`, and `encryptionPassphrase`.

State, dependencies, and integration: consumed by CephFS StorageClass and SnapshotClass secret references for provisioning, expansion, publish, and snapshots. E2E helpers load this and replace credentials.

Risks and test signals: placeholder credentials are not usable as-is, and plaintext examples must not be reused in production. Successful provisioning verifies the secret matches Ceph auth caps.
