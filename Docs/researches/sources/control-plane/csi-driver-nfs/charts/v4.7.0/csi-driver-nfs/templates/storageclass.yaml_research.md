# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
Optionally renders an example NFS `StorageClass` for the v4.7.0 chart when `.Values.storageClass.create` is true.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 StorageClass`, `.Values.storageClass.name`, `.Values.storageClass.parameters`, `reclaimPolicy`, `volumeBindingMode`, and `mountOptions`. The provisioner is hard-coded to `nfs.csi.k8s.io` in this version.

## Control Flow
If enabled, Helm emits one StorageClass with chart labels, optional parameters, reclaim policy, binding mode, and mount options. Workload PVCs then trigger csi-provisioner to create NFS-backed PVs.

## State And Persistence
The StorageClass is cluster-scoped configuration. It does not hold data, but its parameters are copied into dynamic provisioning decisions and influence PV lifecycle.

## Dependencies And Integration Points
Provisioner name must match the driver name. Parameters such as NFS server, share, subdirectory, mount permissions, and optional provisioner secret references are documented in values.

## Risks And Edge Cases
Hard-coding the provisioner can drift if `.Values.driver.name` is changed. There is no annotations block in v4.7.0, so marking it default requires external patching.

## Test Signals
Render with `storageClass.create=true`, create a PVC using the class, and verify PV creation, mount options, and reclaim behavior.
