# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: Registers the v3.0.0 CSI NFS driver using the GA CSIDriver API.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; values `.Values.driver.name` and `.Values.feature.enableFSGroupPolicy`.

Control flow: Static object with optional `fsGroupPolicy: File` when enabled. It declares `attachRequired: false` and persistent lifecycle mode.

State and persistence: Cluster-scoped CSIDriver metadata governs kubelet/storage-controller handling.

Dependencies and integration points: Must match controller/node `--drivername` and StorageClass provisioner name.

Risks: FSGroup behavior can change ownership/mode semantics for mounted volumes; default v3.0.0 values disable it. Test signals: server-side dry-run and pod mount tests with/without fsGroup.
