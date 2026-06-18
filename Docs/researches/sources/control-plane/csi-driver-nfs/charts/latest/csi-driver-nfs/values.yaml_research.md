# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/values.yaml

Purpose: Default values for the latest/canary CSI NFS Helm chart.

Important APIs/types/functions: Helm values configure image repositories/tags, service accounts, RBAC, driver name, feature gates, kubelet paths, controller/node pod settings, external snapshotter, optional `VolumeSnapshotClass`, image pull secrets, one `storageClass`, and multiple `storageClasses`.

Control flow: Templates read these values to choose sidecar images, render optional resources, set scheduling policy, enable snapshotter and snapshot compression, propagate host mount options, and configure node-driver-registrar liveness options.

State and persistence: Values themselves are chart input; persisted state appears as rendered Kubernetes objects and workload pods.

Dependencies and integration points: Uses staging/canary NFS plugin and newer sidecars (`csi-provisioner`, `csi-resizer`, `csi-snapshotter`, livenessprobe, registrar, snapshot-controller). `baseRepo` combines with repositories beginning with `/`.

Risks: Canary images are not release-pinned. Feature defaults can install privileged host-mounted pods and cluster-wide RBAC. Test signals: `helm lint`, `helm template`, image reference checks, and install/upgrade tests with snapshot/storage class options.
