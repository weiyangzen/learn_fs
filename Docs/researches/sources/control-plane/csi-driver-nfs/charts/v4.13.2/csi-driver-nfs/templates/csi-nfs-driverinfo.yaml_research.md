# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template creates the `CSIDriver` object that advertises the NFS CSI driver to Kubernetes for v4.13.2 installs.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, optional `Ephemeral`, and optional `fsGroupPolicy: File`. The object name comes from `.Values.driver.name`.

## Control Flow, State, and Persistence
It renders unconditionally and persists as cluster-scoped storage driver metadata. Kubernetes uses it when scheduling and mounting CSI volumes; kubelet registration confirms the runtime endpoint separately through the node DaemonSet.

## Dependencies and Integration Points
The name must match controller and node `--drivername` args plus StorageClass `provisioner`. This file is byte-identical across the listed chart versions.

## Risks and Test Signals
Risks are inconsistent driver names, untested inline ephemeral mode, and unexpected permission semantics from `fsGroupPolicy`. Signals include CSIDriver discovery, CSINode entries, successful PVC mounts, and workload tests that set `fsGroup`.
