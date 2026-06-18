# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/secret.yaml

Purpose: optionally renders a Kubernetes Secret for RBD Ceph credentials and encryption passphrase.

Important APIs/types/functions: gated by `.Values.secret.create`; writes `stringData.userID`, `userKey`, and `encryptionPassphrase`; supports annotations and common labels.

Control flow: StorageClass and SnapshotClass secret reference parameters point driver sidecars/nodeplugin to this Secret when defaults are used.

State and persistence behavior: credentials persist in Kubernetes Secret storage; Kubernetes encodes but does not inherently protect values without cluster secret encryption/RBAC controls.

Dependencies and integration points: Ceph auth users, StorageClass secret fields, KMS/encryption flows, and provisioner/nodeplugin RBAC.

Risks: placeholder plaintext values must be replaced. Enabling chart-managed credentials can leak secrets via values files or release history.

Test signals: provisioning, staging, snapshotting, and encryption tests fail quickly with bad credentials.
