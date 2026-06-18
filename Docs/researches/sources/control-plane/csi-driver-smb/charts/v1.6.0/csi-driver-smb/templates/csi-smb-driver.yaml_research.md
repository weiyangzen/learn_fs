<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-driver.yaml

- Purpose: Helm template for the v1.6.0 `CSIDriver` object named from `.Values.driver.name`, normally `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` and sets `attachRequired: false` because SMB volumes are network filesystem mounts and do not need a Kubernetes attach/detach controller.
- Control flow: this object is applied before or alongside controller/node manifests so Kubernetes knows driver-level capabilities while external provisioner and kubelet registration handle volume lifecycle operations.
- State and persistence behavior: the object persists only CSI driver metadata in the Kubernetes API; it stores no SMB credentials, mount state, or volume data.
- Dependencies/integration points: must match the driver name passed to controller/node pods and the provisioner name used in StorageClasses, PVs, inline volumes, and examples.
- Risks: a name mismatch makes PVC provisioning or pod mounts fail; clusters too old for `storage.k8s.io/v1` need historical manifests instead.
- Test signals: server-side dry-run and `kubectl get csidriver smb.csi.k8s.io`; successful PVC provisioning confirms the object lines up with the running plugin.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
