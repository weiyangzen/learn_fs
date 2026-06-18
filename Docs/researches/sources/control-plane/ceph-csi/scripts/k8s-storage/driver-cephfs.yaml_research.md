<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-cephfs.yaml -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/driver-cephfs.yaml

Purpose: Kubernetes storage e2e driver configuration for CephFS.

Content and behavior: names existing StorageClass and SnapshotClass `k8s-storage-e2e-cephfs`, sets driver name `cephfs.csi.ceph.com`, supported size range 1Gi to 16Ti, mount option `rw`, and capability matrix including persistence, multipods, online/controller expansion, read-write-once-pod, read-only-many, exec, RWX, snapshot/PVC data sources, and no block/topology/node expansion.

State and dependencies: consumed by Kubernetes e2e test framework, not by the driver at runtime.

Integration points: aligned with `sc-cephfs.yaml.in` and `volumesnapshotclass-cephfs.yaml.in`.

Risks: capability drift with actual CephFS driver behavior can cause false test expectations. `fsGroup` and topology are declared unsupported here.

Test signals: used by e2e suite.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-cephfs.yaml -->
