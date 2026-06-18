# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This DaemonSet template installs the 4.12.1 NFS CSI node service on every eligible Linux node.

## APIs, Control Flow, and State
It renders an `apps/v1` DaemonSet using node scheduling values, critical priority, host networking, seccomp, broad tolerations by default, and a rolling update strategy. Containers include liveness probe, node-driver-registrar, and privileged NFS CSI server. HostPath volumes persist the CSI socket under `kubeletDir/plugins/csi-nfsplugin`, expose kubelet plugin registry, and provide pod mount propagation through `kubeletDir/pods`.

## Dependencies and Integration Points
The registrar integrates with kubelet, the CSIDriver object advertises the same driver name, and the NFS container performs node-stage/publish mount operations. The 4.12.1 node template is identical to 4.12.0; runtime version changes come from default images.

## Risks and Test Signals
Registration silently fails when kubelet paths differ from `kubeletDir`. Privileged host access should be reviewed against cluster policy. Test node plugin registration, pod PVC mounts, DaemonSet rollout, and node health after kubelet restarts.
