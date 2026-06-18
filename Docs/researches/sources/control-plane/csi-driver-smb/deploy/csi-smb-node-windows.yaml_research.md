<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows.yaml

- Purpose: current Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.16.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0, gcr.io/k8s-staging-sig-storage/smbplugin:canary. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows.yaml -->
