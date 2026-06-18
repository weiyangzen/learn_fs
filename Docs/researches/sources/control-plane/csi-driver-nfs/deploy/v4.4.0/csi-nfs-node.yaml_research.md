# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-node.yaml

## Purpose
This manifest deploys the v4.4.0 NFS CSI node plugin as a Linux `DaemonSet`. It registers the driver with kubelet on every node and performs node-side NFS mount operations for pods.

## Important APIs, Types, and Functions
The main object is an `apps/v1` `DaemonSet` named `csi-nfs-node` in `kube-system`. Containers are `livenessprobe:v2.10.0`, `csi-node-driver-registrar:v2.8.0`, and `nfsplugin:v4.4.0`. The registrar advertises `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` through `/registration`; the NFS container runs privileged with `SYS_ADMIN`, uses `--endpoint=unix:///csi/csi.sock`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

## Control Flow, State, and Persistence
Kubernetes rolls the DaemonSet with `maxUnavailable: 1` and schedules it on every Linux node via broad tolerations. The driver creates the CSI socket under a hostPath plugin directory, the registrar registers it with kubelet, and kubelet calls the node service to stage and publish NFS volumes. Persistent node state is hostPath socket/registration data and bind mounts under kubelet pod directories; the liveness container probes the shared socket on health port 29653.

## Dependencies and Integration Points
The node plugin depends on `csi-nfs-node-sa`, the `CSIDriver` object, kubelet plugin and plugin registry host paths, host networking, Linux mount propagation, and the NFS CSI controller for provisioning. It integrates directly with kubelet rather than the Kubernetes API for most node calls.

## Risks and Test Signals
Risks include privileged node access, kubelet path differences, missing mount propagation support, stale registration sockets during upgrades, and NFS connectivity failures hidden as pod mount timeouts. Test signals are one ready pod per Linux node, `kubectl get csinode` listing `nfs.csi.k8s.io`, registrar liveness success, healthy port 29653, and pods successfully mounting dynamically provisioned NFS PVCs.
