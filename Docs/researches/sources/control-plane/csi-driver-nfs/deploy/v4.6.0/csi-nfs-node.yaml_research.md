# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-node.yaml

## Purpose
This manifest deploys the v4.6.0 NFS CSI node DaemonSet. It updates sidecars and hardens capability sets while keeping the same kubelet plugin registration path and NFS mount responsibilities.

## Important APIs, Types, and Functions
The DaemonSet uses `livenessprobe:v2.12.0`, `csi-node-driver-registrar:v2.10.0`, and `nfsplugin:v4.6.0`. The liveness sidecar switches to `--http-endpoint=localhost:29653`; the NFS container's liveness probe also targets `host: localhost` and numeric port 29653. Sidecar containers drop all capabilities, while the NFS container runs privileged, adds `SYS_ADMIN`, drops all other capabilities, and mounts `/var/lib/kubelet/pods` bidirectionally plus `/var/lib/kubelet/plugins/csi-nfsplugin` and `/var/lib/kubelet/plugins_registry` host paths.

## Control Flow, State, and Persistence
One pod per Linux node creates a hostPath CSI socket, registers it with kubelet, and handles node publish/unpublish calls. Rolling update limits disruption to one unavailable node plugin. Persistent node effects are CSI socket files, registration data, and kubelet-managed pod volume mounts.

## Dependencies and Integration Points
The DaemonSet depends on kubelet host paths, Linux mount propagation, host networking, `csi-nfs-node-sa`, the `CSIDriver`, and the controller deployment for provisioned volume metadata. It integrates with kubelet through the registrar sidecar and with the liveness sidecar through the shared CSI socket.

## Risks and Test Signals
Risks include capability hardening breaking mount operations, numeric localhost health probes not matching the process listener, registrar version changes, and stale plugin registration files. Test signals are DaemonSet readiness on all Linux nodes, healthy 29653 probes, `CSINode` entries for `nfs.csi.k8s.io`, successful workload mounts after a rolling update, and no mount propagation warnings.
