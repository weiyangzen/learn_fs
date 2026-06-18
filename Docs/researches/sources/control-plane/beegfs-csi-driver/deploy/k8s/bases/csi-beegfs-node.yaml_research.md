<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-node.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-node.yaml

## Purpose
This base manifest defines the node-service `DaemonSet` that runs the BeeGFS CSI node plugin on every selected Kubernetes node.

## Important Objects and Fields
The `DaemonSet` is named `csi-beegfs-node`, uses service account `csi-beegfs-node-sa`, host networking, and containers `node-driver-registrar`, `beegfs`, and `liveness-probe`. The driver exposes health port 9898, connects to `unix://csi/csi.sock`, reads config/connauth/TLS files, and receives node ID from `spec.nodeName`.

## Control Flow
The driver container creates the CSI socket under the host plugin directory. `node-driver-registrar` registers that socket path with kubelet through `/var/lib/kubelet/plugins_registry`. `liveness-probe` checks the CSI socket over `/csi` and exposes health over port 9898.

## State and Persistence
Host-mounted state includes `/var/lib/kubelet/pods`, `/var/lib/kubelet/plugins/kubernetes.io/csi`, `/var/lib/kubelet/plugins_registry`, and `/var/lib/kubelet/plugins/beegfs.csi.netapp.com`. These mounts let the driver inspect mountpoints, publish volumes, and register with kubelet.

## Dependencies and Integration Points
It integrates with Kubelet CSI registration, CSI livenessprobe, generated config/secrets, `chwrap` host command execution via `/host`, and operator expectations for stable container and volume names.

## Risks
The DaemonSet requires privileged containers, host networking, host root visibility, and mount propagation. Host port 9898 must be free on every node. Registration directory type is `Directory`, not `DirectoryOrCreate`, assuming kubelet has created it. Config/secret generators must be applied for named volumes.

## Test Signals
Signals include daemon pod readiness on all nodes, socket registration in kubelet, liveness endpoint success, mount/unmount operations, e2e example pod startup, and `deploy_test.go` checks for stable containers and volume resource references.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-node.yaml -->
