# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/rbac-csi-smb.yaml

## Purpose
This modern `v1.18.0` RBAC template provisions authorization for both the SMB CSI controller and node paths. It covers provisioning, expansion, leader election, controller secret lookup, and optional node secret lookup for inline ephemeral volumes.

## Important APIs, Types, And Functions
The template can render two `ServiceAccount` objects (`.Values.serviceAccount.controller` and `.Values.serviceAccount.node`), an external provisioner `ClusterRole`/`ClusterRoleBinding`, an external resizer `ClusterRole`/`ClusterRoleBinding`, and a conditional node secret role/binding when `.Values.feature.enableInlineVolume` is true. Helm gates are `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Values.feature.enableInlineVolume`.

## Control Flow
Service accounts are emitted first when enabled. RBAC creation then binds the controller service account to provisioning and resizing permissions. The inline-volume block adds `secrets get` for the node service account only when ephemeral volume support is advertised by the CSIDriver.

## State And Persistence Behavior
These cluster-scoped roles and bindings are persistent security state. They do not hold SMB data, but incorrect role updates can immediately break provisioning, expansion, or inline volume mount flows.

## Dependencies And Integration Points
The controller Deployment uses the controller account; Linux and Windows node DaemonSets use the node account. Provisioner/resizer sidecars need PV/PVC/Event/Lease permissions. Node secret access aligns with `podInfoOnMount` and inline CSI volumes that reference secrets.

## Risks And Test Signals
The main risk is excessive or missing Secret access. A disabled inline-volume feature should omit node secret RBAC; an enabled feature should render it. Test with `helm template --set feature.enableInlineVolume=false/true`, `kubectl auth can-i`, PVC provisioning, expansion, and inline-volume mount checks.
