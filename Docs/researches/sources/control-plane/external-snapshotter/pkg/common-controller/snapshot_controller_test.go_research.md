# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_test.go

## Purpose
This file contains focused unit tests for controller cache update semantics and distributed snapshotting node selection. It verifies low-level helpers that the broader controller state machine depends on.

## Important APIs, Types, And Functions
`FakeNodeLister` implements enough of `corelisters.NodeLister` for node-affinity tests. `storeVersion` is a test helper that creates a `VolumeSnapshotContent`, sets a resource version, calls `utils.StoreObjectUpdate`, and checks whether the cache accepted or rejected the update. Test entry points are `TestControllerCache`, `TestControllerCacheParsingError`, and `TestGetManagedByNode`.

## Control Flow
`TestControllerCache` inserts resource versions in increasing, duplicate, stale, and string-order-tricky sequences to prove the store compares versions numerically. `TestControllerCacheParsingError` seeds a valid object and then attempts to store a non-numeric resource version, expecting an error. `TestGetManagedByNode` creates nodes and a PV node affinity selector, then checks that `getManagedByNode` returns the matching node name or an empty string when no node matches.

## State And Persistence Behavior
The cache tests validate in-memory `cache.Store` behavior rather than API persistence. The state being protected is the controller's local view of objects: stale events should not roll back newer cached objects, and invalid resource versions should surface errors. The node test models no persistence and only checks deterministic lookup.

## Dependencies And Integration Points
The file depends on snapshot test constructors, `utils.StoreObjectUpdate`, Kubernetes `cache.Store`, node labels/selectors, and the controller method `getManagedByNode`. It supports the distributed snapshotting integration path where dynamic `VolumeSnapshotContent` may be labeled with `VolumeSnapshotContentManagedByLabel`.

## Risks
The cache tests operate on `VolumeSnapshotContent` only, but the same utility is used for snapshots and group objects. `FakeNodeLister.Get` is a stub, so only list-based matching is covered. The no-match path expects no error and empty node, which matches current controller behavior but may hide cluster configuration problems.

## Test Signals
The file gives strong signal for numeric resource-version ordering and parsing failures. It also confirms node affinity matching uses Kubernetes selector semantics via the controller method.
