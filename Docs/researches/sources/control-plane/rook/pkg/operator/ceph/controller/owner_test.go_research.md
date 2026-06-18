# sources/control-plane/rook/pkg/operator/ceph/controller/owner_test.go

## Purpose
`owner_test.go` verifies `OwnerMatcher.Match()` behavior for child objects with controller owner references.

## Important APIs, Types, and Functions
`TestMatch` creates a `CephObjectStore` owner with a UID and a Secret child with a controller owner reference. It initializes a matcher through `NewOwnerReferenceMatcher()` and mutates the child owner reference through wrong kind, right kind/wrong UID, and right kind/right UID cases.

## Control Flow, State, and Persistence
The test operates entirely in memory and does not use a Kubernetes client. Scheme registration is used only for owner group/kind detection.

## Dependencies and Integration Points
It depends on Ceph API scheme registration, Kubernetes core Secret metadata, owner reference semantics, and reflect-derived Kind setup.

## Risks
The test does not cover namespace differences because owner references do not encode namespace. It does not validate non-controller owner references or multiple owners. The owner TypeMeta and scheme setup are enough for this case but may not reveal failures for unregistered types.

## Test Signals
The test gives clear signal for the primary UID/kind gate. Missing signals include empty owner UID behavior, bad API versions, absent controller refs, and scheme object-kind errors.
