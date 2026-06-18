<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node.yaml

- Purpose: v0.2.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.2.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node.yaml -->
