# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.7.0 NFS CSI controller. It keeps the hardened v4.6.0 deployment shape and upgrades the provisioner, snapshotter, liveness probe, and NFS driver images.

## Important APIs, Types, and Functions
The `Deployment` is still one `csi-nfs-controller` replica in `kube-system` with hostNetwork, Linux node selection, control-plane tolerations, and shared `/csi/csi.sock`. Containers are `csi-provisioner:v5.0.1`, `csi-snapshotter:v8.0.1`, `livenessprobe:v2.13.1`, and `nfsplugin:v4.7.0`. Sidecars drop all capabilities, the NFS container is privileged with `SYS_ADMIN`, and health probing uses `--http-endpoint=localhost:29652` plus an HTTP liveness probe to localhost port 29652.

## Control Flow, State, and Persistence
The controller creates a pod-local CSI socket, sidecars run leader-elected Kubernetes watch loops, and the NFS driver performs controller-side mount/directory work through host networking and host pod mount access. Persistent state remains in PV/PVC/snapshot custom resources, events, coordination leases, and host-mounted kubelet pod directories.

## Dependencies and Integration Points
It depends on updated RBAC, especially because v4.7.0 RBAC adds PV patch permission, as well as the `CSIDriver`, snapshot CRDs, snapshot controller v8.0.1, and registry image availability. It integrates with storage classes and snapshot classes naming `nfs.csi.k8s.io`.

## Risks and Test Signals
Risks include major upgrades to `csi-provisioner:v5.0.1` and snapshotter v8.0.1, RBAC incompatibility if older RBAC is reused, and privileged host mount behavior. Test signals are no provisioner RBAC denials, healthy 29652 probes, successful PVC create/delete including PV patch operations, snapshot create/delete with v8 sidecars, and stable rollout from v4.6.0.
