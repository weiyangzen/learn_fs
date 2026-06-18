# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
Optionally renders an NFS StorageClass for the v4.8.0 chart.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 StorageClass`, labels, `.Values.storageClass.annotations`, parameters, reclaim policy, volume binding mode, and mount options. The provisioner remains hard-coded as `nfs.csi.k8s.io` in this version.

## Control Flow
When `storageClass.create` is true, Helm emits one StorageClass and includes an annotations block even if no annotations are provided. PVCs selecting the class trigger the controller provisioner.

## State And Persistence
The StorageClass is cluster-scoped configuration that persists provisioning defaults. Parameters flow into PV creation and can reference provisioner secrets for mount options during delete.

## Dependencies And Integration Points
Depends on the NFS CSI provisioner deployment and driver name matching the hard-coded provisioner. Values include example server/share/subdirectory parameters and optional default-class annotation.

## Risks And Edge Cases
The annotations block is new compared with v4.7.0, but the provisioner remains hard-coded, so custom `driver.name` can still diverge. Empty annotations should be checked in rendered YAML for valid formatting.

## Test Signals
`helm template` with and without annotations, StorageClass creation, PVC dynamic provisioning, and default-class behavior if the annotation is set.
