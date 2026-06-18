# sources/control-plane/rook/pkg/operator/ceph/controller/predicate_test.go

## Purpose
`predicate_test.go` validates key helper logic used by controller-runtime event predicates.

## Important APIs, Types, and Functions
`TestObjectChanged` checks patch-based object change detection. `TestIsValidEvent` verifies patch trimming and invalid JSON handling. Tests cover `isCanary`, `shouldReconcileCM`, `isCMToIgnoreOnDelete`, `isSecretToIgnoreOnUpdate`, `IsDoNotReconcile`, and `DuplicateCephClusters`.

## Control Flow, State, and Persistence
Most tests operate on in-memory objects. `TestDuplicateCephClusters` uses a controller-runtime fake client with CephCluster objects across same and different namespaces. No real watch events are created.

## Dependencies and Integration Points
The tests depend on Ceph CR types, Kubernetes ConfigMaps/Secrets/Deployments, controller-runtime fake clients, scheme registration, and package-level test constants shared with other tests.

## Risks
The suite tests helper functions more than the composed typed predicates, so event-specific behavior can regress without detection. `TestIsValidEvent` expects a patch containing `spec` to reconcile after metadata/status trimming, but does not cover metadata-only patches. Secret redaction and keyring annotation suppression are not directly tested.

## Test Signals
Signals are good for individual whitelist/blacklist decisions and duplicate cluster blocking. Missing signals include create/delete/update predicate end-to-end behavior, peer-token Secret predicates, and object matcher error handling.
