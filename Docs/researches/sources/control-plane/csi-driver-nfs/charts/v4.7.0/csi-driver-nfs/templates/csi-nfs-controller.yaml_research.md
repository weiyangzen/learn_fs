# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
Renders the v4.7.0 controller `Deployment` for the CSI NFS driver. The pod hosts control-plane sidecars plus the NFS CSI plugin in controller mode so dynamic provisioning, snapshotting, liveness, and server-side directory management run together.

## Important APIs, Types, And Functions
Uses `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.driver.*`, `include "nfs.labels"`, `hasPrefix`, `toYaml`, `nindent`, and Helm release namespace templating. Containers are `csi-provisioner`, `csi-snapshotter`, `liveness-probe`, and privileged `nfs`.

## Control Flow
Helm resolves image repositories, resource blocks, scheduling settings, and command-line flags. The provisioner connects to `/csi/csi.sock`, uses leader election, enables extra metadata, sets `HonorPVReclaimPolicy=false`, and waits up to 1200 seconds. The NFS container starts the CSI endpoint, mounts kubelet pods with bidirectional propagation, and receives node name from the pod spec.

## State And Persistence
State is mostly external: Kubernetes leases for leader election, PV/PVC/snapshot objects, the host kubelet pod mount tree, and NFS server paths. In v4.7.0 the controller also mounts an `emptyDir` at `.Values.controller.workingMountDir` for temporary NFS mounts.

## Dependencies And Integration Points
Depends on RBAC in `rbac-csi-nfs.yaml`, service accounts, snapshot CRDs if snapshotting is used, host networking for NFS mount operations, kubelet directory layout, and the `nfsplugin` binary flags defined by `cmd/nfsplugin/main.go`.

## Risks And Edge Cases
The `nfs` container is privileged with `SYS_ADMIN`, so scheduling and namespace isolation matter. `HonorPVReclaimPolicy=false` may ignore PV reclaim policy behavior that later chart versions enable. The explicit working mount `emptyDir` can hide host paths and differs from v4.8.0+.

## Test Signals
Use `helm template` and Kubernetes schema validation. Runtime checks include controller pod readiness, liveness endpoint on the configured health port, leader election leases, provisioned PVs, and successful cleanup respecting the configured delete policy.
