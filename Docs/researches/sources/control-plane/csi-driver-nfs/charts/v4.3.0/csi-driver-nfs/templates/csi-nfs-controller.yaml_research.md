# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template renders the v4.3.0 NFS CSI controller Deployment, adding snapshot support compared with v4.2.0 but not yet including the resizer sidecar found in v4.13.x.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` with `csi-provisioner`, optional `csi-snapshotter`, `liveness-probe`, and privileged `nfs` containers. It adds pod `seccompProfile: RuntimeDefault`, read-only root filesystems for non-driver sidecars, `--default-ondelete-policy`, and an `emptyDir` mounted at `.Values.controller.workingMountDir`.

## Control Flow, State, and Persistence
Snapshot sidecar rendering follows `externalSnapshotter.enabled`. Control-plane/master scheduling is still implemented through nodeSelector labels when no custom nodeSelector overrides them. Sidecars use namespace leader election, and the NFS driver uses host pod mount propagation plus a pod-local working directory.

## Dependencies and Integration Points
The controller depends on v4.3.0 RBAC, service account defaults, snapshot CRDs when enabled, `CSIDriver`, and any externally supplied StorageClass. It does not include volume expansion support.

## Risks and Test Signals
Risks are optional snapshot sidecar without resources, lack of resizer, privileged host mounts, and older nodeSelector-based control-plane placement. Signals are rendered diffs with snapshot on/off, controller rollout, PVC lifecycle, snapshot creation when enabled, and checking the working mount directory is writable.
