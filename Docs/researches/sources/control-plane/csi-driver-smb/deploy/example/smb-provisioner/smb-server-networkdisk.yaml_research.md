<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-networkdisk.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-networkdisk.yaml

- Purpose: example SMB server backed by a PVC named `pvc-networkdisk-smbshare`, demonstrating a share hosted on another storage provider.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `Service, PersistentVolumeClaim, Deployment`; notable images `dperson/samba`; names include `smb-server, pvc-networkdisk-smbshare, smbcreds, data-volume`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Builds an SMB service on top of another persistent disk, so failures/debugging span two storage layers; demo credentials and image are not production controls.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-networkdisk.yaml -->
