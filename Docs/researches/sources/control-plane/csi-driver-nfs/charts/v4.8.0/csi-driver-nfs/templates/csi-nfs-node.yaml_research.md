# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
Renders the v4.8.0 node `DaemonSet` for CSI socket registration and node-side NFS mount operations.

## Important APIs, Types, And Functions
Uses `apps/v1 DaemonSet`, liveness-probe, node-driver-registrar, and privileged NFS plugin containers. Values control kubelet paths, resources, image tags, mount options propagation, scheduling, health ports, and driver flags.

## Control Flow
Each Linux node gets a pod. The registrar registers the plugin socket path with kubelet, the NFS plugin serves CSI node calls from `/csi/csi.sock`, and liveness probes monitor both the registrar and plugin HTTP endpoint.

## State And Persistence
Uses hostPath volumes for plugin socket, plugin registry, and kubelet pods. Optional host NFS mount configuration files/directories are mounted when `propagateHostMountOptions` is true. Mount state persists on the node through kubelet and host mount namespaces.

## Dependencies And Integration Points
Depends on kubelet directory layout, privileged mount capability, service account existence, `CSIDriver`, and workload PVCs referencing the NFS StorageClass.

## Risks And Edge Cases
This template is byte-identical across v4.7.0, v4.8.0, and v4.9.0 here. Wrong host paths or missing host networking break registration and mount continuity. Privileged hostPath access should be treated as node-level trust.

## Test Signals
DaemonSet rollout, registrar liveness, `CSINode` plugin entries, workload pod NFS mounts, and mount option propagation checks.
