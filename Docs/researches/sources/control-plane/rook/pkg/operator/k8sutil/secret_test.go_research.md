# sources/control-plane/rook/pkg/operator/k8sutil/secret_test.go

## Purpose
This file validates owner-reference comparison and ownership-safe secret delete/update behavior.

## Important APIs, Types, and Functions
`TestIsSameOwnerReference()` checks matching and mismatched refs. `TestDeleteSecretIfOwnedBy()` uses fake-client reactors to simulate get/delete outcomes. `TestUpdateSecretIfOwnedBy()` creates fake secrets and validates update success and rejection cases.

## Control Flow, State, and Persistence
Tests run against `k8s.io/client-go/kubernetes/fake`. Delete tests intercept get and delete actions. Update tests persist fake secrets, mutate local objects, and re-read from the fake store.

## Dependencies and Integration Points
It uses Kubernetes metadata/errors/runtime/schema test APIs, fake clientsets, `ptr.To(true)` for controller refs, and testify.

## Risks
The "owned by caller, deletion succeeds" table entry uses a secret owner name that does not match the `owner` variable, so it may not actually assert a delete unless reactors mask the mismatch. Tests do not inspect fake actions to prove delete was called in all expected cases.

## Test Signals
Important signals are not-found delete idempotence, unowned secret preservation, different-owner preservation, delete error propagation, and update rejection for unowned or differently owned secrets.
