# sources/control-plane/rook/pkg/operator/ceph/controller/finalizer.go

## Purpose
`finalizer.go` manages Rook Ceph CR finalizers so controllers can block deletion until external Ceph or Kubernetes cleanup is complete.

## Important APIs, Types, and Functions
`AddFinalizerIfNotPresent()` builds a finalizer from object kind and `ceph.rook.io`, appends it when absent, updates the object, and reports whether the object generation changed. `RemoveFinalizer()` removes the kind-derived finalizer. `RemoveFinalizerWithName()` refreshes the latest object from the API, removes a specific finalizer, and updates. `buildFinalizerName()` lowercases the kind and appends the Ceph custom resource group. The local `remove()` helper deletes a string from a slice.

## Control Flow, State, and Persistence
Finalizer changes are persisted via controller-runtime `client.Update()`. Removal first performs a fresh `Get()` to avoid updating stale finalizer state. The generated finalizer format is `<lowercase-kind>.ceph.rook.io`, for example `cephblockpool.ceph.rook.io`.

## Dependencies and Integration Points
The file depends on Kubernetes object metadata access, controller-runtime client operations, `cephv1.CustomResourceGroup`, and logging helpers. It is used by CR reconcilers that need cleanup protection.

## Risks
`remove()` mutates while iterating and does not break after removal; duplicate entries could be skipped or handled unexpectedly, though finalizers should be unique. Finalizer naming depends on `ObjectKind().GroupVersionKind().Kind`; missing TypeMeta can produce an empty-kind finalizer. Add does not refresh before update, so concurrent finalizer edits can conflict. Generation-change semantics differ between fake clients and API server behavior.

## Test Signals
`finalizer_test.go` covers add, remove by derived name, and remove by explicit name against a fake client. It does not cover missing TypeMeta, conflicts, duplicate finalizers, or metadata accessor failures.
