# sources/control-plane/ceph-csi/examples/nvmeof/snapshot.yaml

Purpose: example NVMe-oF `VolumeSnapshot`.

Important fields and flow: Snapshot `nvme-pvc-snapshot` uses class `csi-nvmeplugin-snapclass` and source PVC `nvmeof-pvc`.

State, dependencies, and integration: creates an RBD snapshot for the NVMe-oF-backed volume through the CSI snapshotter.

Risks and test signals: requires snapshot class, secrets, and a ready source PVC. Restore success validates snapshot data.
