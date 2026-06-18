<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.14.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-driver.yaml -->
