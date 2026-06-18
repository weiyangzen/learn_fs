<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb-inline-volume.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb-inline-volume.yaml

- Purpose: pod example using an inline CSI volume with direct SMB `source`, secret name, and mount options instead of a PVC.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `Pod`; notable images `mcr.microsoft.com/mirror/docker/library/nginx:1.23`; names include `nginx-smb-inline-volume, nginx-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Inline volume settings couple credentials and source to the pod spec; secret namespace defaults to the pod namespace; unsuitable for reusable storage policy.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb-inline-volume.yaml -->
