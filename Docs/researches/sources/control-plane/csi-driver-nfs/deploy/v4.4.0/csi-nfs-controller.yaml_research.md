# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.4.0 NFS CSI controller as a single `kube-system` `Deployment`. It hosts the controller-side NFS CSI process plus provisioner, snapshotter, and liveness sidecars that drive PVC provisioning and CSI snapshot operations.

## Important APIs, Types, and Functions
The main object is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica and labels `app: csi-nfs-controller`. Containers are `csi-provisioner:v3.5.0`, `csi-snapshotter:v6.2.2`, `livenessprobe:v2.10.0`, and `nfsplugin:v4.4.0`. The sidecars share `/csi/csi.sock`; provisioner and snapshotter enable leader election in `kube-system` and use long `--timeout=1200s` CSI calls. The NFS container runs `--nodeid=$(NODE_ID)` and `--endpoint=$(CSI_ENDPOINT)` with `SYS_ADMIN`, `privileged: true`, and bidirectional mount propagation on `/var/lib/kubelet/pods`.

## Control Flow, State, and Persistence
Kubernetes creates one controller pod on Linux, tolerating control-plane taints and using host networking so the controller can mount NFS while creating backing directories. The NFS driver creates the Unix CSI socket in an `emptyDir`, the sidecars connect to it, and leader-elected sidecars watch PVCs, PVs, snapshot resources, leases, and events through the service account. Persistent state lives in Kubernetes objects and host-mounted pod directories; pod-local socket state is ephemeral.

## Dependencies and Integration Points
This deployment depends on `rbac-csi-nfs.yaml` for `csi-nfs-controller-sa`, `csi-nfs-driverinfo.yaml` for the `CSIDriver`, snapshot CRDs and snapshot RBAC for snapshot flows, kubelet host paths, and registry images from `registry.k8s.io/sig-storage`. It also expects NFS client tooling and kernel mount support in the `nfsplugin` image and reachable NFS servers from host networking.

## Risks and Test Signals
Risks include privileged mount access, hostNetwork DNS behavior, long-running CSI operations tying up sidecars, missing CRDs causing snapshotter failures, and named health port exposure on the host network. Test signals are a ready deployment, healthy `/healthz` on port 29652, one lease holder for provisioner/snapshotter leader election, successful dynamic provisioning with `nfs.csi.k8s.io`, successful snapshot creation, and clean sidecar logs with no CSI socket connection errors.
