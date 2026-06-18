# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `CSIDriver` object.

Important APIs and types: creates `storage.k8s.io/v1` `CSIDriver` named `.Values.driver.name`, sets `attachRequired: false`, always enables `Persistent` lifecycle mode, conditionally enables `Ephemeral`, and conditionally sets `fsGroupPolicy: File`.

Control flow: Kubernetes storage components read this object to understand attach behavior, inline volume support, and fsGroup handling.

State and persistence: creates a cluster-scoped CSIDriver object.

Dependencies and integration: must match the `--drivername` used by controller and node plugin pods and any StorageClass/SnapshotClass templates.

Risks: driver name mismatch breaks provisioning and node registration. Enabling inline volume or fsGroup policy depends on cluster version support and driver implementation behavior.

Test signals: `kubectl get csidriver`, successful pod inline volumes, PVC mount behavior, and fsGroup E2E.
