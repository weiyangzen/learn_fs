# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
Renders the v4.9.0 node `DaemonSet` for kubelet CSI registration and node-side NFS publish operations.

## Important APIs, Types, And Functions
Uses liveness-probe, node-driver-registrar, and privileged NFS plugin containers; hostPath volumes for socket, kubelet pods, and registration; optional host NFS config mounts; and values for node scheduling, resources, health port, log level, and image tags.

## Control Flow
Kubernetes schedules one pod per matching Linux node. The registrar advertises the kubelet registration path, the NFS plugin listens on the CSI socket, liveness checks use the configured health port, and optional host mount configuration is mounted when enabled.

## State And Persistence
HostPath socket and registration directories persist on nodes. NFS mount state and workload pod mounts are mediated through the kubelet pod directory with bidirectional propagation.

## Dependencies And Integration Points
Works with `CSIDriver`, kubelet, controller-provisioned PVs, host networking, and the NFS plugin binary. The driver name must match StorageClass and controller settings.

## Risks And Edge Cases
Byte-identical to v4.7.0 and v4.8.0 in this source set. Incorrect `kubeletDir`, missing registration directory, or restricted privileged execution blocks mounts. Host config propagation can make behavior node-dependent.

## Test Signals
DaemonSet readiness, registrar probe success, socket files under kubelet plugins, `CSINode` state, and workload pod mount/unmount tests.
