# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/snapshotclass.yaml

Purpose: optionally renders an RBD `VolumeSnapshotClass`.

Important APIs/types/functions: gated by `.Values.volumeSnapshotClass.create`; sets driver, `clusterID`, optional `snapshotNamePrefix`, snapshotter secret name/namespace, annotations, labels, and deletion policy.

Control flow: external-snapshotter uses this class to create `VolumeSnapshotContent` objects and call the RBD CSI snapshot service.

State and persistence behavior: class is cluster-scoped; snapshots persist as Kubernetes snapshot CRs and Ceph RBD snapshots.

Dependencies and integration points: requires snapshot CRDs/controller, provisioner snapshotter sidecar, configured Ceph cluster ID, and credentials.

Risks: missing CRDs or secret namespace mismatch break snapshot creation. Deletion policy affects whether backing snapshots are retained.

Test signals: snapshot/restore e2e tests and Helm rendering with the create flag.
