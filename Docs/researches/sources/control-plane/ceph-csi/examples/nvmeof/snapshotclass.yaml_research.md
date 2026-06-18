# sources/control-plane/ceph-csi/examples/nvmeof/snapshotclass.yaml

Purpose: example NVMe-oF `VolumeSnapshotClass`.

Important fields and flow: class `csi-nvmeplugin-snapclass` uses driver `nvmeof.csi.ceph.com`, `deletionPolicy: Delete`, placeholder `clusterID`, optional snapshot name prefix, and snapshotter list/secret refs to `csi-nvme-secret`.

State, dependencies, and integration: configures snapshotting for NVMe-oF volumes, which are backed by RBD images.

Risks and test signals: placeholders and secret names must align with deployment. Snapshot readiness validates controller-side configuration.
