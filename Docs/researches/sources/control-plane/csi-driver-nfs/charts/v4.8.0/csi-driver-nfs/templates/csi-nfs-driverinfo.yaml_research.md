# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
Declares the v4.8.0 chart's CSI NFS driver metadata to Kubernetes.

## Important APIs, Types, And Functions
Emits `storage.k8s.io/v1 CSIDriver` using `.Values.driver.name`, `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle mode, and optional `fsGroupPolicy: File`.

## Control Flow
Always rendered by Helm. Feature flags add optional lines to the `CSIDriver` spec before Kubernetes consumes the object for CSI scheduling and kubelet behavior.

## State And Persistence
The cluster-scoped `CSIDriver` object persists driver capabilities. It does not manage NFS data directly.

## Dependencies And Integration Points
Must align with the driver name in controller/node plugin args and StorageClass provisioner. Kubelet uses it with the node-driver-registrar socket registration.

## Risks And Edge Cases
This file is byte-identical to v4.7.0 and v4.9.0 in this set. A custom driver name must be propagated everywhere or dynamic provisioning and registration fail.

## Test Signals
`kubectl get csidriver`, rendered spec inspection, and successful PVC mount without an attach operation.
