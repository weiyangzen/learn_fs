<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-driver.yaml

- Purpose: current static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-driver.yaml -->
