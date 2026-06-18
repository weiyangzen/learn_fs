# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
Optionally renders a v4.9.0 NFS StorageClass.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 StorageClass`, labels, optional annotations, values-driven parameters, reclaim policy, volume binding mode, mount options, and a provisioner value set to `.Values.driver.name`.

## Control Flow
When `storageClass.create` is true, Helm emits the StorageClass. Compared with v4.8.0, the provisioner now follows the configured driver name, so custom driver names can be reflected consistently.

## State And Persistence
The StorageClass persists cluster-scoped provisioning defaults. Its parameters influence dynamically created PVs and deletion behavior.

## Dependencies And Integration Points
Integrates with the csi-provisioner deployment, `CSIDriver`, driver name values, and NFS server/share parameters supplied by the user.

## Risks And Edge Cases
Annotations block rendering should be checked for empty values. Changing driver names during upgrades can orphan old StorageClasses or PVC expectations. Parameters remain opaque to Kubernetes and are validated mostly by the CSI driver.

## Test Signals
Render with custom `driver.name`, annotations, and mount options; create a PVC using the class; verify PV provisioner name and NFS mount behavior.
