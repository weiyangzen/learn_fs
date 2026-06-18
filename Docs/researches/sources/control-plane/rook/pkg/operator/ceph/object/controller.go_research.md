# sources/control-plane/rook/pkg/operator/ceph/object/controller.go

## Purpose
`controller.go` is the main controller-runtime reconciler for `CephObjectStore`. It watches object-store CRs and owned Kubernetes objects, manages finalizers/status, coordinates CephCluster readiness and Ceph version state, creates or updates RGW services/pools/deployments/config, and safely deletes stores.

## Important APIs, Types, and Functions
`Add()`/`add()` register watches for CephObjectStore, owned Secrets/Services/Deployments, and externally referenced Secrets. `secretPredicate()` ignores Rook-owned Secrets, while `mapSecretToCR()` requeues object stores that reference changed RGW config or Keystone secrets. `Reconcile()` wraps `reconcile()` with panic recovery and reporting. `reconcile()` handles finalizers, status initialization, CephCluster readiness, cluster-info loading, deletion dependency checks, version/upgrade gates, cephx key-rotation decisions, validation, and create/update flow. `reconcileCreateObjectStore()` splits external and internal object-store reconciliation. `getMultisiteResourceNames()` and `retrieveMultisiteZone()` enforce multisite zone/zonegroup/realm readiness before RGW starts.

## Control Flow, State, and Persistence
Reconciliation writes CR status, finalizers, Kubernetes Services/Endpoints/Deployments/Secrets/ConfigMaps via `clusterConfig`, Ceph pools and multisite config through admin commands, mon config-store options, and cephx status. Deletion sets `Deleting`, checks bucket/user/zone dependents when possible, calls `deleteStore()`, and removes the finalizer. Create/update sets `Progressing` first and `Ready` with observed generation only after successful reconciliation.

## Dependencies and Integration Points
The controller integrates controller-runtime, Rook CephCluster readiness helpers, Ceph command execution, object multisite helpers, pool validation/creation, admin-ops endpoint setup, keyring rotation, Kubernetes event/status reporting, bucket/COSI dependency checks, and externally referenced Secrets.

## Risks and Test Signals
Risks include races with multisite zone setup, false deletion safety when admin context or pools are unavailable, secret watch fan-out across all stores in a namespace, cephx status assumptions for brownfield stores, and exact Ceph version comparison during upgrades. Tests cover no/ready cluster behavior, normal and multisite creation/deletion, zone-not-ready requeue, external stores, missing external credentials, secret-to-CR mapping, version comparison, and key rotation.
