<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-volumesnapshotclasses.sh -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/create-volumesnapshotclasses.sh

Purpose: materializes VolumeSnapshotClass templates for k8s storage e2e tests.

Control flow: reads Rook fsid from toolbox pod, loops over `volumesnapshotclass-*.yaml.in`, substitutes `@@CLUSTER_ID@@`, and creates each manifest.

State and persistence: creates Kubernetes VolumeSnapshotClasses.

Dependencies: kubectl, Rook toolbox, snapshot CRDs already installed, template files.

Integration points: driver YAMLs reference these snapshot class names for snapshot e2e coverage.

Risks: repeated runs fail on existing resources. Assumes snapshot CRDs/controllers are installed separately.

Test signals: no unit tests; snapshot e2e validates indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-volumesnapshotclasses.sh -->
