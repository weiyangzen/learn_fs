# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/values.yaml

## Purpose
This values file configures the v4.3.0 NFS CSI chart, introducing snapshot-related image and controller defaults compared with v4.2.0.

## Important APIs, Types, and Functions
Defaults include nfsplugin `v4.3.0`, csi-provisioner `v3.5.0`, csi-snapshotter and snapshot-controller `v6.2.2`, livenessprobe `v2.10.0`, node-driver-registrar `v2.8.0`, driver name `nfs.csi.k8s.io`, controller default delete policy, and `externalSnapshotter.enabled: true`.

## Control Flow, State, and Persistence
Values control service account/RBAC creation, snapshot CRD/controller rendering, optional snapshot sidecar rendering, controller/node scheduling, health ports, resources, and image pull secrets. There are still no built-in StorageClass or VolumeSnapshotClass values in this file.

## Dependencies and Integration Points
The file binds v4.3.0 templates to CSI sidecar versions and snapshot-controller resources. It assumes standard kubelet paths and registry.k8s.io images.

## Risks and Test Signals
Risks include snapshot stack enabled by default, no CRD sub-gate, service account naming sensitivity, and no resizer/storageclass config. Signals are install smoke tests, snapshot CRD/controller readiness, PVC provisioning/deletion, node registration, and feature-off rendering with `externalSnapshotter.enabled=false`.
