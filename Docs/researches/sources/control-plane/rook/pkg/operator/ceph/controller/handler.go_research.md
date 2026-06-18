# sources/control-plane/rook/pkg/operator/ceph/controller/handler.go

## Purpose
`handler.go` provides a generic map function that lets a watch on one object type enqueue reconcile requests for all objects of another CR type.

## Important APIs, Types, and Functions
`ObjectToCRMapper[List client.ObjectList, T runtime.Object]()` determines the list GVK with `apiutil.GVKForObject()`, returns a `handler.TypedMapFunc`, lists objects of that GVK through the controller-runtime client into an `unstructured.UnstructuredList`, and maps every item to a `reconcile.Request`.

## Control Flow, State, and Persistence
The mapper does not persist state. On each watched event, it lists all target CRs cluster-wide or within whatever scoping the client/cache enforces, then enqueues reconcile requests by namespace/name. List errors return nil and silently skip enqueueing.

## Dependencies and Integration Points
It depends on controller-runtime client/list handling, unstructured lists, runtime schemes, typed handlers, and reconcile request construction. It is intended for cross-resource watches, such as reconciling CephFilesystem objects when a CephCluster changes.

## Risks
Listing all target CRs on every event can be expensive in large clusters. Errors are swallowed with no log, which can make missed reconciles hard to diagnose. The mapper currently takes no list options, so callers cannot easily namespace-filter here. GVK resolution must be correct for list types registered in the scheme.

## Test Signals
`handler_test.go` confirms that a fake CephFilesystem list maps to the expected request. It does not cover list failures, multiple objects, namespace filtering, or missing scheme registrations.
