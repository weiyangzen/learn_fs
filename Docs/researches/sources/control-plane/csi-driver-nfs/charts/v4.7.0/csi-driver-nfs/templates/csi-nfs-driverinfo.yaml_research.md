# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
Declares the CSI NFS driver to Kubernetes through a `CSIDriver` object for the v4.7.0 chart.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 CSIDriver`, `.Values.driver.name`, `.Values.feature.enableInlineVolume`, and `.Values.feature.enableFSGroupPolicy`. The spec sets `attachRequired: false`, includes `Persistent` lifecycle mode, optionally includes `Ephemeral`, and optionally sets `fsGroupPolicy: File`.

## Control Flow
Helm always renders this object. Feature values determine whether inline CSI volumes and FSGroup policy are advertised to kubelet and admission.

## State And Persistence
The object is cluster-scoped Kubernetes configuration. It persists the driver's attach behavior and volume lifecycle capabilities, but it does not store volume data.

## Dependencies And Integration Points
The driver name must match the NFS plugin `--drivername` flag and StorageClass provisioner name. Kubelet, scheduler, and CSI sidecars use the `CSIDriver` object to understand whether attach operations are required and how FSGroup should be applied.

## Risks And Edge Cases
Mismatched driver names break provisioning and node registration. Enabling inline volumes or FSGroup policy on unsupported clusters or incompatible driver behavior can cause scheduling or mount failures.

## Test Signals
Validate with `kubectl get csidriver nfs.csi.k8s.io` after install, plus pod mount tests that confirm no attach phase is required.
