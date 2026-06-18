# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template optionally creates one primary NFS `StorageClass` and any additional classes listed in `storageClasses`.

## APIs, Control Flow, and State
When `storageClass.create` is true it emits one `storage.k8s.io/v1` `StorageClass` named by `storageClass.name`, with labels, annotations, `provisioner: driver.name`, parameter map, reclaim policy, binding mode, `allowVolumeExpansion: true`, and optional mount options. When `storageClasses` is set it ranges over the list and emits multiple classes with per-entry names, annotations, parameters, reclaim policy defaulting to `Delete`, binding mode defaulting to `Immediate`, and `allowVolumeExpansion` defaulting true unless explicitly provided.

## Dependencies and Integration Points
Parameters such as NFS server, share, subDir, mount permissions, and provisioner secrets are consumed by the CSI provisioner and driver. Generated classes must match the CSIDriver/provisioner name.

## Risks and Test Signals
Invalid NFS server/share settings produce PVC provisioning failures. Multiple default-class annotations can conflict. Test by rendering both single and multiple class modes, creating PVCs, expanding PVCs, validating reclaim policy behavior, and checking mount options.
