# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

## Purpose
This `v1.3.0` RBAC template creates the controller service account and the external-provisioner cluster permissions used by the SMB CSI controller Deployment. It is named `rbac-csi-smb-controller.yaml` in these earlier chart versions because node workloads do not receive a separate chart-managed service account here.

## Important APIs, Types, And Functions
The rendered APIs are `v1/ServiceAccount`, `rbac.authorization.k8s.io/v1/ClusterRole`, and `ClusterRoleBinding`. `.Values.serviceAccount.create` gates service account creation, while `.Values.rbac.create` gates the role and binding. The role can create/delete PVs, update PVCs, read StorageClasses, CSINodes, Nodes, Events, Leases, and Secrets; leader election uses `coordination.k8s.io/leases`.

## Control Flow
Helm emits the service account only when requested, then independently emits RBAC when requested. The binding references `.Values.serviceAccount.controller` in `.Release.Namespace`, so setting `serviceAccount.create: false` still expects a preexisting account with the same name.

## State And Persistence Behavior
The resources are cluster-persistent authorization state. They do not store volume data, but they govern whether dynamic provisioning, event recording, secret lookup, and leader election can proceed.

## Dependencies And Integration Points
The controller Deployment uses this account. The provisioner sidecar depends on the PV/PVC/StorageClass/secret permissions; lease verbs must match the sidecar's `--leader-election` settings.

## Risks And Test Signals
The role is broad enough to read Kubernetes Secrets, which is necessary for SMB credentials but security-sensitive. Test with `helm template` for both create flags, `kubectl auth can-i` as the controller account, and dynamic provisioning of a PVC backed by an SMB secret.
