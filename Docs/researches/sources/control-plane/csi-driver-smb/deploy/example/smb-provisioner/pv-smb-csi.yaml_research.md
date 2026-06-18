<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/pv-smb-csi.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/pv-smb-csi.yaml

- Purpose: static PersistentVolume example for an SMB share, including CSI volumeHandle/source and node-stage secret reference.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `PersistentVolume`; notable images `none`; names include `pv-smb, smbcreds`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: `volumeHandle` must be globally unique; static PVs rely on correct secret namespace and manual lifecycle; mount option mistakes affect all bound pods.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/pv-smb-csi.yaml -->
