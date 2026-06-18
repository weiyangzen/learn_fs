# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/storageclass.yaml

Purpose: v4.10.0 optional single StorageClass template.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass`; values `.Values.storageClass.create`, `.name`, `.annotations`, `.parameters`, `.reclaimPolicy`, `.volumeBindingMode`, `.mountOptions`, and `.Values.driver.name`.

Control flow: Renders only when `storageClass.create` is true. It always sets `allowVolumeExpansion: true` and includes optional parameters and mountOptions.

State and persistence: Cluster-scoped provisioning policy for PVCs.

Dependencies and integration points: External provisioner and resizer; parameters identify NFS server/share/subDir and optional provisioner secrets.

Risks: Empty annotations block can render even when no annotations are provided. Missing parameters make provisioning fail. Test signals: render with sample NFS parameters and create/resize a PVC.
