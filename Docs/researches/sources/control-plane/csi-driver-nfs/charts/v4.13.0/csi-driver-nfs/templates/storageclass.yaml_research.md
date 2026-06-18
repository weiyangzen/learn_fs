# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template optionally creates one or more NFS `StorageClass` objects for chart 4.13.0.

## APIs, Control Flow, and State
The single-class and multi-class rendering paths are unchanged from 4.12.x. Classes use `driver.name` as provisioner, user parameters for NFS endpoint/path behavior, reclaim policy, volume binding mode, expansion controls, annotations, labels, and mount options. Multi-class entries default reclaim policy to `Delete`, binding mode to `Immediate`, and expansion to true.

## Dependencies and Integration Points
Provisioner sidecar version is newer in 4.13.0, but the class contract remains the same. NFS driver runtime consumes server/share/subDir/mount options and optional provisioner secrets.

## Risks and Test Signals
Provisioning failures typically surface after PVC creation, so class examples should be tested against real NFS endpoints. Test rendering, PVC bind, mount options, expansion, and reclaim behavior.
