# sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume.go

Purpose: controller-runtime reconciler for Kubernetes `PersistentVolume` objects. It regenerates or repairs Ceph-CSI metadata/journal entries when PVs exist but backend OMAP metadata needs to be restored.

Important APIs/types/functions: `ReconcilePersistentVolume` owns a controller-runtime client, `ctrl.Config`, and an `IDLocker`. Public registration uses `Init()` and `Add()`. Key functions are `Reconcile()`, `reconcilePV()`, `newPVReconciler()`, `shouldReconcileBasedOnDriver()`, `add()`, `getCredentials()`, and `checkStaticVolume()`.

Control flow: watch predicates accept create/update/generic events for PVs not deleting and either missing `pv.kubernetes.io/provisioned-by` or matching this driver. Reconcile fetches the PV, skips missing/deleting objects, then `reconcilePV()` verifies CSI driver, claim binding, and non-static volume. It selects controller-expand or node-stage secret refs, serializes by volume handle, fetches user credentials from the secret, then dispatches by PV attributes: CephFS PVs have `fsName` and call `cephfsstore.SetSubVolCSIMetadata()`, while RBD PVs call `rbd.RegenerateJournal()` and logs if the handler changes.

State and persistence: writes or repairs Ceph-side OMAP/journal/subvolume metadata. Reads Kubernetes PVs and Secrets. Per-volume in-process locks prevent concurrent repair for the same handle, while controller concurrency is also set to one.

Dependencies and integration points: uses controller-runtime metadata watches, Kubernetes PV/Secret APIs, CephFS store metadata, RBD journal regeneration, common credentials, and controller config cluster/instance IDs.

Risks: missing secret refs produce hard errors. Driver detection for CephFS relies on `fsName` in volume attributes. Static volumes are skipped, so stale metadata for static PVs is intentional. The missing provisioner annotation path reconciles all such PVs, which is conservative for deleted annotations but can process unrelated objects until CSI driver check stops them.

Test signals: unit coverage exists for `shouldReconcileBasedOnDriver()` only. Additional tests should cover secret selection, static skip, CephFS/RBD dispatch, lock contention, missing claim ref, and fake-client reconciliation.
