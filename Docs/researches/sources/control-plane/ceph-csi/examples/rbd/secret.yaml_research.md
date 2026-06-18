## sources/control-plane/ceph-csi/examples/rbd/secret.yaml

Purpose: Example Kubernetes Secret carrying Ceph credentials and an encryption passphrase for RBD CSI.

Important API surface: `v1/Secret` named `csi-rbd-secret` in `default`, `stringData.userID`, `stringData.userKey`, and `stringData.encryptionPassphrase`.

Control flow and state: CSI sidecars reference this secret from StorageClass and SnapshotClass parameters for provisioning, staging, publishing, expansion, modification, and snapshotting. Kubernetes stores secret data base64-encoded in etcd; the driver uses it to authenticate to Ceph and optionally unlock encryption.

Dependencies and risks: Placeholder credentials must be replaced and must not include `client.` prefix in `userID`. Example plaintext passphrase is unsuitable for production. RBAC should limit secret access. Test by provisioning a PVC and verifying authentication succeeds.
