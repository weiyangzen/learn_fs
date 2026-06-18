# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes for v2.0.0.

Important APIs/types/functions: `storage.k8s.io/v1beta1` `CSIDriver` named `nfs.csi.k8s.io`; fields `attachRequired: false`, `volumeLifecycleModes: Persistent`, and `podInfoOnMount: true`.

Control flow: Static manifest, no Helm gates. The object tells Kubernetes the driver does not require attach/detach and only handles persistent volumes.

State and persistence: Persists cluster-scoped driver metadata used by kubelet and storage controllers.

Dependencies and integration points: Name must match `--drivername` arguments in controller/node pods and StorageClass provisioner fields.

Risks: `v1beta1` CSIDriver is unsupported on newer Kubernetes releases. Static driver name cannot be customized in this version. Test signals: server-side dry-run against supported clusters and CSI node registration smoke.
