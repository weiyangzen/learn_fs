# sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents.go

## Purpose

This helper finds Kubernetes resources that depend on a `CephObjectZone`, currently `CephObjectStore` CRs in the same namespace whose `spec.zone.name` matches the zone. It is used to block zone deletion while object stores still reference the zone.

## Important APIs and Functions

- `CephObjectZoneDependentStores(clusterdCtx, clusterInfo, zone, objContext) (*dependents.DependentList, error)` lists object stores and returns a `DependentList` of matching store names under kind `CephObjectStore`.

## Control Flow

The function builds a namespace/name for logging and error wrapping, initializes an empty dependent list, lists `CephObjectStores` in `zone.Namespace` using the Rook clientset and `clusterInfo.Context`, and iterates through the list. Stores with `store.Spec.Zone.Name == zone.Name` are added as dependents. Non-matching stores are logged as non-dependent. Any list error is wrapped with context and returned with the possibly empty list.

## State and Persistence Behavior

The function is read-only. It does not mutate Kubernetes or Ceph state. Its result affects deletion state through callers such as `deleteCephObjectZone`, which reports deletion-blocked conditions when dependents are present.

## Dependencies and Integration Points

It depends on the Rook typed clientset, `client.ClusterInfo.Context`, `object.Context` for the signature, `dependents.DependentList`, Rook controller namespace/name formatting, and logging. The `objContext` argument is not used by the function body, but callers already have it in deletion flows.

## Risks and Edge Cases

- Only same-namespace object stores are considered.
- Only `spec.zone.name` is checked; other possible implicit dependencies are not considered.
- The unused `objContext` parameter may indicate legacy API shape or future intended checks.
- The non-dependent debug log is executed for all stores, but the current code logs the non-dependent message even after dependent checks only in the `else` branch, so functional behavior is correct.

## Test Signals

`dependents_test.go` covers no stores, one matching store, one different-zone store, and multiple matching stores. It provides good confidence for the current dependency filter.
