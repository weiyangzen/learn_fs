# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the v4.13.2 node DaemonSet for kubelet driver registration and node-side NFS volume mount handling.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with liveness probe, `node-driver-registrar`, and privileged `nfs` containers. Values configure update `maxUnavailable`, DNS policy, node service account, priority class, scheduling, resources, registrar health endpoint, kubelet directories, and optional host NFS mount configuration propagation.

## Control Flow, State, and Persistence
The DaemonSet uses host networking and host paths for `plugins/csi-nfsplugin`, `pods`, and `plugins_registry`. The registrar advertises the CSI socket path to kubelet, while the NFS driver performs mounts with bidirectional propagation into pod volume directories. v4.13.2 correctly reads `.Values.node.dnsPolicy`, unlike v4.13.1.

## Dependencies and Integration Points
It depends on kubelet path conventions, node service account creation, the `CSIDriver` object, and matching driver names. It also integrates with host-level NFS configuration if `feature.propagateHostMountOptions` is true.

## Risks and Test Signals
Risks include privileged host mounts, socket registration failures when `kubeletDir` is wrong, DNS regressions under host networking, and accidental host NFS config mutation/visibility. Signals are DaemonSet availability, registrar HTTP health, CSINode driver entries, mount/unmount workloads, kubelet plugin logs, and comparing node DNS override rendering with v4.13.1.
