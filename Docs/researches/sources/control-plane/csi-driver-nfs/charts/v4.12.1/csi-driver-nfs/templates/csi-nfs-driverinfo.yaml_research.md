# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template registers the CSI NFS driver with Kubernetes as a `CSIDriver` object for chart 4.12.1.

## APIs, Control Flow, and State
It renders `storage.k8s.io/v1`, kind `CSIDriver`, named by `driver.name`. It sets `attachRequired: false`, always supports persistent lifecycle, optionally supports ephemeral inline lifecycle, and conditionally sets `fsGroupPolicy: File`. It stores no runtime state beyond the cluster API object.

## Dependencies and Integration Points
The object must align with controller/node `--drivername` and StorageClass `provisioner`. Kubelet and Kubernetes storage controllers use it to understand attach, lifecycle, and FSGroup behavior.

## Risks and Test Signals
Mismatched driver names are a hard integration failure. Inline volume and FSGroup settings affect pod admission and mount ownership semantics. Test by rendering value permutations and checking actual CSIDriver state after install.
