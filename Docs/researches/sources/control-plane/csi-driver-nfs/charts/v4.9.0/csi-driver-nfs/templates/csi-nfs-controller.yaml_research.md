# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
Renders the v4.9.0 CSI NFS controller `Deployment` with updated control-plane scheduling logic.

## Important APIs, Types, And Functions
Defines an `apps/v1 Deployment` with provisioner, snapshotter, liveness probe, and privileged NFS plugin containers. It uses Helm functions `contains`, `tpl`, `with`, `toYaml`, `hasPrefix`, and values for images, resources, driver flags, leader election, tolerations, node selectors, and affinity.

## Control Flow
The controller always uses host networking. If `.Values.controller.affinity` already contains `nodeSelectorTerms`, it is rendered directly. Otherwise `runOnControlPlane` and `runOnMaster` generate required node affinity rather than nodeSelector labels. The provisioner honors PV reclaim policy, and all sidecars communicate over `/csi/csi.sock`.

## State And Persistence
State lives in PV/PVC/snapshot objects, events, leader-election leases, host kubelet pod mounts, and NFS server directories. The socket directory is an `emptyDir`; kubelet pods are mounted from hostPath.

## Dependencies And Integration Points
Depends on RBAC, service accounts, kubelet host paths, snapshot CRDs/RBAC if enabled, image tags from v4.9.0 values, and `nfsplugin` controller flags including working mount directory and default delete policy.

## Risks And Edge Cases
The v4.9.0 affinity branch checks rendered affinity text for `nodeSelectorTerms`, which can miss nonstandard affinity shapes. Switching from nodeSelector labels to required node affinity changes scheduling semantics for control-plane placement. Privileged `SYS_ADMIN` remains a high-trust requirement.

## Test Signals
Render tests for custom affinity, `runOnControlPlane`, and `runOnMaster`; controller rollout; leader election; PV reclaim behavior; provisioning and delete policy tests.
