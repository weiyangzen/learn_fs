<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-cephfs.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-cephfs.yaml.in

Purpose: CephFS VolumeSnapshotClass template for e2e snapshot tests.

Content: driver `cephfs.csi.ceph.com`, cluster ID placeholder, Rook CephFS snapshotter secret reference, and `Delete` deletion policy.

State and dependencies: created by `create-volumesnapshotclasses.sh`; requires snapshot CRDs and Rook secrets.

Integration points: referenced by `driver-cephfs.yaml` as existing snapshot class.

Risks: hardcoded secret namespace/name and delete policy. Snapshot controller must be installed separately.

Test signals: used by snapshot e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-cephfs.yaml.in -->
