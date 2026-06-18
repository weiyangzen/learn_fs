<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/deployment.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/deployment.yaml

- Purpose: Linux Deployment example with an inline PVC definition and a pod that writes timestamps into `/mnt/smb/outfile`.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `PersistentVolumeClaim, Deployment`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.19.5`; names include `pvc-smb, deployment-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Continuous write loop can grow data indefinitely; deployment assumes the `smb` StorageClass and credentials already exist.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/deployment.yaml -->
