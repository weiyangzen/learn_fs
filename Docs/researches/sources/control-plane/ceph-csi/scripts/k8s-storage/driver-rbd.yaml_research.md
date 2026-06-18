<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-rbd.yaml -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/driver-rbd.yaml

Purpose: Kubernetes storage e2e driver configuration for RBD.

Content and behavior: uses existing StorageClass and SnapshotClass `k8s-storage-e2e-rbd`, driver name `rbd.csi.ceph.com`, size range 1Gi to 16Ti, fs types ext4/xfs, mount option `rw`, and capability matrix including persistence, block, exec, controller/node expansion, multipods, read-write-once-pod, snapshot/PVC data sources, and read-only-many for snapshot data sources; RWX and topology are false.

State and dependencies: consumed by Kubernetes storage e2e framework.

Integration points: paired with `sc-rbd.yaml.in` and `volumesnapshotclass-rbd.yaml.in`.

Risks: declared capabilities must track actual RBD behavior and e2e requirements. Topology is disabled in this e2e configuration even though other Ceph-CSI code supports topology-aware provisioning.

Test signals: e2e test configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-rbd.yaml -->
