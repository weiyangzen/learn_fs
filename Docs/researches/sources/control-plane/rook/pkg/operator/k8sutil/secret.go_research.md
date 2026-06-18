# sources/control-plane/rook/pkg/operator/k8sutil/secret.go

## Purpose
`secret.go` contains create/update and ownership-gated delete/update helpers for Kubernetes Secrets.

## Important APIs, Types, and Functions
`CreateOrUpdateSecret()` creates a secret and updates it on `AlreadyExists`. `DeleteSecretIfOwnedBy()` deletes only when the existing secret's controller owner matches the provided owner. `UpdateSecretIfOwnedBy()` fetches the latest secret, verifies both existing and desired controller ownership, copies data/stringData/labels/annotations, and updates. `IsSameOwnerReference()` compares owner references by API group, kind, and name.

## Control Flow, State, and Persistence
The functions persist Kubernetes Secret changes through `clientset.CoreV1().Secrets(namespace)`. Delete ignores not-found and skips unowned or differently owned secrets. Update returns errors for missing existing secret, missing owner references, conflicting owners, and update failures.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 secrets, API error helpers, schema parsing, and client-go. It protects user-created secrets from accidental operator deletion or mutation.

## Risks
Owner matching ignores UID, so a recreated owner with the same group/kind/name is treated as the same. `UpdateSecretIfOwnedBy()` has a typo in one error message ("founf"). `CreateOrUpdateSecret()` updates the whole provided secret, so callers must preserve fields they intend to keep.

## Test Signals
`secret_test.go` covers owner comparison, deletion for not found/get error/unowned/different owner/matching owner/delete error, and update success/no owner/different owner/not found.
