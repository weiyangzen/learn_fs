<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/statefulset.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/windows/statefulset.yaml

- Purpose: Windows workload example consuming an SMB PVC with a Server Core container and PowerShell write loop.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `StatefulSet`; notable images `mcr.microsoft.com/windows/servercore:ltsc2022`; names include `busybox-smb, persistent-storage`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Requires Windows node scheduling, compatible image/host version, and SMB subPath handling; shell loop is a smoke test, not production workload logic.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/statefulset.yaml -->
