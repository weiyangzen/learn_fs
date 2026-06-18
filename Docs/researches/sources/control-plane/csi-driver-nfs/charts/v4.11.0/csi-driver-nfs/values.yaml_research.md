# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/values.yaml

Purpose: Default values for chart 4.11.0.

Important APIs/types/functions: Same value surface as v4.10.0 with NFS plugin tag updated to `v4.11.0`; sidecar tags remain provisioner v5.2.0, resizer v1.13.1, snapshotter/snapshot-controller v8.2.0, livenessprobe v2.15.0, registrar v2.13.0.

Control flow: Values control image refs, RBAC/service accounts, feature gates, controller/node scheduling/resources, optional snapshot controller/CRDs/classes, and optional StorageClass.

State and persistence: Helm release values and rendered Kubernetes resources.

Dependencies and integration points: Coordinates CSI sidecars, kubeletDir, snapshot APIs, and storage class parameters.

Risks: Snapshotter enabled by default in controller while external snapshotter/CRDs are disabled by default. Test signals: default render and full-feature snapshot/storage install dry-run.
