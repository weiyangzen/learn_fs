# sources/control-plane/rook/pkg/operator/ceph/file/controller.go

## Purpose
This is the controller-runtime reconciler for `CephFilesystem` custom resources. It wires watches, enforces finalizer-based cleanup, gates reconciliation on CephCluster readiness and Ceph version state, creates/deletes CephFS and MDS resources, configures mirroring, manages CephX key-rotation status, and starts or stops mirror-status monitoring goroutines.

## Important APIs, Types, and Functions
The public controller entry point is `Add`, which constructs a `ReconcileCephFilesystem` via `newReconciler` and registers watches in `add`. `ReconcileCephFilesystem` holds controller-runtime client/recorder/scheme, Rook cluster context, Ceph cluster spec/info, per-filesystem mirror health contexts, operator config, and a `shouldRotateCephxKeys` decision flag. `Reconcile` wraps `reconcile` with panic recovery and reporting. Helper methods include `reconcileCreateFilesystem`, `reconcileDeleteFilesystem`, `reconcileMirroring`, `reconcileAddBootstrapPeer`, `fsChannelKeyName`, and `cancelMirrorMonitoring`.

## Control Flow, State, and Persistence
`add` watches `CephFilesystem` CRs, owned Secrets and Deployments, and the monitor endpoint ConfigMap so bootstrap peer token changes can reconcile all filesystems. `reconcile` fetches the CR, cancels mirror monitoring on not-found, records the current generation, adds a finalizer, initializes status and CephX status when absent, and returns early until the owning `CephCluster` is ready. Once ready, it creates a per-filesystem cancelable context in `fsContexts`, reloads `ClusterInfo`, handles deletion by checking dependents and calling `reconcileDeleteFilesystem`, and removes the finalizer only after cleanup.

For normal reconciliation, it detects running and desired Ceph versions, waits during cluster upgrades, validates the filesystem spec, decides whether MDS CephX keys should rotate, and calls `reconcileCreateFilesystem`. It updates CephX status to Progressing, then handles mirroring: disabling mirroring when configured off, enabling the mirroring and snap-schedule modules, creating bootstrap peer secrets, importing peer tokens, setting Ready status with mirroring info, and optionally starting the periodic mirror checker. If mirroring did not update status, it sets Ready at the end.

## Dependencies and Integration Points
The controller integrates with controller-runtime watches, Kubernetes Secrets/Deployments/ConfigMaps, Rook `opcontroller` readiness/version/finalizer/status helpers, Ceph command clients, keyring rotation helpers, the `mds` package, mirror status checking, and deletion reporting. It depends on `CephFilesystemDependents` to prevent destructive deletion while subvolume state exists.

## Risks
`fsContexts` is a plain map modified from reconcile paths and read before indexing; concurrent reconciles for the same controller could race unless controller-runtime serialization and practical scheduling prevent overlap. Mirroring status goroutines use the `ClusterInfo` and spec pointer captured at startup; later cluster/spec updates may not affect a running checker until it is canceled and recreated. Status is set Ready even though a TODO notes it does not fully prove filesystem health. Deletion continues after some Ceph cleanup failures in lower layers, so operator status/events are important for operator visibility.

## Test Signals
Good signals include finalizer add/remove behavior, not-found mirror-monitor cancellation, requeue on missing or unready cluster, upgrade wait behavior, dependent deletion blocking events, CephX status transitions, mirroring enable/disable paths, bootstrap peer secret validation/import, and one mirror checker per filesystem when status checking is enabled.
