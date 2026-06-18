# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This DaemonSet template installs the 4.13.0 node-side NFS CSI service and kubelet registrar.

## APIs, Control Flow, and State
The base node flow matches 4.12.x: host networking, Linux node selection, node service account, critical priority, seccomp, liveness probe, registrar, privileged NFS server, hostPath CSI socket, kubelet pod directory, and plugin registry. New in 4.13.0, `nodeDriverRegistrar.livenessProbe.enabled` can add `--http-endpoint`, a healthz port, and a Kubernetes liveness probe to the registrar container. Image repository handling also prefixes `image.baseRepo` when a repository starts with `/`.

## Dependencies and Integration Points
The optional registrar health settings are defined in `values.yaml`. Runtime still depends on kubelet plugin paths, CSIDriver name alignment, and bidirectional mount propagation for pod volumes.

## Risks and Test Signals
Registrar liveness can improve recovery but may restart a registrar if health port settings are wrong. Test both disabled default and enabled health probe rendering, kubelet registration after rollout, pod volume mounts, and node pod liveness behavior.
