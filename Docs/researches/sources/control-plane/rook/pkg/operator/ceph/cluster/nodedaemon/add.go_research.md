# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add.go

## Purpose
This file registers the node daemon controller. The controller watches nodes, Ceph pods, and crash collector deployments so it can reconcile node-scoped crash collector and ceph-exporter daemons.

## Important APIs, Types, And Functions
Constants define `controllerName`, `CrashCollectorAppName`, `cephExporterAppName`, `prunerName`, and `NodeNameLabel`. `Add()` constructs and registers the controller. `newReconciler()` creates a `ReconcileNode`. `add()` creates the controller-runtime controller and installs watches. `isCephPod(labels, podName)` filters Ceph workload pods.

## Control Flow And State
The controller watches node spec updates only when `Node.Spec` changes. It watches crash collector Deployments and maps them back to the node named in the pod template's `node_name` label. It watches pods and enqueues the hosting node when a Ceph pod moves nodes; the update predicate only allows node-name changes. `isCephPod` requires `rook_cluster` and excludes canary, crashcollector, and exporter pods to avoid reconciling node daemons from temporary or self-owned pods.

## Dependencies And Integration Points
The file depends on controller-runtime controller, source, handler, predicate, Kubernetes Node/Pod/Deployment APIs, Rook cluster context, and operator config. It integrates with `ReconcileNode` in `reconcile.go`.

## Risks And Test Signals
Risk centers on event filtering. If `isCephPod` is too broad, daemon pods can trigger loops; if too narrow, node daemon creation/deletion may lag. `add_test.go` covers canary exclusion and positive/negative `rook_cluster` label behavior. Crashcollector/exporter exclusion is implemented but not directly covered in the shown tests.
