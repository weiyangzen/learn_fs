# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the v4.3.0 node DaemonSet for NFS CSI plugin registration and node-side mounts.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with liveness probe, node-driver-registrar, and privileged `nfs` containers. Compared with v4.2.0 it adds pod `seccompProfile: RuntimeDefault`, read-only liveness root filesystem, and hard-coded `system-node-critical` priority.

## Control Flow, State, and Persistence
The DaemonSet uses host networking, `dnsPolicy: {{ .Values.controller.dnsPolicy }}`, hard-coded `csi-nfs-node-sa`, host paths for CSI socket/pods/plugin registry, and rolling updates. Host state is kubelet registration sockets and mounted pod volumes.

## Dependencies and Integration Points
It depends on the default service account names from RBAC, kubelet path defaults, and matching driver names. Kubelet consumes the registrar's socket registration path.

## Risks and Test Signals
Risks include hard-coded node service account, controller DNS policy reuse, old exec-based registrar liveness probe, privileged host access, and no host mount option propagation feature yet. Signals are DaemonSet rollout, CSINode entries, registrar health, pod mount/unmount tests, and custom kubeletDir rendering.
