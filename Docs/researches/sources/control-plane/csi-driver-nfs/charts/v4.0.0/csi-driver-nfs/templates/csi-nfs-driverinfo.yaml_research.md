# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v4.0.0 CSIDriver manifest.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; `.Values.driver.name`, `.Values.feature.enableInlineVolume`, `.Values.feature.enableFSGroupPolicy`.

Control flow: Emits persistent lifecycle mode, optional ephemeral lifecycle mode, optional `fsGroupPolicy: File`, and `attachRequired: false`.

State and persistence: Cluster-scoped driver capability state.

Dependencies and integration points: Must match driver flags and StorageClass provisioner references.

Risks: Default FSGroup changed to enabled in v4 values, which can change volume ownership handling. Test signals: dry-run, CSIDriver inspection, fsGroup workload test.
