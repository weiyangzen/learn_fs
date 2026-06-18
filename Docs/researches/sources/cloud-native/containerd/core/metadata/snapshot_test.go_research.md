# sources/cloud-native/containerd/core/metadata/snapshot_test.go

Purpose: provides targeted unit tests and a fake backend snapshotter for metadata snapshot reference, lease, namespace, and inherited-label behavior.

Important APIs and helpers: `snapshotLease`, `TestSnapshotterWithRef`, `TestFilterInheritedLabels`, `tmpSnapshotter`, and `NewTmpSnapshotter`. The fake implements `snapshots.Snapshotter` with in-memory maps of snapshots and target references.

Control flow: `TestSnapshotterWithRef` creates a metadata DB with a fake snapshotter, uses leases in multiple namespaces, prepares and commits snapshots with `containerd.io/snapshot.ref`, verifies already-exists behavior, checks cross-namespace materialization of target snapshots, validates parent mismatch/not-found behavior, and checks lease resource changes for active and committed names. `TestFilterInheritedLabels` table-drives label filtering for the inherited label prefix. The fake backend models target deduplication by returning already-exists when a target with the same parent exists.

State and persistence: the test combines metadata bbolt state, lease resources, namespace contexts, and fake backend maps. The fake stores `snapshots.Info` keyed by backend name and target-to-backend-name indexes.

Dependencies and integration: uses leases, snapshots, mount, filters, namespaces, and errdefs. It is a direct test of `snapshot.go` target and lease flows.

Risks: fake backend behavior approximates but does not fully reproduce real snapshotter implementations. Time values and map iteration order are not central to assertions.

Test signals: strong signal for snapshot reference deduplication, lease attachment/removal, cross-namespace target sharing, and inherited label filtering.
