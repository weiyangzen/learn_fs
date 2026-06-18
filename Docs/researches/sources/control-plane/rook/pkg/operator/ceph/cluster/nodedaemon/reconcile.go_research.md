# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/reconcile.go

## Purpose
This file implements the node daemon reconciler. It ensures crash collector and ceph-exporter daemons exist only on nodes that currently host Ceph pods, removes them from nodes without Ceph pods, manages disabled states, performs one-time orphan exporter cleanup, and reconciles the crash pruner.

## Important APIs, Types, And Functions
`ReconcileNode` stores scheme, controller-runtime client, Rook cluster context, operator manager context, and operator config. `Reconcile()` wraps `reconcile()` with panic recovery/logging. `reconcile(request)` is the main control loop. Supporting methods include `createOrUpdateNodeDaemons()`, `removeDisabledCrashCollectorDaemons()`, `removeDisabledCephExporterDaemons()`, `listDeploymentAndDelete()`, `deleteNodeDaemon()`, `cephPodList()`, `listNodeDaemonsAndDelete()`, and `deleteDeployment()`. Global state includes `waitForRequeueIfSecretNotCreated` and `exporterOrphanCheckDone`.

## Control Flow And State
Reconciliation fetches the requested node and ignores not-found nodes. It lists all Ceph pods by app labels for mon, mgr, osd, object, mds, rbd, and mirror, groups them by namespace, and for each namespace fetches the first CephCluster. If crash collector/exporter are disabled, it deletes their deployments and may skip the namespace if both are disabled. It requires the crash collector keyring secret before creating any node daemons, requeueing for 30 seconds if missing. It determines Ceph version from the cluster image, collects unique tolerations from Ceph pods on the target node, runs one-time exporter orphan cleanup per namespace, and either creates/updates node daemons when the node hosts Ceph pods or deletes node daemons from that node when it does not. Finally it reconciles the crash pruner.

## Dependencies And Integration Points
The reconciler depends on controller-runtime client/list/delete operations, Kubernetes Node/Pod/Deployment/Secret APIs, CephCluster CRs, app label conventions across Ceph daemon packages, Ceph version detection, disruption toleration set utilities, crash/exporter/pruner builders, and service/service monitor helpers. It is the integration point tying node and pod watch events to daemon resources.

## Risks And Test Signals
Risks include selecting the first CephCluster when multiple exist in a namespace, global `exporterOrphanCheckDone` lifecycle across tests/operator lifetime, requeue blocking all node daemons on missing crash secret, partial API list failures, and best-effort deletion only logging errors in cleanup paths. This file has no direct test file in the listed set; behavior is covered indirectly by tests for add filters, crash/exporter/pruner object builders, and orphan exporter cleanup.
