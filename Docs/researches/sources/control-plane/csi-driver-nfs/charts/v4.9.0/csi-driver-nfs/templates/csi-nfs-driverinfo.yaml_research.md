# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
Declares the v4.9.0 CSI NFS driver to Kubernetes.

## Important APIs, Types, And Functions
Emits `storage.k8s.io/v1 CSIDriver` with driver name from `.Values.driver.name`, `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle mode, and optional `fsGroupPolicy: File`.

## Control Flow
Rendered unconditionally. Feature flags determine optional `volumeLifecycleModes` and FSGroup behavior in the final object.

## State And Persistence
The cluster-scoped object persists capability metadata used by kubelet and scheduler. It does not persist volume contents.

## Dependencies And Integration Points
Must match controller/node `--drivername`, node-driver-registrar registration, and StorageClass provisioner. Enables Kubernetes to skip attach operations for NFS.

## Risks And Edge Cases
Byte-identical to earlier versions in this set. Driver-name drift or unsupported feature flags can break provisioning or pod volume admission.

## Test Signals
Check rendered `CSIDriver`, `CSINode` plugin registration, and a PVC-backed pod that mounts without attach.
