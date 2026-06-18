# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template renders the v4.2.0 NFS CSI controller Deployment. It is a simpler controller than later versions, containing provisioner, liveness, and NFS driver containers only.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` with `csi-provisioner`, `liveness-probe`, and privileged `nfs` containers. It uses direct image repository/tag values, `--extra-create-metadata=true`, leader election, `--working-mount-dir`, driver name, mount permissions, and host kubelet pod mount propagation.

## Control Flow, State, and Persistence
The pod uses `hostNetwork: true`, controller DNS policy, optional affinity, hard-coded priority class `system-cluster-critical`, run-on-master/control-plane node selector labels, and an `emptyDir` CSI socket. Persistent effects are PV/PVC objects, events, leases, and directories on the configured NFS server.

## Dependencies and Integration Points
It depends on the controller service account from RBAC, the external provisioner RBAC role, the `CSIDriver` object, and `StorageClass` resources supplied outside this chart version. It does not include resizer or snapshotter sidecars.

## Risks and Test Signals
Risks include no expansion sidecar, no snapshot support, privileged host mount access, old liveness `--health-port` style, and node placement through nodeSelector labels instead of node affinity. Signals are successful deployment rollout, leader-election lease creation, PVC provisioning/deletion, liveness health, and rendering with `runOnMaster`/`runOnControlPlane`.
