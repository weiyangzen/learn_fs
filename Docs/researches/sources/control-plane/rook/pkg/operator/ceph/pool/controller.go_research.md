# sources/control-plane/rook/pkg/operator/ceph/pool/controller.go

## Purpose

This file implements the `CephBlockPool` controller. It reconciles block pool CRs into Ceph pools, initializes RBD pools, configures RBD per-image stats, manages RBD mirroring bootstrap and peer import, tracks mirroring health check goroutines, protects deletion when pools are non-empty or have RADOS namespace dependents, deletes pools and EC profiles, and maintains status.

## Important APIs, Types, and Functions

- `ReconcileCephBlockPool` stores the controller-runtime client/scheme, clusterd context, cluster info, mirror monitoring contexts, operator manager context, event recorder, and operator config.
- `blockPoolHealth` stores the internal monitoring context/cancel function and whether monitoring has started.
- `Add`, `newReconciler`, and `add` register the controller and watches for `CephBlockPool` CRs, monitor endpoint ConfigMap changes, and peer-token Secret changes.
- `Reconcile` wraps `reconcile` with panic recovery and result reporting.
- `reconcile` is the main state machine for finalizers, cluster readiness, deletion, validation, pool creation/update, stats config, mirroring, and status.
- `configurePoolMirroring` creates bootstrap peer Secrets, imports configured peer tokens, reconciles CSI pool ID maps, updates status, and starts/stops mirror monitoring.
- `handleDeletionBlocked` computes deletion-blocked conditions from RADOS namespace dependents and pool emptiness, optionally starts cleanup jobs for force-delete, and returns an error when deletion must remain blocked.
- `createPool` and `deletePool` wrap Ceph pool create/delete operations and RBD pool initialization / EC profile cleanup.
- `generateStatsPoolList` and `configureRBDStats` maintain the mgr/prometheus `rbd_stats_pools` mon config key.
- `cancelMirrorMonitoring`, `disableMirroring`, `isAnyRadosNamespaceMirrored`, and `canConfigurePoolMirroring` manage mirroring shutdown and constraints.

## Control Flow

Controller setup watches pool CRs directly. It also maps monitor endpoint ConfigMap changes to all pool CRs so bootstrap peer tokens can refresh when mon endpoints change, and maps peer-token Secret changes to all pool CRs using `WatchPeerTokenSecretPredicate`.

Reconcile ignores missing CRs but cancels mirror monitoring for the vanished pool to avoid leaked goroutines. Existing CRs get finalizers. New CRs with nil status are marked Progressing. Cluster readiness is required; if a deleting pool's cluster is gone, mirror monitoring is cancelled and the finalizer is removed without Ceph cleanup.

Once cluster info is loaded, deletion runs first. `handleDeletionBlocked` checks RADOS namespace dependents, pool presence, pool emptiness including namespace contents, and force-delete cleanup. If deletion is not blocked, mirror monitoring is cancelled, the Ceph pool is deleted, RBD stats config is updated to remove the pool, and the finalizer is removed.

For active pools, `validatePool` checks CR and pool-spec constraints. Uninitialized operator config errors produce a delayed requeue. The Ceph version is read from the cluster status into cluster info. `reconcileCreatePool` calls `createPool`, which defaults the application to `rbd`, calls `cephclient.CreatePool`, and runs `rbd pool init` for RBD pools. RBD stats config is then synchronized from all non-deleting pool CRs with `enableRBDStats`.

Mirroring is configured only for non-EC pools. When enabled, the controller creates a bootstrap peer Secret, sets Progressing status with the cluster's RBD mirror peer cephx status, imports any configured peer Secrets, updates the CSI peermap ConfigMap, marks Ready, and manages a mirror health checker goroutine unless mirror status checks are disabled or mirroring mode is `init-only`. When mirroring is disabled, it attempts to disable Ceph-side mirroring, marks Ready with an empty cephx peer token, cancels monitoring, and clears mirroring status.

`disableMirroring` refuses to disable if any RADOS namespace in the pool still has mirroring enabled. For image-mode mirroring it also refuses when mirrored images remain. It removes storage cluster peers and then disables pool mirroring.

## State and Persistence Behavior

Kubernetes state includes the pool CR finalizer, `.status.phase`, `.status.info` fields such as pool type/failure domain and mirroring bootstrap Secret name, `.status.poolID`, `.status.cephx.peerToken`, deletion-blocked conditions, generated bootstrap peer Secrets, cleanup Jobs, and CSI pool ID map ConfigMaps. In-memory state includes `blockPoolMirrorContexts`, keyed by namespace/name, to cancel or avoid duplicate health-check goroutines.

Ceph state includes pools, pool application metadata, RBD initialization state, EC profiles, mirroring mode/peers, mirrored image state, RADOS namespace mirroring, and mgr/prometheus `rbd_stats_pools` config. Deletion removes the pool if present and deletes EC profiles for EC pools.

## Dependencies and Integration Points

The controller integrates with `CephCluster`, `cephclient` pool/RBD/mirroring APIs, mon endpoint predicates, config mon store, cleanup-job creation, Rook status reporting, dependent detection in `dependents.go`, peer token import in `peers.go`, CSI peermap reconciliation, Kubernetes ConfigMaps/Secrets, and status helpers in `status.go`. It depends on `validate.go` for pool-spec validation.

## Risks and Edge Cases

- Watch handlers for ConfigMaps and Secrets map changes to all pools, which is simple but can cause broad reconcile storms in large namespaces.
- `handleDeletionBlocked` can start cleanup jobs on force-delete while still returning blocked if dependents or non-empty state remain; cleanup job idempotency is important.
- Mirroring disable is intentionally conservative; leftover namespace mirroring or image mirroring keeps mirroring enabled and logs warnings while reconcile can still mark Ready in the disabled spec path after warning.
- In-memory mirror monitoring contexts are process-local; operator restart relies on future reconciles to recreate health checking.
- `configureRBDStats` merges existing external pool names with Rook-managed pools. Bad existing config with names that should be removed only disappears if they match current deleted/disabled pools.
- EC pools skip mirroring entirely, so mirroring fields on EC specs will not be reconciled.

## Test Signals

`controller_test.go` covers pool creation, name overrides, deletion including EC profile cleanup, readiness gating, successful reconcile to Ready, mirroring enabled/disabled, peer-token Secret import success/failure, deletion blocking for non-empty pools and RADOS namespace dependents, RBD stats config merge/removal/deduplication/errors, mirror peer key rotation status, Ready status for replicated and EC pools, and EC mirroring exclusion. `dependents_test.go` covers RADOS namespace dependent discovery. Coverage is broad, though some goroutine lifecycle, cleanup job details, and watch mapping behavior are not deeply tested.
