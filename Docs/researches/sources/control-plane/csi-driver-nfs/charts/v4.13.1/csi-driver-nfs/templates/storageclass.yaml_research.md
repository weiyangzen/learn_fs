# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template optionally creates one default-style NFS CSI `StorageClass` and/or multiple additional storage classes from `storageClasses`. It exposes NFS server/share parameters and mount options to Kubernetes dynamic provisioning.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `StorageClass` objects. Important fields are `metadata.name`, chart labels, optional annotations, `provisioner: {{ .Values.driver.name }}`, `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and `mountOptions`. The multi-class loop supports per-entry defaults for reclaim policy, binding mode, and expansion.

## Control Flow, State, and Persistence
The single class is gated by `storageClass.create`; the multi-class list is rendered whenever `.Values.storageClasses` is set. StorageClasses are cluster-scoped and influence future PVC provisioning. Persistent data is created on the configured NFS server/share/subdirectory by the CSI controller.

## Dependencies and Integration Points
The provisioner name must match the CSIDriver and `nfsplugin` driver name. Parameters integrate with the CSI NFS driver (`server`, `share`, `subDir`, `mountPermissions`, and provisioner secret fields for delete-time mount options). Mount options are used by kubelet during NFS mounts.

## Risks and Test Signals
In v4.13.1 the single-class template always emits an `annotations:` key even when no annotations are configured, producing an empty map. Other risks include missing NFS parameters, invalid mount options, multiple default classes, and relying on expansion without testing the resizer sidecar. Signals are `helm template` with single and multi-class values, server-side dry-run, PVC provisioning, mount option verification in pods, expansion tests, and reclaim-policy deletion/retention checks.
