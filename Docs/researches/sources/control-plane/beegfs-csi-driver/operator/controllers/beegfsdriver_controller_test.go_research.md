<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller_test.go -->
# sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller_test.go

## Purpose
Ginkgo/Gomega integration and helper tests for the BeegfsDriver controller.

## Important APIs, Types, And Functions
Tests use `getValidCRWithNoFields`, `getValidCRWithAllFields`, and `getContainerImageForName`. Specs cover resource creation, finalizers, status, deletion cleanup, rollout-triggering updates, invalid CRs, and helper functions.

## Control Flow
Each integration test creates a random namespace and a populated BeegfsDriver CR, then uses Eventually against envtest API server state to observe reconciliation. Modification contexts update pluginConfig or Secrets and assert resource versions/annotations change.

## State And Persistence
Creates transient namespaces, CRs, Kubernetes resources, and cluster-scoped objects inside envtest. Random namespace state avoids collisions but debug output suggests historical duplicate namespace issues.

## Dependencies And Integration Points
Depends on deploy/k8s manifest getters, operator API types, envtest client, Ginkgo/Gomega, and controller-runtime.

## Risks And Edge Cases
The deletion test has a type switch branch for non-pointer `rbacv1.ClusterRoleBinding`, while deploy resources likely use pointers, risking missed assertions. Singleton name patch is explicitly not tested because envtest loads only CRD bases.

## Test Signals
High-value coverage of reconcile side effects and rollout triggers. Missing coverage for RBAC authorization, Prometheus/OLM manifests, and kustomize-only CRD patches.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller_test.go -->
