# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.3.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false` and `spec.podInfoOnMount: true`. Unlike later chart versions, it does not render `spec.volumeLifecycleModes`, does not advertise inline `Ephemeral` volumes, and does not expose custom CSIDriver labels.

## Control Flow
Rendering is unconditional and has no feature-gated branches in this older template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver` and on node-driver-registrar publishing the same driver name. Inline ephemeral volume support is not declared by this template version.

## Risks And Test Signals
Risk centers on driver-name drift and assumptions that this older chart supports inline ephemeral CSI volumes. Validate with `helm template`, `kubectl get csidriver`, and a smoke PVC that checks kubelet registration.
