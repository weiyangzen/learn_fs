# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template deploys the node service as an `apps/v1` `DaemonSet`. It registers the CSI driver with kubelet on every Linux node and performs node-side NFS mount work.

## APIs, Control Flow, and State
The DaemonSet uses rolling updates with `node.maxUnavailable`, `hostNetwork: true`, the node service account, Linux node selector, tolerations, affinity, priority class, and pod seccomp defaulting. It runs `liveness-probe`, `node-driver-registrar`, and privileged `nfs`. The registrar points kubelet to `$(kubeletDir)/plugins/csi-nfsplugin/csi.sock` and mounts `/registration`; the NFS container exposes `unix:///csi/csi.sock`, receives `NODE_ID`, uses the configured driver name and mount permissions, and mounts kubelet pod directories with bidirectional propagation.

## Dependencies and Integration Points
HostPath volumes connect the pod to kubelet plugin, plugin registry, and pod mount directories. The CSIDriver object must share the same driver name, and kubelet must use the same `kubeletDir`. RBAC creates the node service account but node runtime behavior mostly depends on host filesystem and kubelet registration.

## Risks and Test Signals
Privileged SYS_ADMIN plus bidirectional host mounts are necessary but sensitive. Wrong `kubeletDir` or missing host directories blocks registration. Test with `kubectl get pods -l app=csi-nfs-node`, kubelet plugin registration files, successful volume mounts on multiple nodes, rolling update behavior, and liveness failures.
