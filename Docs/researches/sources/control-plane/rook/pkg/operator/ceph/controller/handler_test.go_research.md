# sources/control-plane/rook/pkg/operator/ceph/controller/handler_test.go

## Purpose
`handler_test.go` verifies that `ObjectToCRMapper()` can turn a watched event into reconcile requests for existing target CRs.

## Important APIs, Types, and Functions
`TestObjectToCRMapper` creates a `CephFilesystem`, registers Ceph list/object types in the scheme, builds a fake client, obtains a mapper for `CephFilesystemList`, and asserts that invoking it returns the filesystem's namespace/name request.

## Control Flow, State, and Persistence
The test keeps all objects in fake-client memory. The event object passed to the mapper is not itself used beyond triggering the list.

## Dependencies and Integration Points
It depends on Ceph API scheme registration, controller-runtime fake clients, runtime objects, and reconcile request types.

## Risks
The expected request name is shared package test data (`name`, `namespace`) from another test file, which couples tests in the package. Only a single object is listed. Error handling is not exercised because fake list succeeds.

## Test Signals
The test confirms happy-path GVK/list/request mapping. Missing signals include list error behavior, multiple CRs, empty lists, and mapper construction failures.
