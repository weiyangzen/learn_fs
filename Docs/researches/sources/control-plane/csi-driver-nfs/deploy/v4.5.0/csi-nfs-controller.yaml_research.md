# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.5.0 NFS CSI controller. It is structurally the same controller deployment as v4.4.0 with sidecar and driver image updates for the v4.5.0 release.

## Important APIs, Types, and Functions
The `Deployment` remains `csi-nfs-controller` in `kube-system`, one replica, hostNetwork, `ClusterFirstWithHostNet`, `system-cluster-critical`, Linux-only scheduling, and control-plane tolerations. Containers are `csi-provisioner:v3.6.1`, `csi-snapshotter:v6.3.1`, `livenessprobe:v2.11.0`, and `nfsplugin:v4.5.0`. Sidecars still use `/csi/csi.sock`, leader election, extra create metadata, and `--timeout=1200s`; the driver keeps privileged `SYS_ADMIN` access and port-named health checks on 29652.

## Control Flow, State, and Persistence
The pod lifecycle and controller flow mirror v4.4.0: the NFS process exposes a CSI socket from an `emptyDir`, sidecars drive Kubernetes watches and CSI calls, and state is persisted in PV/PVC/snapshot API objects plus host pod mount directories. The only behavioral deltas visible in YAML are upgraded images, so runtime changes depend on the new sidecar and driver binaries.

## Dependencies and Integration Points
It depends on the same RBAC, `CSIDriver`, snapshot CRDs, kube-system leader-election leases, Linux host mounts, and registry image availability as v4.4.0. The sidecar versions align with the v4.5.0 snapshot controller manifest.

## Risks and Test Signals
Risks include upgrade compatibility from provisioner v3.5.0 to v3.6.1, snapshotter v6.2.2 to v6.3.1, and liveness v2.10.0 to v2.11.0 while still using named health ports. Test signals are rollout success from v4.4.0, no forbidden or deprecated API warnings, healthy port 29652, successful provisioning and deletion, successful snapshots, and no CSI timeout regressions.
