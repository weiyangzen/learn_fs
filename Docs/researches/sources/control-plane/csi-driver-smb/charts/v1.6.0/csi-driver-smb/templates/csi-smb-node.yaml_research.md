<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node.yaml

- Purpose: Helm template for the v1.6.0 Linux node DaemonSet. It installs the SMB CSI node service on every Linux node and exposes the CSI socket to kubelet registration.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.linux.enabled` is true. Key values are `.Values.linux.kubelet`, `.Values.node.maxUnavailable`, `.Values.feature.enableGetVolumeStats`, `.Values.driver.name`, image tags, tolerations, affinity, and node selectors.
- Control flow: Kubernetes schedules one pod per Linux node; liveness-probe monitors `/csi/csi.sock`, node-driver-registrar registers the socket under `${kubelet}/plugins_registry`, and the `smb` container starts with node ID from `spec.nodeName` and metrics/stat flags.
- State and persistence behavior: hostPath volumes create/use `${kubelet}/plugins/<driver>`, `${kubelet}/plugins_registry`, and the kubelet root with bidirectional mount propagation. SMB volume content persists remotely; local state is mounts and registration sockets.
- Dependencies/integration points: kubelet CSI plugin registry, Linux mount propagation, privileged SMB plugin container, CSI liveness and registrar sidecars, node ServiceAccount, and RBAC permitting node secret reads when used with secrets.
- Risks: privileged hostPath mount access is required; wrong kubelet path or driver name breaks registration; mount propagation must be bidirectional; enabling stats may add filesystem stat load on nodes.
- Test signals: `helm template` rendering, DaemonSet rollout, registrar health, kubelet `CSINode` driver entry, and a Linux pod mounting an SMB PVC are the main validation signals.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node.yaml -->
