# sources/control-plane/rook/pkg/operator/ceph/cluster/dependents_test.go

Purpose: verifies that `CephClusterDependents` discovers dependent Rook Ceph custom resources by kind and namespace.

Important APIs and tests: `TestCephClusterDependents` creates a fake controller-runtime client with the Rook Ceph scheme and uses subtests for `CephBlockPool`, `CephRBDMirror`, `CephFilesystem`, `CephFilesystemMirror`, `CephObjectStore`, `CephObjectStoreUser`, `CephObjectZone`, `CephObjectZoneGroup`, `CephObjectRealm`, `CephNFS`, `CephClient`, `CephBucketTopic`, `CephBucketNotification`, and an all-types scenario.

Control flow: each subtest creates objects in the target namespace, calls `CephClusterDependents`, and asserts `PluralKinds` plus names from `OfKind`. The combined scenario also verifies that querying another namespace returns an empty dependent list.

State and persistence behavior: all state is in a fake client. No status or real Kubernetes resources are modified.

Dependencies and integration points: uses the Rook Ceph scheme, controller-runtime fake client, `clusterd.Context`, and `testify/assert`.

Risks: not every kind in `cephClusterDependentListKinds` appears to be fully asserted in the visible active tests; error-path testing is commented out because fake client list failures are not configured. Tests rely on fake client behavior for unstructured list kinds, which may differ from discovery behavior in a real API server when CRDs are absent or versioned differently.

Test signals: strong signal that common dependents block deletion and namespace filtering works; weak signal for aggregate error handling and newly added dependent kinds unless tests are updated with the list.
