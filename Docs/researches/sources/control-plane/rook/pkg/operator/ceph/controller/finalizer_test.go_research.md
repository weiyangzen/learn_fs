# sources/control-plane/rook/pkg/operator/ceph/controller/finalizer_test.go

## Purpose
`finalizer_test.go` validates basic finalizer add/remove behavior for Ceph CR objects.

## Important APIs, Types, and Functions
`TestAddFinalizerIfNotPresent` starts with a `CephBlockPool` with no finalizers and asserts one is added without a fake-client generation change. `TestRemoveFinalizer` removes the derived finalizer from a `CephBlockPool`. `TestRemoveFinalizerWithName` removes the same finalizer by explicit string.

## Control Flow, State, and Persistence
The tests register Ceph types in the scheme and use a controller-runtime fake client seeded with the object. Updates persist only in fake-client memory.

## Dependencies and Integration Points
The tests depend on Ceph API scheme registration, runtime objects, fake client, and metav1 object metadata.

## Risks
Fake clients do not model all API-server generation/resourceVersion behavior, so generation assertions are weak. Test objects use lower-case TypeMeta Kind for removal, matching the expected finalizer but not necessarily all live object TypeMeta forms. Error and conflict branches are untested.

## Test Signals
Signals prove the happy paths for add and remove. Missing signals include idempotent add/remove, stale object refresh, duplicate finalizers, conflict retries, and empty Kind behavior.
