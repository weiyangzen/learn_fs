# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-snapshot-controller.yaml

Purpose: deploys the external snapshot controller that reconciles Kubernetes `VolumeSnapshot` and `VolumeSnapshotContent` objects for CSI drivers.

Important APIs/types/functions: the file defines an `apps/v1` `Deployment` named `snapshot-controller` in `kube-system`, usually with two replicas, service account `snapshot-controller`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and image `registry.k8s.io/sig-storage/snapshot-controller:v8.2.0`. Arguments enable leader election in the pod namespace or `kube-system` depending on the release.

Control flow: after snapshot CRDs exist, the controller watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PV, and PVC objects. It binds snapshot requests to snapshot contents, coordinates status updates, and relies on CSI snapshotter sidecars in driver controller pods for driver-specific RPC execution.

State and persistence: the controller persists reconciliation state through snapshot API objects, status fields, Kubernetes Events, and leader-election Leases. It stores no snapshot data in the pod.

Dependencies and integration points: requires `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, and driver-side `csi-snapshotter` support. It integrates with `snapshotclass.yaml` and all `deploy/example/snapshot` resources.

Risks: starting before CRDs are installed leaves the deployment unready or crash-looping. Version skew between the controller, CRDs, and `csi-snapshotter` sidecar can break status transitions. Running two replicas requires working leader election RBAC.

Test signals: check rollout status, verify leader election Leases in `kube-system`, create `snapshot-nfs-dynamic.yaml`, and confirm a ready `VolumeSnapshotContent` plus successful restored PVC.
