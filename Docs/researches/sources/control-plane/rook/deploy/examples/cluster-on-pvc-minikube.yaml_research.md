
# sources/control-plane/rook/deploy/examples/cluster-on-pvc-minikube.yaml

Purpose: provides a single-node Minikube example using local PVs and PVC-backed OSDs for development testing.

Important APIs/types/functions: local `StorageClass`, four `PersistentVolume` objects for Minikube devices `/dev/vdb` through `/dev/vde`, Rook `CephCluster` with `mon.count: 1`, `allowMultiplePerNode: true`, one mgr, block-mode `storageClassDeviceSets`, and a `CephBlockPool` named `.mgr` with replica size 1.

Control flow: the single filesystem PV backs the mon, three block PVs back OSD PVCs, and Rook runs all Ceph daemons on the Minikube node. The built-in manager pool is explicitly created with unsafe single-replica settings.

State and persistence: data persists on the configured Minikube extra disks and `/var/lib/rook`. The `.mgr` pool and OSDs are intentionally non-redundant.

Dependencies/integration: depends on Minikube device naming, local PV support, Rook common/operator manifests, and an environment with extra disks created as described by the comments.

Risks: device names differ by Minikube driver. Single monitor and replica size 1 can lose data. `quay.io/ceph/ceph:v20` is less precise than a patch tag.

Test signals: verify Minikube has expected devices, PVs bind, CephCluster becomes ready, `.mgr` pool exists with size 1, and basic RBD/Ceph health commands succeed.
