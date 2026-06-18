# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template renders the 4.13.0 `CSIDriver` registration for the NFS CSI driver.

## APIs, Control Flow, and State
It creates `storage.k8s.io/v1` `CSIDriver`, named from `driver.name`, with `attachRequired: false`, persistent lifecycle, optional ephemeral lifecycle, and optional `fsGroupPolicy: File`. It stores static cluster driver capability state.

## Dependencies and Integration Points
The object ties Kubernetes driver discovery to controller/node `--drivername` and StorageClass provisioner names. It is unchanged from 4.12.x and remains central to kubelet volume handling.

## Risks and Test Signals
Driver-name drift breaks provisioning and mounting. FSGroup and inline volume flags should be tested with workloads that rely on ownership changes or CSI ephemeral volumes. Validate rendered YAML and installed `CSIDriver`.
