<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/controller.go

## Purpose
This file implements the `CephNFS` reconciler. It watches the CR and owned Deployments, Services, and ConfigMaps, coordinates cluster readiness and upgrades, manages finalizers, validates security, ensures NFS pool/config state, reconciles NFS-Ganesha daemon instances, and updates CR status including CephX rotation state.

## Important APIs and control flow
`Add`, `newReconciler`, `watchOwnedCoreObject`, and `add` install the controller and watches. `Reconcile` delegates to `reconcile` and reports events/status through `reporting.ReportReconcileResult`. `reconcile` fetches the CR, adds a finalizer, initializes empty/CephX status, validates `Spec.Security`, waits for a ready `CephCluster`, loads cluster info, handles deletion by removing Ganesha servers from the grace database and finalizer, waits for Ceph upgrades to finish, forces RADOS pool/namespace to `.nfs` and CR name, validates settings, decides whether CephX keys should rotate, configures the NFS pool, reconciles daemon deployments/services/config maps, and marks Ready with updated CephX status.

`reconcileCreateCephNFS` validates external cluster versions, counts current NFS deployments by labels, scales down if needed, then calls `upCephNFS` for create/update.

## State and persistence
State includes `CephNFS.status`, finalizers, events, `.nfs` pool/application state, Ganesha RADOS objects, per-daemon Deployments, Services, ConfigMaps, keyring Secrets, and Ganesha grace database entries.

## Dependencies and integration points
The reconciler depends on Rook cluster readiness/version helpers, keyring rotation helpers, Ceph command wrappers, Kubernetes clientsets, controller-runtime clients, and event recording. It integrates with `nfs.go` for daemon lifecycle, `config.go` for RADOS config/keyrings, `security.go` for pod security additions, and `spec.go` for Kubernetes resource generation.

## Risks and test signals
The reconciler mutates `cephNFS.Spec.RADOS` in-memory to `.nfs` and the CR name; callers must not assume user-provided RADOS fields survive reconciliation. It blocks during Ceph upgrades for non-external clusters and depends on deployment labels to compute scale-down targets. Tests cover readiness gates, invalid security, one/multiple instances, scale-down, multiple CRs, image override, key rotation, and Ganesha config object naming.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller.go -->
