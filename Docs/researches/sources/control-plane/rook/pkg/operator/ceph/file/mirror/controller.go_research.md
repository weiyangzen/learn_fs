# sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller.go

## Purpose
This is the controller-runtime reconciler for `CephFilesystemMirror` custom resources. It watches the mirror CR and owned resources, gates work on CephCluster readiness and version state, starts or updates the `cephfs-mirror` Deployment, and maintains phase, observed generation, and CephX key-rotation status.

## Important APIs, Types, and Functions
`Add`, `newReconciler`, `watchOwnedCoreObject`, and `add` register the controller. `ReconcileFilesystemMirror` stores Rook context, cluster info/spec, controller-runtime client/scheme, operator config, event recorder, and key-rotation flag. `Reconcile` wraps `reconcile` and reports results. `reconcile` handles fetch/status initialization/readiness/versioning/key-rotation/start/status update. `reconcileFilesystemMirror` validates external-cluster version compatibility and calls `start`. `updateStatus` retries status updates on conflicts.

## Control Flow, State, and Persistence
The controller watches `CephFilesystemMirror` CRs and owned ConfigMaps, Secrets, and Deployments. Reconcile returns cleanly for not-found, initializes empty status plus uninitialized CephX state, waits when the CephCluster is absent or unready, loads cluster info, detects running/desired Ceph versions, waits during upgrades for non-external clusters, decides whether daemon keys should rotate, starts the mirror deployment, computes updated CephX status, and writes Ready phase with observed generation. On reconcile errors, `Reconcile` attempts to mark the CR failed.

## Dependencies and Integration Points
It integrates with controller-runtime, Rook cluster readiness helpers, Ceph version reporting, keyring status helpers, `reporting.UpdateStatus`, fake and real Kubernetes clients, mirror deployment startup in `mirror.go`, and Ceph auth/keyring logic in `config.go`.

## Risks
There is no finalizer or deletion cleanup path in this controller; cleanup relies on owner references and Kubernetes garbage collection. The not-ready branch records a "successfully removed finalizer" event even though this CR has no finalizer path, which may be misleading. On reconcile error, a status-update failure shadows the original error in logging. The comment references `cephRBDMirror` in a CephFS mirror path, indicating copy/paste risk.

## Test Signals
Signals include requeue on missing/unready cluster, no requeue for too-old version handling if start path returns successfully/with status, requeue during cluster upgrade, Ready status on supported Ceph versions, CephX status initialization and generation updates, and failed status updates on reconciliation errors.
