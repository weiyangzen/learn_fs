# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/values.yaml

## Purpose
This file is the default configuration contract for chart version 4.12.0. It controls image repositories/tags, service accounts, RBAC, driver behavior, scheduling, resources, optional snapshot controller/CRDs, and optional generated storage/snapshot classes.

## APIs, Control Flow, and State
Defaults use the NFS driver image tag `v4.12.0`, sidecars such as csi-provisioner `v5.3.0`, csi-resizer `v1.14.0`, csi-snapshotter and snapshot-controller `v8.3.0`, livenessprobe `v2.17.0`, and registrar `v2.15.0`. It enables service account and RBAC creation, sets `driver.name` to `nfs.csi.k8s.io`, enables FSGroup policy, disables inline volume, and configures kubeletDir. Controller defaults include one replica, host-network DNS, snapshotter enabled, tar snapshots disabled, delete-on-delete, critical priority, broad control-plane tolerations, and resource requests. Node defaults tolerate all taints and run critical priority. External snapshot controller and CRDs default off except CRD creation is true when the controller is enabled.

## Dependencies and Integration Points
All chart templates read these values. StorageClass and VolumeSnapshotClass examples document expected user overrides.

## Risks and Test Signals
Default `storageClass.create: false` means installing the chart alone does not create usable classes. Privileged host-mount defaults require trusted nodes. Test by rendering default and enabled feature profiles, checking image availability, and running PVC, resize, and snapshot workflows.
