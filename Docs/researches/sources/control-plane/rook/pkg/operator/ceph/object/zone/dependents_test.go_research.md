# sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents_test.go

## Purpose

This file tests `CephObjectZoneDependentStores`, the helper that detects object stores blocking zone deletion.

## Important Test Cases

- No object stores exist, so the dependent list is empty.
- One object store references the zone, so that store appears under `CephObjectStore`.
- One object store references a different zone, so the dependent list remains empty.
- Multiple object stores reference the zone, so all matching names are returned.

## Control Flow and Test Setup

The test constructs a `CephObjectZone`, two `CephObjectStore` objects, a fake Rook clientset, a mock executor-backed clusterd context, and `client.AdminTestClusterInfo`. Each subtest creates a fresh context and populates the fake clientset as needed before calling `CephObjectZoneDependentStores`.

## State and Persistence Signals

All state is fake Kubernetes API state in the Rook clientset. Assertions inspect `deps.Empty()` and `deps.OfKind("CephObjectStore")`, which is the data the zone deletion path uses to decide whether finalizer removal is blocked.

## Dependencies and Integration Points

The test uses fake Rook clientsets, `object.NewContext`, `exectest.MockExecutor`, `testify/assert`, and Ceph API scheme registration. No real Ceph commands are executed.

## Risks and Gaps

The test does not cover list errors from the Rook clientset or cross-namespace stores. It mutates `objectStoreB.Spec.Zone.Name` in one subtest, so future test changes should avoid accidental state leakage by copying objects per subtest.

## Test Signals

The file gives direct confidence that the current deletion-blocking dependency lookup includes exactly same-namespace stores with matching `spec.zone.name`.
