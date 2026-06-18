# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.19.1`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and `spec.volumeLifecycleModes`. It always advertises `Persistent` volumes and conditionally adds `Ephemeral` when `.Values.feature.enableInlineVolume` is true.

## Control Flow
Rendering is unconditional. The inline volume mode is the only feature branch in this template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver`, on node-driver-registrar publishing the same driver name, and on inline-volume RBAC matching the advertised `Ephemeral` lifecycle mode when enabled.

## Risks And Test Signals
Risk centers on name drift and enabling ephemeral mode without matching node secret access. Validate with `helm template`, `kubectl get csidriver`, rendered `volumeLifecycleModes`, and a smoke PVC or inline CSI volume that checks kubelet registration.
