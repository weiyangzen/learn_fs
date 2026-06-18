<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/csi-proxy.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/windows/csi-proxy.yaml

- Purpose: Windows CSI proxy HostProcess DaemonSet example used by Windows SMB node plugins that still use CSI proxy APIs.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `DaemonSet`; notable images `ghcr.io/kubernetes-sigs/sig-windows/csi-proxy:v1.1.2`; names include `csi-proxy`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Runs as `NT AUTHORITY\SYSTEM` with host networking; CSI proxy version must match driver expectations and Windows support matrix.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/csi-proxy.yaml -->
