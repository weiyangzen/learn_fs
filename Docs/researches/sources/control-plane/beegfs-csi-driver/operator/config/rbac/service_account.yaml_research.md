<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/service_account.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/service_account.yaml

## Purpose
Defines the Kubernetes ServiceAccount used by the operator manager deployment.

## Important APIs, Types, And Functions
ServiceAccount `controller-manager` in placeholder namespace `system`.

## Control Flow
Kustomize namespaces/prefixes it and `manager.yaml` references it by name.

## State And Persistence
ServiceAccount persists identity and token projection behavior for the manager pod.

## Dependencies And Integration Points
Bound by leader election, metrics auth, and manager role bindings.

## Risks And Edge Cases
Changing the name requires updating all bindings and the Deployment.

## Test Signals
Envtest controller tests check that service accounts from driver deployment manifests are created, but not this install service account directly.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/service_account.yaml -->
