# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template renders optional NFS CSI `StorageClass` resources for v4.13.2. It supports either a single configured class or a list of multiple classes.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `StorageClass` with chart labels, optional annotations, `provisioner` from the CSI driver name, optional driver parameters, reclaim policy, volume binding mode, expansion support, and mount options. The `storageClasses` loop provides per-class defaults and per-class `allowVolumeExpansion` handling.

## Control Flow, State, and Persistence
The single class renders only when `storageClass.create` is true. Multiple class entries render whenever `.Values.storageClasses` is set. StorageClasses persist cluster-wide and control future PVC provisioning onto the target NFS server/share.

## Dependencies and Integration Points
The provisioner must match the NFS CSI driver. Parameters feed the external provisioner and NFS plugin, including `server`, `share`, optional `subDir`, mount permissions, and secret references for delete-time mount options.

## Risks and Test Signals
v4.13.2 fixes v4.13.1's empty single-class `annotations:` emission by placing the key inside the `with` block. Remaining risks include invalid server/share values, bad NFS mount options, multiple default annotations, and untested expansion. Signals are rendered YAML with no empty annotation block, server-side dry-run, PVC bind/mount/delete, multi-class provisioning, and expansion tests.
