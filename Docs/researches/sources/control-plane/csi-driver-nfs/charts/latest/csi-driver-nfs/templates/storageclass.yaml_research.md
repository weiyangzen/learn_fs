# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/storageclass.yaml

Purpose: Optional StorageClass rendering for one legacy `storageClass` object plus a newer `storageClasses` list for multiple NFS classes.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass`; Helm `with`, `range`, `hasKey`, defaults, `.Values.driver.name`, `.Values.storageClass.*`, and `.Values.storageClasses`.

Control flow: First gate renders the single class when `storageClass.create` is true. A second gate ranges over `storageClasses`, rendering each with per-entry annotations, parameters, reclaim policy, binding mode, mount options, and configurable `allowVolumeExpansion`.

State and persistence: Persists cluster storage provisioning policy. Runtime PV/PVC state is created later by the external provisioner.

Dependencies and integration points: Consumed by PVCs and `csi-provisioner`; parameters such as `server`, `share`, `subDir`, and provisioner secrets drive NFS volume creation and deletion behavior.

Risks: Multiple default StorageClasses can cause ambiguous provisioning. Missing server/share parameters makes the class unusable. Test signals: template both modes and run server-side dry-run plus a PVC provisioning smoke test.
