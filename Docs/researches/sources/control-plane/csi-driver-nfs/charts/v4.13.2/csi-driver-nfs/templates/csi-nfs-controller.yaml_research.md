# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This file renders the v4.13.2 NFS CSI controller Deployment, combining controller-side CSI sidecars with the privileged NFS plugin container.

## Important APIs, Types, and Functions
The template emits an `apps/v1` `Deployment` with containers for `csi-provisioner`, `csi-resizer`, optional `csi-snapshotter`, `liveness-probe`, and `nfs`. It passes provisioner feature gates for `HonorPVReclaimPolicy` and `VolumeAttributesClass=false`, resizer `VolumeAttributesClass=false`, long timeouts/retry intervals, and NFS driver arguments for mount permissions, working mount dir, delete policy, tar snapshot mode, and snapshot compression.

## Control Flow, State, and Persistence
Rendering follows values for replica count, Recreate/Rolling strategy type, scheduling, image pull secrets, and resources. The pod uses host networking and a host kubelet pods mount with bidirectional propagation. Sidecar leader election is persisted in namespace `Lease` objects; provisioned volume and snapshot state lives in Kubernetes objects and the external NFS share.

## Dependencies and Integration Points
The Deployment depends on controller RBAC, service account names, snapshot CRDs/RBAC when snapshotting is enabled, the `CSIDriver` object, and storage classes that target `.Values.driver.name`. Image repository handling supports either full repositories or paths joined with `image.baseRepo`.

## Risks and Test Signals
Risks are privileged mount capability, hostNetwork DNS behavior, sidecar version/API skew, snapshotter enabled without cluster snapshot APIs, and operational impact of `defaultOnDeletePolicy`. Signals are `helm lint`, `helm template`, rollout readiness, sidecar lease objects, PVC provision/delete/expand tests, and snapshot creation with compression/tar settings varied.
