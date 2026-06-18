<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node-windows.yaml

- Purpose: v0.2.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/k8s/csi/smb-csi:v0.2.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node-windows.yaml -->
