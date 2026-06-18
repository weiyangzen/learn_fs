<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/statefulset-nonroot.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/statefulset-nonroot.yaml

- Purpose: Linux StatefulSet example proving SMB mounts can be consumed by a non-root pod security context using fsGroup/user/group 10001.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `StatefulSet`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.19.5`; names include `statefulset-smb-nonroot, persistent-storage`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Non-root access depends on mount uid/gid/permission options in the StorageClass; write loop grows remote data.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/statefulset-nonroot.yaml -->
