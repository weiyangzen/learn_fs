<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller.go -->
# sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller.go

## Purpose
Implements the controller-runtime reconciler for the singleton BeegfsDriver CR and materializes the BeeGFS CSI driver deployment.

## Important APIs, Types, And Functions
`BeegfsDriverReconciler.Reconcile` drives all reconciliation. Helpers include `newConfigMap`, `newSecret`, `newTLS`, `setCommonObjectMetadata`, `setResourceVersionAnnotations`, `setImages`, `setNodeResources`, `setControllerResources`, `getImageStringWithOverride`, `setLogLevel`, and `setNodeAffinity`. `finalizerClusterResourceDeletion` handles cluster-scoped cleanup.

## Control Flow
Reconcile fetches the CR, loads clean driver manifests from `deploy/k8s`, computes status from existing StatefulSet/DaemonSet readiness, updates status only if changed, manages a finalizer, creates or updates ConfigMap/Secrets/RBAC/CSIDriver, and then creates or updates driver StatefulSet and DaemonSet. Pod templates receive ConfigMap/Secret resource-version annotations to force rollouts on config/auth/TLS changes.

## State And Persistence
Persistent cluster state includes namespaced ConfigMap, ConnAuth Secret, TLS Secret, service account/Roles/RoleBindings, StatefulSet, DaemonSet, cluster-scoped ClusterRoles/ClusterRoleBindings, and CSIDriver. Status conditions persist controller/node service readiness. Cluster-scoped resources cannot be owner-referenced, so the finalizer deletes them manually.

## Dependencies And Integration Points
Depends on operator API types, deploy/k8s manifest getters, Kubernetes apps/core/rbac/storage APIs, controller-runtime client/manager, and sigs.k8s.io/yaml for plugin config serialization.

## Risks And Edge Cases
Status is computed before resources are reconciled, so first reconcile can report not-created before creating objects. Secrets are not reconciled after creation by design. Cluster-scoped updates lack owner references and rely on finalizer correctness. Image parsing splits on the first colon, which can mishandle registry strings with ports.

## Test Signals
Envtest verifies object creation, owner refs for namespaced resources, finalizer addition, cluster-scoped cleanup, status unreadiness, ConfigMap/Secret rollout annotation updates, invalid logLevel validation, and helper behavior for image overrides/log level/string containment.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller.go -->
