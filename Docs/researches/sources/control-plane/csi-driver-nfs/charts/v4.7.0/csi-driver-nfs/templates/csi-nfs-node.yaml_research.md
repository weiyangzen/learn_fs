# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
Renders the v4.7.0 node `DaemonSet` for the CSI NFS driver. It runs one pod per eligible Linux node to register the CSI socket with kubelet, serve node-stage/node-publish operations, and expose liveness health.

## Important APIs, Types, And Functions
Uses `apps/v1 DaemonSet`, `node-driver-registrar`, `liveness-probe`, and privileged `nfs` containers. Key values include `.Values.node.*`, `.Values.image.*`, `.Values.kubeletDir`, `.Values.feature.propagateHostMountOptions`, and the driver name and mount permissions.

## Control Flow
Helm renders scheduling, resources, and optional image pull secrets. Kubelet starts the pod on nodes, the registrar points kubelet at `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`, the NFS plugin listens on `unix:///csi/csi.sock`, and liveness probes both the sidecar and plugin endpoint.

## State And Persistence
The DaemonSet uses host paths for the CSI plugin socket, plugin registry, kubelet pod mount directory, and optionally `/etc/nfsmount.conf` plus `/etc/nfsmount.conf.d`. Volume mount propagation is bidirectional for kubelet pod mounts.

## Dependencies And Integration Points
Requires kubelet plugin directories, Linux nodes, privileged mount capabilities, service account/RBAC, and the same driver name as the `CSIDriver` and StorageClass. Host networking is required because losing the original NFS connection can break mounts.

## Risks And Edge Cases
Privileged hostPath access is broad and sensitive. Wrong `kubeletDir` breaks registration. Optional propagation of host NFS mount config can create host coupling. The template uses controller DNS policy for node pods, which is intentional in this chart but ties node networking to controller defaults.

## Test Signals
Signals include `CSINode` entries, node-driver-registrar liveness success, socket creation under kubelet plugins, pod volume mounts, and host mount propagation behavior during workload pod restarts.
