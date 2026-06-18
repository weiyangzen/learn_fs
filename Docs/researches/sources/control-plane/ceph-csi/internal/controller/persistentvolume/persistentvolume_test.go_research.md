# sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume_test.go

Purpose: unit tests for the PV reconciler event-filter helper `shouldReconcileBasedOnDriver()`.

Important APIs/types/functions: `Test_shouldReconcileBasedOnDriver()` constructs `client.Object` inputs using `corev1.PersistentVolume` metadata and compares expected boolean decisions.

Control flow: table cases cover nil object, deletion timestamp, missing annotation, matching provisioner annotation, and non-matching provisioner annotation. All subtests run in parallel.

State and persistence: in-memory Kubernetes object metadata only.

Dependencies and integration points: protects the predicate used by the PV controller's metadata watch in `add()`. The missing-annotation case documents intended reconciliation of PVs where the provisioner annotation was removed.

Risks: does not cover update/delete/generic predicate wrappers, full reconcile behavior, nil annotation map, or CSI driver mismatch inside `reconcilePV()`. It validates only the first filter gate.

Test signals: good quick signal for event filtering regressions. Fake controller-runtime tests are still needed for full PV journal repair behavior.
