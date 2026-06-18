# sources/control-plane/rook/pkg/operator/ceph/cluster/controller_test.go

Purpose: validates key controller lifecycle behaviors: deletion blocking by dependent resources, finalizer removal, and skip-reconcile handling.

Important APIs and tests: `TestReconcileDeleteCephCluster` builds a deleting `CephCluster` and a dependent `CephBlockPool`, then calls `Reconcile`. `TestRemoveFinalizers` directly tests `removeFinalizer` for a `CephCluster` and mon Secret. `TestReconcileSkipsWhenSkipReconcileLabelSet` calls the internal `reconcile` method for a labeled cluster and checks the emitted event.

Control flow: the deletion test first expects a requeue and a deletion-blocked event/condition while the block pool exists. It then deletes the pool and reconciles again, expecting zero result and a non-blocking deletion condition. The finalizer test builds fake clients with objects containing finalizers and verifies they are cleared. The skip test verifies no reconcile work is done when the skip label exists after the finalizer is already present.

State and persistence behavior: fake controller-runtime clients persist CR status conditions and finalizer changes. The fake event recorder captures deletion-blocked and skipped events. No real cleanup jobs, PVs, or KMS interactions are executed.

Dependencies and integration points: uses Rook Ceph API scheme, CSI addons scheme, fake Kubernetes and Rook clients, API extension fake client, controller-runtime fake client, and Kubernetes event recorder.

Risks: deletion unblocked flow does not exercise cleanup policy, volume checks, external purge, or finalizer removal all the way to object deletion. Finalizer tests call the helper directly rather than through full reconcile. Skip behavior assumes the finalizer has already been added; the first reconcile for a newly created labeled object may still add the finalizer before later skipping.

Test signals: strong focused signals for dependent deletion safety and skip event emission, moderate coverage for finalizer utility behavior.
