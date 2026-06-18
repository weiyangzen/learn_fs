# sources/control-plane/rook/pkg/operator/ceph/controller/object_operations.go

## Purpose
`object_operations.go` provides a small generic create-or-update helper for controller-runtime objects.

## Important APIs, Types, and Functions
`CreateOrUpdateObject()` obtains object metadata with `meta.Accessor()`, attempts `client.Create()`, and on `AlreadyExists` attempts `client.Update()`. It logs created or updated object type/name using reflection and `NsName()`.

## Control Flow, State, and Persistence
State is persisted through controller-runtime client create/update calls. The function does not fetch the existing object before update; it updates the object passed by the caller when creation reports already exists.

## Dependencies and Integration Points
It depends on Kubernetes API error classification, controller-runtime clients, metadata accessors, reflection, and Rook logging. It is a convenience helper for Ceph controller object reconciliation.

## Risks
Updating a caller-provided object after `AlreadyExists` may fail if it lacks the current `resourceVersion`, especially with real API servers. There is no patch/merge behavior and no conflict retry. Status subresources are not handled separately. Reflection output may be noisy but is only for logs.

## Test Signals
No direct tests are included in this subset. Useful tests would cover create success, already-exists update with a fake client, accessor failure, update conflict, and real-client-like resourceVersion requirements.
