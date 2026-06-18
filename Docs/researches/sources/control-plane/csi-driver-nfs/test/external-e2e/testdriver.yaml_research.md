## sources/control-plane/csi-driver-nfs/test/external-e2e/testdriver.yaml

Purpose: configures Kubernetes external storage tests for the NFS CSI driver when run as `test.csi.k8s.io`. It points the external test suite at generated StorageClass and SnapshotClass inputs and declares supported driver capabilities.

Important content: `StorageClass.FromFile` uses `/tmp/csi/storageclass.yaml`, `SnapshotClass.FromName` expects an existing snapshot class, and `DriverInfo` advertises NFS fs type plus persistence, exec, multipods, RWX, fsGroup, PVC/snapshot data sources, controller expansion, and node expansion. `InlineVolumes` supplies server and share attributes for an inline NFS mount.

State is declarative; the external test binary reads it. Dependencies are the `/tmp/csi` files created by `run.sh`, the NFS service DNS name, and external e2e storage test schemas. Risks include over-advertising capabilities that may not hold on all clusters, hard-coded `default` namespace service, and snapshot class ambiguity. Test signal is the external conformance matrix selected by `run.sh`.
