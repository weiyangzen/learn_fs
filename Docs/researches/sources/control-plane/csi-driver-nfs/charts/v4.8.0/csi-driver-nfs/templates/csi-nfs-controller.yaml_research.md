# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
Renders the v4.8.0 controller `Deployment` for CSI NFS control-plane functions.

## Important APIs, Types, And Functions
Defines an `apps/v1 Deployment` with `csi-provisioner`, `csi-snapshotter`, `liveness-probe`, and privileged `nfs` containers. Uses Helm values for images, leader election namespace, resource blocks, controller scheduling, driver name, mount permissions, working mount directory, and delete policy.

## Control Flow
The provisioner connects to the shared CSI socket, runs leader election, creates metadata, and sets `--feature-gates=HonorPVReclaimPolicy=true`. The NFS container starts the CSI endpoint with controller flags and mounts kubelet pods with bidirectional propagation. Images can be resolved through `baseRepo` when repository values start with `/`.

## State And Persistence
Persistent state is in Kubernetes PV/PVC/snapshot objects, events, leases, and NFS server directories. Unlike v4.7.0, this template no longer mounts an `emptyDir` at `.Values.controller.workingMountDir`.

## Dependencies And Integration Points
Integrates with controller service account/RBAC, node daemonset, snapshot CRDs/RBAC when enabled, kubelet host paths, and the `nfsplugin` flags in `cmd/nfsplugin/main.go`.

## Risks And Edge Cases
The privileged controller can mount NFS and host kubelet pod paths, so node placement matters. The removal of the temporary working mount volume changes filesystem behavior compared with v4.7.0. Reclaim policy honoring can alter deletion outcomes during upgrades.

## Test Signals
Check rendered deployment diffs from v4.7.0, controller pod readiness, PV deletion behavior with different reclaim policies, leader leases, and liveness endpoint status.
