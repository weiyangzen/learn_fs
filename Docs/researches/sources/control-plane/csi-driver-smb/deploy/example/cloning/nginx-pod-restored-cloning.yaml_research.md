<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/cloning/nginx-pod-restored-cloning.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/cloning/nginx-pod-restored-cloning.yaml

- Purpose: pod workload example mounting an SMB PVC and continuously appending timestamps to validate read/write behavior.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `Pod`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.17.3-alpine`; names include `nginx-smb-restored-cloning`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Continuous write loop is only a smoke test and can grow remote data; it assumes PVC, StorageClass, and credentials are already present.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/cloning/nginx-pod-restored-cloning.yaml -->
