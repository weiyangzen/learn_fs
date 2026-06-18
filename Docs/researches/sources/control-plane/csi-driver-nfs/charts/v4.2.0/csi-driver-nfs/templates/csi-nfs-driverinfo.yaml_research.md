# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template registers the v4.2.0 NFS CSI driver as a Kubernetes `CSIDriver`.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `CSIDriver` named from `.Values.driver.name`, with `attachRequired: false`, persistent lifecycle mode, optional inline ephemeral mode, and optional `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
It renders unconditionally and persists as cluster-scoped metadata used by storage scheduling and kubelet interactions. Runtime endpoint registration still comes from the node DaemonSet.

## Dependencies and Integration Points
The driver name must match controller/node `--drivername` and any external StorageClass provisioner field. This same template content is reused across all listed chart versions.

## Risks and Test Signals
Risks are name mismatch, enabling inline mode without node coverage, and changing fsGroup semantics. Signals are CSIDriver presence, CSINode registration, PVC mount success, and fsGroup workload checks.
