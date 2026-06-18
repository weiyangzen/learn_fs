<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-rbd.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-rbd.yaml.in

Purpose: RBD VolumeSnapshotClass template for e2e snapshot tests.

Content: driver `rbd.csi.ceph.com`, cluster ID placeholder, Rook RBD snapshotter secret reference, and `Delete` deletion policy.

State and dependencies: created by `create-volumesnapshotclasses.sh`; requires snapshot CRDs and Rook secrets.

Integration points: referenced by `driver-rbd.yaml`.

Risks: hardcoded secret namespace/name and delete policy. Repeated create can fail if class already exists.

Test signals: used by snapshot e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-rbd.yaml.in -->
