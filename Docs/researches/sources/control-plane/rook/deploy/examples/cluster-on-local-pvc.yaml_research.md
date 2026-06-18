
# sources/control-plane/rook/deploy/examples/cluster-on-local-pvc.yaml

Purpose: demonstrates a production-style Rook Ceph cluster using manually defined local PVs: filesystem PVs for mons and block PVs for OSD PVCs.

Important APIs/types/functions: Kubernetes `StorageClass` `local-storage` with `kubernetes.io/no-provisioner`, six `PersistentVolume` objects with `Retain` reclaim policy and node affinity, and Rook `CephCluster` with mon `volumeClaimTemplate`, `storage.storageClassDeviceSets`, topology spread constraints, prepare pod anti-affinity, priority classes, and disruption management.

Control flow: Kubernetes binds local PVs only when consumers are scheduled. Rook creates mon PVCs from the filesystem template and OSD PVCs from the block-mode device set, then schedules OSD prepare and daemon pods across hosts `host0`, `host1`, and `host2`.

State and persistence: Ceph data persists on host devices `/dev/sdb` and `/dev/sdc` through Retain PVs and under `dataDirHostPath`. Deleting the cluster does not automatically delete retained local PV data.

Dependencies/integration: depends on exact node hostnames, real devices at configured paths, local PV support, Rook common/operator manifests, and Kubernetes scheduler topology behavior.

Risks: wrong device paths can destroy unintended disks. Hostname drift prevents PV scheduling. Retained PVs require manual cleanup before reinstall. Local PVs are not portable, so `portable: false` is required.

Test signals: verify PV availability and node affinity, apply the cluster, check PVC binding distribution, confirm three mons and three OSDs, and test node drain/PDB behavior.
