# sources/control-plane/rook/pkg/operator/ceph/object/bucket/predicate.go

## Purpose
`predicate.go` defines event filters for the bucket provisioner controller watches. It limits ConfigMap and CephCluster events to the ones that should start or restart OBC watching.

## Important APIs, Types, and Functions
`rookOBCWatchOperatorNamespace` names the operator setting key `ROOK_OBC_WATCH_OPERATOR_NAMESPACE`. `cmPredicate()` returns typed predicate functions for ConfigMap create/update/delete/generic events. `cephClusterPredicate()` returns typed predicates for CephCluster events and uses `controller.DuplicateCephClusters()` to suppress duplicate clusters in a namespace.

## Control Flow, State, and Persistence
For ConfigMaps, create events are accepted only for the operator settings ConfigMap at generation 1. Update events compare the watched namespace setting; when it changes, the predicate logs and calls `controller.ReloadManager()` so the manager restarts and rebuilds watches. Update, delete, and generic events all return false. For CephClusters, create events reconcile only if there is no duplicate cluster; update, delete, and generic events return false. There is no direct persisted state, but `ReloadManager()` changes operator process lifecycle.

## Dependencies and Integration Points
The file depends on controller-runtime typed predicates/events, core ConfigMaps, Rook CephCluster types, and Rook controller helpers. It is wired by `bucket/controller.go` when registering watches.

## Risks
Only ConfigMap create and CephCluster create events enqueue reconciles. If the CephCluster transitions from not ready to ready after the initial create, the bucket controller relies on reconcile requeues from failed cluster-info loading or other paths, not this predicate's update handling. Calling `ReloadManager()` from a predicate is a broad side effect; changes to one ConfigMap setting restart the manager rather than just updating an informer. There are no direct tests for these predicates in the requested set.

## Test Signals
Coverage is indirect through bucket controller tests. Dedicated predicate tests should cover generation filtering, watch-namespace setting changes, manager reload call behavior through an injectable hook, duplicate CephCluster suppression, and false returns for updates/deletes/generic events.
