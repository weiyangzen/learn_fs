<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-node.yaml

## Purpose
Defines the v4.12.1 NFS CSI node DaemonSet. It is the per-node runtime responsible for kubelet registration and NFS volume mount/unmount operations.

## Important APIs, Types, And Objects
The DaemonSet runs `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.12.1`. It uses host paths `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/pods`, and `/var/lib/kubelet/plugins_registry`, with bidirectional mount propagation for pod mounts.

## Control Flow
On each Linux node, the NFS plugin serves CSI over `/csi/csi.sock`; the registrar advertises the host socket path to kubelet; kubelet calls the node service to publish volumes for pods. The liveness container checks `localhost:29653`.

## State And Persistence Behavior
The plugin socket and registration files are host-local runtime state. Actual mount state lives in the node mount table and kubelet directories. Kubernetes persists desired scheduling and volume attachment-free volume usage in API objects.

## Dependencies And Integration Points
Requires kubelet's CSI plugin registry, Linux NFS mount support, the v4.12.1 controller, matching `CSIDriver`, and provisioned PVs referencing the NFS CSI driver.

## Risks And Edge Cases
Privileged execution and bidirectional mount propagation remain the main operational risk. Kubelet root path assumptions must match the host. The plugin-only image bump from v4.12.0 should be tested for mount compatibility and upgrade behavior.

## Test Signals
Confirm one ready pod per target node, successful CSI registration in `CSINode`, mount/unmount behavior for workload pods, health endpoint readiness, and node pod rolling update with existing mounted workloads.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-node.yaml -->
