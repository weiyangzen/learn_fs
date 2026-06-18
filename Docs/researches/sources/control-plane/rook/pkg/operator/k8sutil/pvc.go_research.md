# sources/control-plane/rook/pkg/operator/k8sutil/pvc.go

## Purpose
`pvc.go` conditionally expands persistent volume claims when the desired storage request is larger than the current request and the storage class permits expansion.

## Important APIs, Types, and Functions
`ExpandPVCIfRequired(ctx, client, desiredPVC, currentPVC) bool` compares `ResourceStorage` requests, validates `StorageClassName`, fetches the `StorageClass`, checks `AllowVolumeExpansion`, updates `currentPVC.Spec.Resources.Requests`, and calls `client.Update()`.

## Control Flow, State, and Persistence
The function mutates the in-memory `currentPVC` and persists it through the controller-runtime client only for expansions. Missing requests, missing storage class, storage class lookup failures, disabled expansion, update failures, equal sizes, and shrink attempts all return false after logging.

## Dependencies and Integration Points
It uses Kubernetes core PVC types, storage class types, controller-runtime client, and namespaced object keys. It is intended for reconcile loops where PVC expansion should not fail the whole reconcile on update errors.

## Risks
Errors are logged but not returned, so callers only get a boolean. Shrink requests are ignored. The `pvcBacked` style of device logic is not relevant here; expansion depends entirely on storage class policy and API update success.

## Test Signals
`pvc_test.go` covers equal, larger, smaller, allowed, and disallowed expansion cases using a fake controller-runtime client. Missing storage class name, storage class get failures, and update failures are not directly covered.
