# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template creates the v4.3.0 `CSIDriver` declaration for the NFS CSI driver.

## Important APIs, Types, and Functions
It emits a `storage.k8s.io/v1` `CSIDriver` named from `.Values.driver.name`, with `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle mode, and optional `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The manifest is unconditional and cluster-scoped. It influences Kubernetes storage handling while the node DaemonSet supplies actual kubelet plugin registration.

## Dependencies and Integration Points
The name must match controller/node args and StorageClass provisioner names. This content is identical across all listed chart versions.

## Risks and Test Signals
Risks are driver-name drift and insufficient testing of optional lifecycle/fsGroup behavior. Signals are CSIDriver presence, CSINode registration, PVC mount tests, and fsGroup workload checks.
