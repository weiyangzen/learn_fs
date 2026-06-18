# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/values.yaml

Purpose: Default values for v4.10.0 chart.

Important APIs/types/functions: Image baseRepo and sidecar tags, controller/node service accounts, RBAC name, driver, feature gates, kubeletDir, controller snapshotter/resizer settings, external snapshotter, optional CRDs/classes, and StorageClass example.

Control flow: Values enable snapshotter by default inside the CSI controller but disable standalone externalSnapshotter and optional classes by default. They configure host networking, priority classes, resources, default delete policy, tar snapshot behavior, and host mount option propagation.

State and persistence: Helm configuration; rendered workloads/RBAC/CRDs/classes persist in cluster.

Dependencies and integration points: Coordinates csi-provisioner v5.2.0, csi-resizer v1.13.1, snapshotter v8.2.0, and NFS plugin v4.10.0.

Risks: Snapshot sidecar enabled while CRDs/external controller are optional requires cluster preconditions. Test signals: render with default and full snapshot/storage options.
